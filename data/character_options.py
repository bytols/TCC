CHAR_OPTIONS = {
    "rosto": [
        {"id": "rosto_1", "label": "Claro",   "color": "#FDBCB4"},
        {"id": "rosto_2", "label": "Médio",   "color": "#D4956A"},
        {"id": "rosto_3", "label": "Escuro",  "color": "#8D5524"},
        {"id": "rosto_4", "label": "Rosa",    "color": "#FFB6C1"},
        {"id": "rosto_5", "label": "Moreno",  "color": "#C68642"},
    ],
    "cabelo": [
        {"id": "cabelo_1", "label": "Preto",     "color": "#1A1A1A"},
        {"id": "cabelo_2", "label": "Loiro",     "color": "#F4D03F"},
        {"id": "cabelo_3", "label": "Castanho",  "color": "#8B4513"},
        {"id": "cabelo_4", "label": "Ruivo",     "color": "#CC5500"},
        {"id": "cabelo_5", "label": "Azul",      "color": "#3498DB"},
    ],
    "roupa": [
        {"id": "roupa_1", "label": "Azul",      "color": "#2980B9"},
        {"id": "roupa_2", "label": "Vermelho",  "color": "#C0392B"},
        {"id": "roupa_3", "label": "Verde",     "color": "#27AE60"},
        {"id": "roupa_4", "label": "Roxo",      "color": "#8E44AD"},
        {"id": "roupa_5", "label": "Laranja",   "color": "#D35400"},
    ],
    "acessorio": [
        {"id": "acc_none",    "label": "Nenhum",  "has_item": False},
        {"id": "acc_oculos",  "label": "Óculos",  "has_item": True,  "draw": "glasses"},
        {"id": "acc_chapeu",  "label": "Chapéu",  "has_item": True,  "draw": "hat"},
        {"id": "acc_boina",   "label": "Boné",    "has_item": True,  "draw": "cap"},
        {"id": "acc_tiara",   "label": "Coroa",   "has_item": True,  "draw": "crown"},
    ],
    "fundo": [
        {"id": "fundo_roxo",    "label": "Roxo",    "color": "#6C3483"},
        {"id": "fundo_azul",    "label": "Azul",    "color": "#1A5276"},
        {"id": "fundo_verde",   "label": "Verde",   "color": "#1E8449"},
        {"id": "fundo_laranja", "label": "Laranja", "color": "#784212"},
        {"id": "fundo_rosa",    "label": "Rosa",    "color": "#922B75"},
    ],
}

CHAR_DEFAULTS = {
    "rosto": "rosto_1",
    "cabelo": "cabelo_1",
    "roupa": "roupa_1",
    "acessorio": "acc_none",
    "fundo": "fundo_roxo",
}


def get_option(category: str, option_id: str) -> dict:
    for opt in CHAR_OPTIONS[category]:
        if opt["id"] == option_id:
            return opt
    return CHAR_OPTIONS[category][0]
