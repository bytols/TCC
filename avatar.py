"""
Avatar composto em SVG, montado por camadas independentes:
fundo · cabelo (atrás do corpo) · ombros · rosto · orelhas · cabelo (frente) ·
olhos/boca · acessório.

A cabeça é sempre redonda (formato único). É trocável: estilo de cabelo, cor de
pele, cor de cabelo, acessório e cor de fundo. A MESMA geometria é espelhada em
`static/js/avatar.js` (preview ao vivo no formulário). Veja `data/character_options.py`.

Chapéu e gorro escondem o cabelo (cobrem a cabeça). Cabelo longo é desenhado
ANTES dos ombros, ficando por trás do corpo.

`generate_avatar` grava `static/img/avatars/{id}.svg` e devolve o caminho público.
"""
import os
from data.character_options import CHAR_OPTIONS, CHAR_DEFAULTS

AVATAR_DIR = os.path.join(os.path.dirname(__file__), "static", "img", "avatars")
SHOULDER = "#2E2A45"


def _color(category: str, option_id: str, fallback: str = "#888888") -> str:
    for opt in CHAR_OPTIONS.get(category, []):
        if opt["id"] == option_id:
            return opt.get("color", fallback)
    return fallback


# Cabeça redonda única: círculo cx=100 cy=94 r=46 (topo y=48, base y=140).
FACE_CX, FACE_CY, FACE_R = 100, 94, 46


def _face(skin: str) -> str:
    return f'<circle cx="{FACE_CX}" cy="{FACE_CY}" r="{FACE_R}" fill="{skin}"/>'


def _hair_back(style: str, hair: str) -> str:
    # Desenhado ANTES dos ombros: cabelo comprido cai por trás do corpo.
    if style == "liso_longo":
        return f'<rect x="46" y="58" width="108" height="118" rx="52" fill="{hair}"/>'
    return ""


def _hair_front(style: str, hair: str) -> str:
    # Touca seguindo o círculo da cabeça (r=48, levemente maior que o rosto
    # r=46, para nunca ficar menor que a cabeça), com a linha do cabelo
    # descendo na testa até y=74 (acima dos olhos em y=96).
    cap = ('<path d="M52,94 A48,48 0 0 1 148,94 Q126,74 100,74 '
           f'Q74,74 52,94 Z" fill="{hair}"/>')
    if style == "careca":
        return ""
    if style == "liso_curto" or style == "liso_longo":
        return cap
    if style == "coque":
        return cap + f'<circle cx="100" cy="40" r="15" fill="{hair}"/>'
    if style == "cacheado":
        bumps = "".join(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{hair}"/>'
            for cx, cy, r in [(58, 82, 15), (70, 56, 17), (96, 44, 18),
                              (124, 46, 18), (142, 60, 16), (146, 84, 14)]
        )
        return cap + bumps
    if style == "moicano":
        return f'<path d="M86,50 Q100,22 114,50 L108,82 Q100,88 92,82 Z" fill="{hair}"/>'
    return cap


def _accessory(acc: str) -> str:
    if acc == "oculos":
        return ('<g><rect x="72" y="88" width="22" height="17" rx="8" fill="rgba(255,255,255,0.18)" stroke="#222" stroke-width="3"/>'
                '<rect x="106" y="88" width="22" height="17" rx="8" fill="rgba(255,255,255,0.18)" stroke="#222" stroke-width="3"/>'
                '<line x1="94" y1="96" x2="106" y2="96" stroke="#222" stroke-width="3"/></g>')
    if acc == "bone":
        # Gorro (beanie): copa arredondada sobre a cabeça + barra dobrada + pompom.
        return ('<path d="M50,86 Q50,38 100,38 Q150,38 150,86 Z" fill="#C0392B"/>'
                '<rect x="48" y="78" width="104" height="15" rx="7.5" fill="#A93226"/>'
                '<circle cx="100" cy="34" r="9" fill="#F2F2F2"/>')
    if acc == "chapeu":
        return ('<ellipse cx="100" cy="58" rx="60" ry="12" fill="#1A1A1A"/>'
                '<rect x="74" y="24" width="52" height="36" rx="6" fill="#1A1A1A"/>')
    if acc == "brinco":
        return '<circle cx="143" cy="110" r="4.5" fill="#F4D03F"/>'
    if acc == "headphone":
        return ('<path d="M54,94 Q54,40 100,40 Q146,40 146,94" fill="none" stroke="#222" stroke-width="7"/>'
                '<rect x="46" y="88" width="16" height="26" rx="7" fill="#222"/>'
                '<rect x="138" y="88" width="16" height="26" rx="7" fill="#222"/>')
    return ""


def build_avatar_svg(character: dict) -> str:
    cabelo = character.get("cabelo", CHAR_DEFAULTS["cabelo"])
    acc = character.get("acessorio", CHAR_DEFAULTS["acessorio"])
    skin = _color("pele", character.get("pele", CHAR_DEFAULTS["pele"]), "#F1C27D")
    hair = _color("cor_cabelo", character.get("cor_cabelo", CHAR_DEFAULTS["cor_cabelo"]), "#1A1A1A")
    bg = _color("fundo", character.get("fundo", CHAR_DEFAULTS["fundo"]), "#6C3483")

    # Chapéu e gorro cobrem a cabeça — escondem o cabelo para não conflitar.
    hide_hair = acc in ("chapeu", "bone")
    hair_back = "" if hide_hair else _hair_back(cabelo, hair)
    hair_front = "" if hide_hair else _hair_front(cabelo, hair)

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">'
        '<defs><clipPath id="c"><circle cx="100" cy="100" r="100"/></clipPath></defs>'
        f'<circle cx="100" cy="100" r="100" fill="{bg}"/>'
        '<g clip-path="url(#c)">'
        f'{hair_back}'
        f'<ellipse cx="100" cy="200" rx="72" ry="56" fill="{SHOULDER}"/>'
        f'{_face(skin)}'
        f'<ellipse cx="57" cy="98" rx="8" ry="12" fill="{skin}"/><ellipse cx="143" cy="98" rx="8" ry="12" fill="{skin}"/>'
        f'{hair_front}'
        '<ellipse cx="84" cy="96" rx="5.5" ry="6.5" fill="#1A1A1A"/><ellipse cx="116" cy="96" rx="5.5" ry="6.5" fill="#1A1A1A"/>'
        '<path d="M86,118 Q100,130 114,118" fill="none" stroke="#1A1A1A" stroke-width="3.5" stroke-linecap="round"/>'
        f'{_accessory(acc)}'
        '</g></svg>'
    )


def generate_avatar(character: dict, player_id: int) -> str:
    os.makedirs(AVATAR_DIR, exist_ok=True)
    path = os.path.join(AVATAR_DIR, f"{player_id}.svg")
    with open(path, "w", encoding="utf-8") as f:
        f.write(build_avatar_svg(character))
    return f"/static/img/avatars/{player_id}.svg"
