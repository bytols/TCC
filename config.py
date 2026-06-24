import os

# Carrega variáveis de ambiente do .env (se python-dotenv estiver instalado).
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PORT = 5001
MIN_PLAYERS = 2
MAX_PLAYERS = 4
SECRET_KEY = "movie-night-secret-2024"
SHOW_AUTO_ADVANCE_SECONDS = 60
ROUND1_PICKS = 5
ROUND2_PICKS = 3
ROUND3_PICKS = 3
AUTO_START_SECONDS = int(os.environ.get("AUTO_START_SECONDS", "30"))

# Detecção de saída involuntária (wifi caiu / fechou navegador): o celular envia
# um "heartbeat" a cada HEARTBEAT_PING_SECONDS; o servidor varre a cada
# HEARTBEAT_SWEEP_SECONDS e remove quem não dá sinal há HEARTBEAT_TIMEOUT_SECONDS.
# O timeout é folgado de propósito: durante as fases em que o jogador olha para a
# TV, o navegador móvel pode suspender os timers (tela bloqueada) e atrasar pings.
# Um timeout curto removeria jogadores ativos por engano — e, com 2 jogadores,
# isso derrubaria a partida inteira (reset abaixo de MIN_PLAYERS).
HEARTBEAT_PING_SECONDS = 3
HEARTBEAT_SWEEP_SECONDS = 3
HEARTBEAT_TIMEOUT_SECONDS = 30

# Chave da API do TMDB para buscar posters reais (ver posters.py e .env.example).
# Defina em .env:  TMDB_API_KEY=sua_chave_aqui
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")

# Portas seriais dos Arduinos que controlam os totens LED.
# Exemplo macOS: /dev/cu.usbmodem1401
ARDUINO_A_PORT = os.environ.get("ARDUINO_A_PORT", "")
ARDUINO_B_PORT = os.environ.get("ARDUINO_B_PORT", "")
ARDUINO_BAUD = int(os.environ.get("ARDUINO_BAUD", "9600"))
