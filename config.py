import os

# Carrega variáveis de ambiente do .env (se python-dotenv estiver instalado).
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

PORT = 5000
MIN_PLAYERS = 2
MAX_PLAYERS = 10
SECRET_KEY = "movie-night-secret-2024"
SHOW_AUTO_ADVANCE_SECONDS = 60
ROUND1_PICKS = 5
ROUND2_PICKS = 3
ROUND3_PICKS = 3

# Chave da API do TMDB para buscar posters reais (ver posters.py e .env.example).
# Defina em .env:  TMDB_API_KEY=sua_chave_aqui
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")
