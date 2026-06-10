"""
Avatar composto em SVG, montado por camadas independentes:
fundo · cabelo (atrás) · rosto (forma) · orelhas · olhos/boca · cabelo (frente) · acessório.

Cada peça é trocável: forma do rosto, estilo de cabelo, cor de pele, cor de
cabelo, acessório e cor de fundo. A MESMA geometria é espelhada em
`static/js/avatar.js` (preview ao vivo no formulário). Veja `data/character_options.py`.

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


def _face(shape: str, skin: str) -> str:
    if shape == "redondo":
        return f'<circle cx="100" cy="94" r="46" fill="{skin}"/>'
    if shape == "quadrado":
        return f'<rect x="56" y="50" width="88" height="92" rx="24" fill="{skin}"/>'
    if shape == "triangular":
        return f'<path d="M58,74 Q58,50 100,50 Q142,50 142,74 L116,130 Q100,146 84,130 Z" fill="{skin}"/>'
    # oval (padrão)
    return f'<ellipse cx="100" cy="94" rx="42" ry="50" fill="{skin}"/>'


def _hair_back(style: str, hair: str) -> str:
    if style == "liso_longo":
        return f'<rect x="48" y="52" width="104" height="108" rx="46" fill="{hair}"/>'
    if style == "cacheado":
        return f'<rect x="50" y="50" width="100" height="96" rx="48" fill="{hair}"/>'
    return ""


def _hair_front(style: str, hair: str) -> str:
    cap = (f'<path d="M56,82 C56,42 144,42 144,82 C144,64 126,56 100,56 '
           f'C74,56 56,64 56,82 Z" fill="{hair}"/>')
    if style == "careca":
        return ""
    if style == "liso_curto" or style == "liso_longo":
        return cap
    if style == "coque":
        return cap + f'<circle cx="100" cy="40" r="15" fill="{hair}"/>'
    if style == "cacheado":
        return ("".join(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{hair}"/>'
            for cx, cy, r in [(64, 60, 14), (84, 50, 16), (104, 48, 16), (124, 52, 15), (140, 62, 13)]
        ))
    if style == "moicano":
        return f'<path d="M89,42 Q100,32 111,42 L105,90 Q100,96 95,90 Z" fill="{hair}"/>'
    return cap


def _accessory(acc: str) -> str:
    if acc == "oculos":
        return ('<g><rect x="72" y="88" width="22" height="17" rx="8" fill="rgba(255,255,255,0.18)" stroke="#222" stroke-width="3"/>'
                '<rect x="106" y="88" width="22" height="17" rx="8" fill="rgba(255,255,255,0.18)" stroke="#222" stroke-width="3"/>'
                '<line x1="94" y1="96" x2="106" y2="96" stroke="#222" stroke-width="3"/></g>')
    if acc == "bone":
        return ('<path d="M56,68 Q100,30 144,68 Q120,56 100,56 Q80,56 56,68 Z" fill="#C0392B"/>'
                '<path d="M138,66 Q164,62 162,72 Q142,74 128,70 Z" fill="#922B1E"/>')
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
    rosto = character.get("rosto", CHAR_DEFAULTS["rosto"])
    cabelo = character.get("cabelo", CHAR_DEFAULTS["cabelo"])
    acc = character.get("acessorio", CHAR_DEFAULTS["acessorio"])
    skin = _color("pele", character.get("pele", CHAR_DEFAULTS["pele"]), "#F1C27D")
    hair = _color("cor_cabelo", character.get("cor_cabelo", CHAR_DEFAULTS["cor_cabelo"]), "#1A1A1A")
    bg = _color("fundo", character.get("fundo", CHAR_DEFAULTS["fundo"]), "#6C3483")

    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">'
        '<defs><clipPath id="c"><circle cx="100" cy="100" r="100"/></clipPath></defs>'
        f'<circle cx="100" cy="100" r="100" fill="{bg}"/>'
        '<g clip-path="url(#c)">'
        f'<ellipse cx="100" cy="200" rx="72" ry="56" fill="{SHOULDER}"/>'
        f'{_hair_back(cabelo, hair)}'
        f'{_face(rosto, skin)}'
        f'<ellipse cx="57" cy="98" rx="8" ry="12" fill="{skin}"/><ellipse cx="143" cy="98" rx="8" ry="12" fill="{skin}"/>'
        f'{_hair_front(cabelo, hair)}'
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
