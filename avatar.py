import os
from PIL import Image, ImageDraw
from data.character_options import CHAR_OPTIONS

AVATAR_DIR = os.path.join(os.path.dirname(__file__), "static", "img", "avatars")


def _hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def _get_color(category: str, option_id: str) -> str:
    for opt in CHAR_OPTIONS[category]:
        if opt["id"] == option_id:
            return opt.get("color", "#888888")
    return "#888888"


def generate_avatar(character: dict, player_id: int) -> str:
    os.makedirs(AVATAR_DIR, exist_ok=True)

    size = 200
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    bg_hex = _get_color("fundo", character.get("fundo", "fundo_roxo"))
    draw.ellipse([0, 0, size - 1, size - 1], fill=bg_hex)

    body_hex = _get_color("roupa", character.get("roupa", "roupa_1"))
    draw.ellipse([25, 130, 175, 240], fill=body_hex)

    skin_hex = _get_color("rosto", character.get("rosto", "rosto_1"))
    draw.ellipse([55, 55, 145, 145], fill=skin_hex)

    hair_hex = _get_color("cabelo", character.get("cabelo", "cabelo_1"))
    draw.ellipse([48, 42, 152, 105], fill=hair_hex)
    draw.rectangle([48, 75, 152, 105], fill=hair_hex)
    draw.ellipse([57, 68, 143, 145], fill=skin_hex)

    eye_color = "#1A1A1A"
    draw.ellipse([77, 93, 90, 107], fill=eye_color)
    draw.ellipse([110, 93, 123, 107], fill=eye_color)

    draw.arc([82, 110, 118, 130], start=10, end=170, fill="#1A1A1A", width=3)

    acc_id = character.get("acessorio", "acc_none")
    if acc_id == "acc_oculos":
        draw.rectangle([72, 92, 95, 108], outline="#333", width=2)
        draw.rectangle([105, 92, 128, 108], outline="#333", width=2)
        draw.line([95, 99, 105, 99], fill="#333", width=2)
    elif acc_id == "acc_chapeu":
        draw.rectangle([50, 48, 150, 60], fill="#1A1A1A")
        draw.ellipse([40, 55, 160, 72], fill="#1A1A1A")
    elif acc_id == "acc_boina":
        draw.ellipse([52, 32, 148, 72], fill="#333333")
    elif acc_id == "acc_tiara":
        points = [(82, 45), (90, 30), (100, 42), (110, 28), (118, 44)]
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill="#F4D03F", width=3)
        for pt in points:
            draw.ellipse([pt[0]-3, pt[1]-3, pt[0]+3, pt[1]+3], fill="#F4D03F")

    path = os.path.join(AVATAR_DIR, f"{player_id}.png")
    img.save(path, "PNG")
    return f"/static/img/avatars/{player_id}.png"
