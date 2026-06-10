# CLAUDE.md — RUÍDO (TCC Mary)

## Visão Geral

**RUÍDO** é uma aplicação web de experiência coletiva para sessões de "noite de filme" em grupo. Os participantes entram pelo celular, criam uma identidade (nome + avatar), escolhem filmes preferidos em 3 rodadas de votação crescentemente afuniladas e, ao final, veem qual percentual de gostos o grupo tem em comum ("match"). A tela de TV/desktop exibe o lobby com QR code, o progresso coletivo em tempo real e os resultados.

O conceito central: transformar o **ruído** de gostos divergentes em um **consenso** coletivo. A interface reflege essa jornada mudando de cor a cada rodada (azul → rosa → laranja → consenso).

> **Marca:** o projeto foi rebatizado de "Projeto TV" para **RUÍDO** (design V3 do Figma). O wordmark é a imagem `static/img/logo.png`.

**Stack:** Python 3.13 · Flask 3 · Flask-SocketIO · Flask-SQLAlchemy · SQLite in-memory · eventlet · Pillow · qrcode

---

## Estrutura de Arquivos

```
tcc_mary/
├── run.py                  # Ponto de entrada; inicia o servidor via eventlet
├── app.py                  # Factory Flask: blueprints, DB, SocketIO, TEMPLATES_AUTO_RELOAD
├── config.py               # Constantes globais (portas, limites, segredos)
├── extensions.py           # Instâncias compartilhadas de db e socketio
├── models.py               # Modelos SQLAlchemy (Session, Player, Vote, RoundPool)
├── session_state.py        # Máquina de estados + progresso + emissão de eventos WS
├── match.py                # Algoritmo de cálculo de match entre votos
├── avatar.py               # Geração de avatar PNG via Pillow
├── qr.py                   # Geração de QR code PNG com URL de entrada
│
├── routes/
│   ├── desktop.py          # Blueprint "desktop" — tela do host/TV + APIs
│   ├── join.py             # Blueprint "join" — splash + criação de identidade
│   └── game.py             # Blueprint "game" — rounds e resultados (mobile)
│
├── sockets/
│   └── events.py           # Handlers SocketIO (connect, join_room, state)
│
├── data/
│   ├── movies.py           # Catálogo de filmes por categoria + MOVIE_LOOKUP
│   └── character_options.py # Opções e defaults do construtor de avatar
│
├── templates/
│   ├── base_mobile.html    # Layout base mobile (glow-layer, CSS, socket.io CDN)
│   ├── base_desktop.html   # Layout base desktop (desktop.js)
│   ├── mobile/             # join, waiting, round1-3, results, session_*
│   └── desktop/
│       └── lobby.html      # Tela única do host (renderiza todos os estados)
│
└── static/
    ├── img/
    │   ├── logo.png        # Wordmark "RUÍDO" (asset oficial do Figma)
    │   └── avatars/        # PNGs de avatar gerados por jogador
    ├── css/main.css        # Design system V3 (glassmorphism + estados de cor)
    ├── js/desktop.js       # Controlador da TV (socket + polling, progresso, admin)
    └── js/round1.js        # Carrossel de filmes, chips de gênero e modal de detalhes
```

---

## Configuração (`config.py` + `app.py`)

| Constante | Valor | Descrição |
|---|---|---|
| `PORT` | 5000 | Porta HTTP do servidor |
| `MIN_PLAYERS` | 2 | Mínimo para iniciar a sessão |
| `MAX_PLAYERS` | 10 | Limite de participantes |
| `SECRET_KEY` | string | Chave Flask para sessões |
| `ROUND1_PICKS` | 5 | Filmes a escolher na rodada 1 |
| `ROUND2_PICKS` | 3 | Filmes a escolher na rodada 2 |
| `ROUND3_PICKS` | 3 | Filmes a escolher na rodada final |

O banco de dados é **SQLite in-memory** — todos os dados são perdidos ao reiniciar o servidor. Cada partida é uma sessão efêmera.

> **`TEMPLATES_AUTO_RELOAD = True`** está habilitado em `app.py`. Sem isso, o Flask em modo não-debug cacheia os templates Jinja na primeira renderização e mudanças em `.html` só aparecem após reiniciar o servidor. (Arquivos estáticos em `static/` são sempre lidos do disco a cada request.)

---

## Modelos de Dados (`models.py`)

### `Session`
Uma única sessão de jogo por instância do servidor. Campos: `id`, `state` (máquina de estados), `started_at`.

### `Player`
Cada participante. Campos: `id`, `name`, `character_json` (JSON com as escolhas de avatar), `avatar_path` (caminho para o PNG gerado), `session_id`.

### `Vote`
Registro de voto de um player em uma rodada. Campos: `player_id`, `round_number` (1, 2 ou 3), `movie_id`, `movie_title`, `category`. Constraint única: um player não pode votar duas vezes no mesmo filme na mesma rodada.

### `RoundPool`
Pool de filmes disponíveis nas rodadas 2 e 3 (filmes que receberam votos na rodada anterior). Campos: `round_number`, `movie_id`, `movie_title`, `category`.

---

## Máquina de Estados (`session_state.py`)

O jogo avança por estados lineares:

```
LOBBY → ROUND_1 → SHOW_1 → ROUND_2 → SHOW_2 → ROUND_3 → FINAL
```

| Estado | Cor da UI | Descrição |
|---|---|---|
| `LOBBY` | quente (vermelho/magenta) | Aguardando jogadores entrarem via QR code |
| `ROUND_1` | 🔵 azul | Jogadores escolhem 5 filmes do catálogo (exploração) |
| `SHOW_1` | 🔵 azul | Desktop exibe resultado/match da rodada 1 |
| `ROUND_2` | 🩷 rosa | Jogadores escolhem 3 filmes do pool (aproximação) |
| `SHOW_2` | 🩷 rosa | Desktop exibe resultado/match da rodada 2 |
| `ROUND_3` | 🟧 laranja | Escolha final, 3 filmes (negociação) |
| `FINAL` | consenso | Desktop exibe resultado final coletivo |

**Comportamento das cores:** cada rodada tem uma cor que representa o estágio da decisão coletiva (azul = exploração → rosa = aproximação → laranja = negociação → consenso). Implementado via classes `glow-blue` / `glow-pink` / `glow-orange` / `glow-final` no CSS.

**Transições automáticas:** quando todos os jogadores de uma rodada submetem (`check_round_complete`), o estado avança via `advance_state()`. O host também avança manualmente nos estados SHOW.

**Ao avançar para SHOW/FINAL:** `build_round_pool` monta a lista de filmes da próxima rodada (união dos votos da rodada atual, deduplicada por `movie_id`).

**Funções de progresso (real-time):**
- `count_submitted(round_number)` — quantos jogadores já submeteram naquela rodada.
- `submitted_player_ids(round_number)` — IDs dos jogadores que já concluíram.
- `notify_progress(round_number)` — emite o evento `progress` para a TV atualizar sem mudança de estado.

**Emissão WebSocket:** toda mudança de estado emite `state_change` para o room `game_room`, fazendo todos os clientes redirecionarem.

---

## Catálogo de Filmes (`data/movies.py`)

Dicionário aninhado:
```python
MOVIES = {
    "acao": { "label": "AÇÃO", "color": "#E74C3C", "movies": [{"id","title","year"}, ...] },
    ...
}
```

`MOVIE_LOOKUP` é um dicionário plano para busca rápida, enriquecido com metadados:
```python
id → { id, title, year, category, category_label, category_color }
```

Categorias: Ação, Animação, Comédia, Documentário, Drama, Fantasia, Ficção, Heróis, Romance, Sitcom, Suspense, Terror.

> **Nota:** os dados de origem têm `title`, `year` e `category`. O **rating** (★) e a **sinopse** exibidos no modal de detalhes (round 1) são **gerados de forma determinística** em `round1.js` a partir de um hash do `id` do filme — não existem nos dados. Para dados reais, integrar uma fonte externa (ex.: TMDB).

---

## Construtor de Avatar (`avatar.py` + `data/character_options.py`)

Avatar gerado como PNG 200×200px via Pillow, em camadas:

1. **Fundo** — círculo colorido (roxo, azul, verde, laranja, rosa)
2. **Corpo/Roupa** — elipse inferior (5 cores)
3. **Rosto** — círculo central (5 tons de pele)
4. **Cabelo** — arco + retângulo (5 cores)
5. **Olhos / Boca** — fixos
6. **Acessório** — condicional: óculos, chapéu, boné, coroa/tiara

Salvo em `static/img/avatars/{player_id}.png`. No formulário de join há também um **preview ao vivo em CSS** (divs `.av-*`) que reflete as escolhas antes de submeter.

---

## Rotas

### Blueprint `desktop` (`/desktop`, `/qr.png`, `/admin/*`, `/api/*`)

| Rota | Método | Descrição |
|---|---|---|
| `/desktop` | GET | Renderiza o estado atual do jogo na TV (lobby / loading / resultados) |
| `/qr.png` | GET | QR code PNG da URL de join |
| `/admin/start` | POST | Inicia o jogo (LOBBY → ROUND_1); requer ≥2 jogadores |
| `/admin/advance` | POST | Avança o estado manualmente |
| `/admin/end` | POST | Encerra e limpa toda a sessão |
| `/api/lobby_state` | GET | JSON: `state`, `player_count`, `players` e, em rodada, `progress` (`submitted`, `total`, `submitted_ids`) — usado pelo polling de fallback |

### Blueprint `join` (`/join`)

| Rota | Método | Descrição |
|---|---|---|
| `/` | GET | Redireciona para `/join` |
| `/join` | GET | Splash carousel (3 frases) → formulário de identidade (nome + avatar) |
| `/join` | POST | Cria o player, gera avatar, emite `player_joined`, seta cookie `player_id` |

Guarda o player via cookie `player_id` (httponly). Redireciona para `/waiting` após entrada.

### Blueprint `game` (`/waiting`, `/round/*`, `/results`)

| Rota | Método | Descrição |
|---|---|---|
| `/waiting` | GET | Tela de espera; redireciona conforme o estado |
| `/round/1` | GET | Seleção da rodada 1 (chips de gênero → carrossel) |
| `/round/1/submit` | POST | Submete 5 votos; chama `notify_progress(1)` se a rodada não fechou |
| `/round/2` | GET | Rodada 2 (lista do pool afunilado) |
| `/round/2/submit` | POST | Submete 3 votos; `notify_progress(2)` |
| `/round/3` | GET | Escolha final |
| `/round/3/submit` | POST | Submete 3 votos finais; `notify_progress(3)` |
| `/results` | GET | Resultado/match do round atual (SHOW_1, SHOW_2, FINAL) |

Todas as rotas de game usam `@require_player` (redireciona para `/join` sem cookie).

---

## Algoritmo de Match (`match.py`)

Agrupa votos por `movie_id` e conta quantos players votaram em cada filme:
- **Match:** filme escolhido por ≥ 2 players
- **`match_pct`:** `(filmes_com_match / total_único) * 100`
- Retorna lista ordenada por contagem decrescente, com flag `is_match` e os players de cada filme.

---

## WebSocket (SocketIO)

Room único: `game_room`.

| Cliente → servidor | Descrição |
|---|---|
| `join_room` | Jogador mobile entra no room e recebe o estado atual |
| `desktop_connect` | Host (TV) entra no room e recebe o estado atual |
| `request_state` | Solicita o estado atual |

| Servidor → cliente | Payload | Descrição |
|---|---|---|
| `state_change` | `{state, player_count, players}` | Mudança de estado — clientes redirecionam |
| `player_joined` | `{name, avatar_path, player_count, players}` | Novo jogador entrou |
| `progress` | `{round, submitted, total, submitted_ids}` | Progresso coletivo da rodada (TV atualiza sem reload) |
| `session_ended` | `{}` | Sessão encerrada — todos voltam para `/join` |

**Atualização em tempo real na TV (`desktop.js`):** um único socket trata `player_joined` (adiciona ao grid/chips), `progress` (atualiza "X de Y concluíram" e marca avatares concluídos) e `state_change` (recarrega). Há **polling de fallback** em `/api/lobby_state` a cada 2,5s, caso o WebSocket caia.

---

## Componentes de UI (V3)

### Splash carousel (`mobile/join.html`)
3 frases de apresentação que passam automaticamente a cada 2,4s (ou ao toque), com dots de navegação. Cada frase usa quebra manual `<br>` para ocupar **exatamente 2 linhas centradas** (sem palavras viúvas). Botão "INICIAR" revela o formulário.

### Formulário de identidade
Nome + construtor de avatar. O botão **"ENTRAR" fica desabilitado até o nome ter ≥ 3 caracteres** (transição suave). Preview de avatar ao vivo em CSS.

### Chips de gênero (round 1, fase 1 — `round1.js`)
Chips com efeito glass e um dot colorido por categoria. Estado selecionado: borda branca + glow. Habilita "VER FILMES".

### Carrossel de filmes (round 1, fase 2 — `round1.js`)
Carrossel horizontal com **posters inclinados**. O filme central fica em foco (`scale: 1`, sem rotação, `box-shadow` branco); os laterais ficam reduzidos (`scale: .85`, `opacity: .7`) e inclinados, parcialmente visíveis para incentivar a navegação. Abaixo: título, ano, gênero e ★rating do filme central, botão **"+ Adicionar à minha lista" / "✓ Adicionado"**, contador e botão **"Próximo"** travado até a quantidade exata de filmes.

### Modal de detalhes (round 1 — `round1.js`)
Ao tocar num poster, abre em tela cheia: o poster vira o **background desfocado** (`backdrop-filter: blur(30px)` + overlay escuro). Exibe poster, nome, ano, gênero, ★avaliação e sinopse, com ação de adicionar/remover da lista.

### Telas de loading da TV (`desktop/lobby.html`)
Durante cada rodada, a TV mostra: fundo na **cor da rodada** (azul/rosa/laranja), ícone de telefone em destaque, "AGUARDANDO PARTICIPANTES...", subtítulo contextual, **progresso "X de Y concluíram"**, chips de avatar (com glow nos que já votaram), o **QR code sempre disponível** (para quem entrar no meio) e o logo RUÍDO.

---

## Design System (`static/css/main.css`)

**Tema:** dark, base `#06051A`, tipografia uppercase com alto letter-spacing, fonte **Inter** (pesos 300–900).

**Glassmorphism** (aplicado a botões, cards, chips, inputs, modal, construtor de avatar):
```css
background: rgba(255,255,255,0.10);
backdrop-filter: blur(10px);
border: 1px solid rgba(255,255,255,0.20);
```
Tokens: `--glass-bg`, `--glass-bg-soft`, `--glass-border`, `--glass-blur`.

**Sistema de glow / estados de cor:** elementos `.glow-layer` (mobile) e `.desktop-glow` (TV) renderizam blobs desfocados usando as variáveis `--glow-1` / `--glow-2`. As classes `glow-blue`, `glow-pink`, `glow-orange`, `glow-final` sobrescrevem essas variáveis por rodada.

**Paleta de acento:** `--red` #FF3300 · `--magenta` #B6006F · `--blue` #0004FF · `--match-color` #FF3300.

**Layout:** mobile-first, container máx 430px. Desktop usa CSS Grid de 3 colunas (lobby) ou flex full-height (loading/resultados).

---

## QR Code (`qr.py`)

Detecta WSL2 e usa `ipconfig.exe` para obter o IP real da rede Windows (para QR codes escaneáveis por celulares na mesma rede Wi-Fi). Fora do WSL, usa socket UDP. O PNG é cacheado em memória.

---

## Fluxo Completo de uma Partida

1. **Host** abre `/desktop` na TV — vê o lobby RUÍDO com QR code
2. **Jogadores** escaneiam o QR → splash carousel → criam identidade (nome ≥3 + avatar) → `/waiting`
3. Desktop atualiza o grid de jogadores em tempo real (WebSocket + polling)
4. **Host** clica INICIAR (≥2 jogadores) → `ROUND_1` (UI fica azul)
5. Celulares vão para `/round/1`: selecionam gêneros → carrossel → escolhem 5 filmes (com modal de detalhes) → submetem
6. A TV mostra o progresso "X de Y concluíram" em tempo real; quando o último submete → `SHOW_1`
7. Desktop exibe match% e filmes; host clica PRÓXIMA RODADA
8. `ROUND_2` (rosa, pool afunilado, 3 escolhas) → `SHOW_2`
9. `ROUND_3` (laranja, escolha final) → `FINAL`
10. `FINAL`: "RESULTADO COLETIVO" — o grupo chegou a um consenso; host clica ENCERRAR

---

## Como Executar

```bash
# Criar/ativar venv (Python 3.13) e instalar dependências
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Iniciar servidor (ponto de entrada é run.py, NÃO app.py)
python run.py

# Desktop (host/TV): http://localhost:5000/desktop
# Mobile (jogadores): http://<IP_LOCAL>:5000/join  (ou escanear o QR)
```

O QR code na tela desktop já aponta para o IP correto da rede local.
