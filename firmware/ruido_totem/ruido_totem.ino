// RUÍDO — Firmware do totem LED (Arduino A e B usam ESTE MESMO sketch).
//
// O servidor Flask (arduino.py) faz o roteamento de player_id -> Arduino + slot.
// Cada Arduino só conhece dois slots locais: S1 e S2 (um pino/fita cada).
//
// Protocolo serial (9600 baud, deve bater com ARDUINO_BAUD do .env):
//   Mensagens ASCII terminadas em '\n' no formato  S{slot}:{COR}
//   slot ∈ {1, 2}
//   COR  ∈ {WHITE, BLUE, PINK, ORANGE, GREEN, OFF}
//   Exemplo: "S1:BLUE\n"
//
// Comportamento (incorporando os efeitos do sketch original):
//   - Boot: cada fita acende LED por LED em azul fraco e ganha força (auto-teste).
//   - Ao receber uma cor: TRANSIÇÃO suave (fadeToColor) da cor atual para a nova.
//   - Estados de rodada (BLUE/PINK/ORANGE): a fita RESPIRA (pulso) na cor,
//     comunicando urgência — porém de forma NÃO-BLOQUEANTE, então a serial
//     continua sendo lida o tempo todo (inclusive comandos para o outro slot).
//   - WHITE (entrou/votou), GREEN (consenso) e OFF (slot vazio): cor sólida estável.
//
// Requer a biblioteca "Adafruit NeoPixel" (Gerenciador de Bibliotecas da IDE).

#include <Adafruit_NeoPixel.h>

// ---- Ajuste estes valores ao seu hardware ----
#define SLOT1_PIN   6     // pino de dados da fita do slot S1
#define SLOT2_PIN   7     // pino de dados da fita do slot S2
#define NUMPIXELS   9     // nº de LEDs em cada fita
// ----------------------------------------------

Adafruit_NeoPixel strips[2] = {
  Adafruit_NeoPixel(NUMPIXELS, SLOT1_PIN, NEO_GRB + NEO_KHZ800),
  Adafruit_NeoPixel(NUMPIXELS, SLOT2_PIN, NEO_GRB + NEO_KHZ800)
};

// Cor atual e modo de cada slot (índice 0 = S1, 1 = S2).
int  curR[2]   = {0, 0};
int  curG[2]   = {0, 0};
int  curB[2]   = {0, 0};
bool pulsing[2] = {false, false};

// Preenche toda a fita de um slot com uma cor sólida.
void setAll(int idx, int r, int g, int b) {
  for (int i = 0; i < NUMPIXELS; i++) {
    strips[idx].setPixelColor(i, strips[idx].Color(r, g, b));
  }
  strips[idx].show();
}

// Transição suave entre duas cores numa fita (bloqueante e curta).
void fadeToColor(int idx,
                 int r1, int g1, int b1,
                 int r2, int g2, int b2,
                 int steps, int waitTime) {
  for (int s = 0; s <= steps; s++) {
    int r = r1 + ((r2 - r1) * s) / steps;
    int g = g1 + ((g2 - g1) * s) / steps;
    int b = b1 + ((b2 - b1) * s) / steps;
    setAll(idx, r, g, b);
    delay(waitTime);
  }
}

// Mapeia o nome da cor (linguagem visual do design system) para RGB + modo pulso.
bool nameToRGB(const String &name, int &r, int &g, int &b, bool &pulse) {
  if      (name == "WHITE")  { r = 180; g = 190; b = 220; pulse = false; return true; }  // branco frio calibrado — menos variação entre lotes
  else if (name == "BLUE")   { r = 0;   g = 102; b = 255; pulse = true;  return true; }  // glow-blue
  else if (name == "PINK")   { r = 182; g = 0;   b = 111; pulse = true;  return true; }  // #B6006F
  else if (name == "ORANGE") { r = 255; g = 51;  b = 0;   pulse = true;  return true; }  // glow-orange
  else if (name == "GREEN")  { r = 0;   g = 255; b = 80;  pulse = true;  return true; }  // consenso (respira)
  else if (name == "OFF")    { r = 0;   g = 0;   b = 0;   pulse = false; return true; }  // slot vazio
  return false;
}

// Aplica uma nova cor a um slot, com transição a partir da cor atual.
void setColor(int idx, const String &name) {
  int r, g, b;
  bool pulse;
  if (!nameToRGB(name, r, g, b, pulse)) return;

  fadeToColor(idx, curR[idx], curG[idx], curB[idx], r, g, b, 60, 8);
  curR[idx] = r;
  curG[idx] = g;
  curB[idx] = b;
  pulsing[idx] = pulse;  // se sólida, fica como a fade deixou; se pulsante, o loop respira
}

// Auto-teste no power-on: acende LED por LED em azul fraco, ganha força e apaga.
void bootGreeting() {
  for (int idx = 0; idx < 2; idx++) {
    for (int i = 0; i < NUMPIXELS; i++) {
      strips[idx].setPixelColor(i, strips[idx].Color(0, 0, 30));
      strips[idx].show();
      delay(120);
    }
  }
  for (int idx = 0; idx < 2; idx++) fadeToColor(idx, 0, 0, 30, 0, 102, 255, 80, 8);
  delay(300);
  // Estado inicial: apagado, aguardando comandos do servidor.
  for (int idx = 0; idx < 2; idx++) fadeToColor(idx, 0, 102, 255, 0, 0, 0, 60, 6);
}

void setup() {
  Serial.begin(9600);
  for (int idx = 0; idx < 2; idx++) {
    strips[idx].begin();
    strips[idx].clear();
    strips[idx].show();
  }
  bootGreeting();
}

void loop() {
  // 1) Lê comando serial, se houver (responsivo mesmo enquanto o outro slot respira).
  if (Serial.available() > 0) {
    String msg = Serial.readStringUntil('\n');  // ex.: "S1:BLUE"
    msg.trim();

    int sep = msg.indexOf(':');
    if (msg.length() >= 4 && msg.charAt(0) == 'S' && sep > 0) {
      char slot = msg.charAt(1);
      String color = msg.substring(sep + 1);
      color.toUpperCase();
      if      (slot == '1') setColor(0, color);
      else if (slot == '2') setColor(1, color);
    }
  }

  // 2) Respiração não-bloqueante: brilho 40..255 em onda triangular (~2,4s por ciclo).
  static unsigned long lastBreath = 0;
  if (millis() - lastBreath >= 20) {
    lastBreath = millis();
    float phase = (millis() % 2400) / 2400.0;          // 0..1
    float tri = phase < 0.5 ? phase * 2 : 2 - phase * 2; // 0..1..0
    int brilho = 40 + (int)(tri * (255 - 40));
    for (int idx = 0; idx < 2; idx++) {
      if (pulsing[idx]) {
        setAll(idx,
               curR[idx] * brilho / 255,
               curG[idx] * brilho / 255,
               curB[idx] * brilho / 255);
      }
    }
  }
}
