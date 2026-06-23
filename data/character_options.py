# Opções do construtor de personagem (avatar composto em SVG).
# Categorias: cabelo (estilo), pele (cor), cor_cabelo (cor), acessorio e
# fundo (cor). A cabeça é sempre redonda (formato único). Veja avatar.py /
# static/js/avatar.js.

CHAR_OPTIONS = {
    "cabelo": [  # estilo de cabelo
        {"id": "liso_curto", "label": "Liso curto"},
        {"id": "liso_longo", "label": "Liso longo"},
        {"id": "cacheado",   "label": "Cacheado"},
        {"id": "careca",     "label": "Careca"},
        {"id": "coque",      "label": "Coque"},
        {"id": "moicano",    "label": "Moicano"},
    ],
    "pele": [    # tom de pele (8)
        {"id": "pele_1", "label": "Tom 1", "color": "#FFE0BD"},
        {"id": "pele_2", "label": "Tom 2", "color": "#F1C27D"},
        {"id": "pele_3", "label": "Tom 3", "color": "#E0AC69"},
        {"id": "pele_4", "label": "Tom 4", "color": "#C68642"},
        {"id": "pele_5", "label": "Tom 5", "color": "#A56A3A"},
        {"id": "pele_6", "label": "Tom 6", "color": "#8D5524"},
        {"id": "pele_7", "label": "Tom 7", "color": "#5C3A1E"},
        {"id": "pele_8", "label": "Tom 8", "color": "#FFB6C1"},
    ],
    "cor_cabelo": [  # cor do cabelo (8)
        {"id": "cab_1", "label": "Preto",    "color": "#1A1A1A"},
        {"id": "cab_2", "label": "Castanho", "color": "#5B3A1E"},
        {"id": "cab_3", "label": "Loiro",    "color": "#E6BE63"},
        {"id": "cab_4", "label": "Ruivo",    "color": "#B5532A"},
        {"id": "cab_5", "label": "Grisalho", "color": "#B8B8C0"},
        {"id": "cab_6", "label": "Azul",     "color": "#3498DB"},
        {"id": "cab_7", "label": "Rosa",     "color": "#E84393"},
        {"id": "cab_8", "label": "Verde",    "color": "#27AE60"},
    ],
    "acessorio": [
        {"id": "nenhum",    "label": "Nenhum"},
        {"id": "oculos",    "label": "Óculos"},
        {"id": "bone",      "label": "Boné"},
        {"id": "chapeu",    "label": "Chapéu"},
        {"id": "brinco",    "label": "Brinco"},
        {"id": "headphone", "label": "Headphone"},
    ],
    "fundo": [   # cor de fundo do avatar
        {"id": "fundo_roxo",    "label": "Roxo",    "color": "#6C3483"},
        {"id": "fundo_azul",    "label": "Azul",    "color": "#1A5276"},
        {"id": "fundo_verde",   "label": "Verde",   "color": "#1E8449"},
        {"id": "fundo_laranja", "label": "Laranja", "color": "#B9770E"},
        {"id": "fundo_rosa",    "label": "Rosa",    "color": "#922B75"},
        {"id": "fundo_grafite", "label": "Grafite", "color": "#34344A"},
    ],
}

CHAR_DEFAULTS = {
    "cabelo":     "liso_curto",
    "pele":       "pele_2",
    "cor_cabelo": "cab_1",
    "acessorio":  "nenhum",
    "fundo":      "fundo_roxo",
}


def get_option(category: str, option_id: str) -> dict:
    for opt in CHAR_OPTIONS[category]:
        if opt["id"] == option_id:
            return opt
    return CHAR_OPTIONS[category][0]
