#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

WIDTH = 800
HEIGHT = 600
SOURCE = Path(__file__).resolve().parent / "source"


def font(size: int, bold: bool = False):
    names = [
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for name in names:
        if Path(name).is_file():
            return ImageFont.truetype(name, size)
    return ImageFont.load_default()


def centered_text(draw, box, text, text_font, fill=(246, 244, 224, 255),
                  stroke_fill=(25, 20, 10, 255), stroke_width=1):
    left, top, right, bottom = box
    bounds = draw.textbbox((0, 0), text, font=text_font, stroke_width=stroke_width)
    x = left + (right - left - (bounds[2] - bounds[0])) // 2
    y = top + (bottom - top - (bounds[3] - bounds[1])) // 2 - bounds[1]
    draw.text((x, y), text, font=text_font, fill=fill,
              stroke_fill=stroke_fill, stroke_width=stroke_width)


def wood_texture(size, seed=0):
    width, height = size
    image = Image.new("RGBA", size, (54, 34, 17, 255))
    draw = ImageDraw.Draw(image)
    for y in range(height):
        wave = ((y * 17 + seed * 11) % 31) / 31
        shade = int(39 + wave * 14)
        draw.line((0, y, width, y), fill=(shade + 18, shade + 3, max(12, shade - 17), 255))
    for y in range(8, height, 17):
        draw.line((4, y, width - 5, y + (seed + y) % 3 - 1), fill=(104, 70, 34, 75), width=1)
    return image


def build_background(path):
    source = Image.open(SOURCE / "hero-forest.webp").convert("RGB")
    image = ImageOps.fit(source, (WIDTH, HEIGHT), method=Image.Resampling.LANCZOS,
                         centering=(0.50, 0.50))
    image = ImageEnhance.Color(image).enhance(0.94)
    image = ImageEnhance.Contrast(image).enhance(0.96)
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for y in range(235):
        alpha = int(44 * (1 - y / 235) ** 1.7)
        draw.line((0, y, WIDTH, y), fill=(4, 28, 13, alpha))
    Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB").save(path, "PNG", optimize=True)


def build_logo(path):
    source = Image.open(SOURCE / "everleaf-logo.webp").convert("RGBA")
    source.thumbnail((385, 150), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (397, 219), (0, 0, 0, 0))
    shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    alpha = source.getchannel("A").filter(ImageFilter.GaussianBlur(4))
    shadow.paste((0, 12, 2, 185), (8, 19), alpha)
    canvas = Image.alpha_composite(canvas, shadow)
    canvas.alpha_composite(source, ((397 - source.width) // 2, 8))
    draw = ImageDraw.Draw(canvas)
    centered_text(draw, (0, 157, 397, 183), "YOUR ADVENTURE, YOUR STORY",
                  font(13, True), fill=(250, 248, 224, 245), stroke_width=2,
                  stroke_fill=(19, 45, 16, 230))
    canvas.save(path, "PNG", optimize=True)


def build_frame(path):
    # UI.wz/Login.img/Common/frame is the legacy open-book overlay. Replacing
    # it with a fully transparent 800x600 canvas keeps the stock login controls
    # functional while letting the EverLeaf background fill the client cleanly.
    Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0)).save(path, "PNG", optimize=True)


def build_signboard(path):
    image = wood_texture((368, 236), 3)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((2, 2, 365, 233), radius=12, outline=(35, 25, 9, 255), width=4)
    draw.rounded_rectangle((7, 7, 360, 228), radius=9, outline=(144, 105, 49, 255), width=2)
    draw.text((12, 18), "Login ID", font=font(10, True), fill=(244, 239, 211, 255),
              stroke_width=1, stroke_fill=(25, 16, 7, 255))
    draw.text((12, 53), "Password", font=font(10, True), fill=(244, 239, 211, 255),
              stroke_width=1, stroke_fill=(25, 16, 7, 255))
    for top in (10, 45):
        draw.rounded_rectangle((58, top, 208, top + 31), radius=4,
                               fill=(25, 22, 14, 255), outline=(126, 94, 43, 255), width=2)
    draw.line((12, 82, 356, 82), fill=(141, 103, 45, 170), width=1)
    draw.line((12, 122, 356, 122), fill=(36, 22, 8, 180), width=1)
    centered_text(draw, (10, 186, 358, 213), "WELCOME TO EVERLEAF",
                  font(11, True), fill=(195, 218, 109, 215), stroke_width=1)
    image.save(path, "PNG", optimize=True)


def button(path, size, text, state, green=False, text_size=None):
    width, height = size
    palettes = ({
        "normal": ((103, 132, 15), (151, 180, 36)),
        "mouseOver": ((128, 158, 21), (183, 208, 52)),
        "pressed": ((73, 96, 10), (121, 148, 27)),
        "disabled": ((72, 75, 58), (105, 108, 82)),
    } if green else {
        "normal": ((67, 42, 20), (126, 83, 38)),
        "mouseOver": ((86, 54, 24), (158, 107, 49)),
        "pressed": ((47, 30, 15), (102, 66, 31)),
        "disabled": ((66, 59, 49), (103, 91, 74)),
    })
    fill, edge = palettes[state]
    image = Image.new("RGB", size, fill)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((1, 1, width - 2, height - 2), radius=max(3, height // 7),
                           fill=fill, outline=(28, 20, 9), width=2)
    draw.rounded_rectangle((4, 4, width - 5, height - 5), radius=max(2, height // 9),
                           outline=edge, width=1)
    centered_text(draw, (2, 1, width - 2, height - 2), text,
                  font(text_size or max(9, min(15, height // 3)), True),
                  fill=(246, 244, 224), stroke_width=1)
    image.save(path, "PNG", optimize=True)


def build_check(path, checked):
    image = Image.new("RGB", (18, 23), (58, 40, 20))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((1, 3, 16, 18), radius=3, fill=(31, 47, 13),
                           outline=(137, 168, 35), width=2)
    if checked:
        draw.line((4, 10, 8, 15, 15, 6), fill=(201, 229, 72), width=3, joint="curve")
    image.save(path, "PNG", optimize=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="client/branding/login/generated")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    required = [SOURCE / "hero-forest.webp", SOURCE / "everleaf-logo.webp"]
    missing = [str(item) for item in required if not item.is_file()]
    if missing:
        raise SystemExit("Missing EverLeaf source artwork: " + ", ".join(missing))

    build_background(output / "background.png")
    build_logo(output / "logo.png")
    build_frame(output / "frame.png")
    build_signboard(output / "signboard.png")
    specs = {
        "login": ((89, 42), "LOG IN", True, 14),
        "save-id": ((76, 23), "SAVE ID", False, 9),
        "find-id": ((82, 23), "FIND ID", False, 9),
        "reset-password": ((66, 23), "RESET", False, 9),
        "register": ((92, 38), "REGISTER", False, 11),
        "homepage": ((93, 38), "HOMEPAGE", False, 10),
        "quit": ((84, 38), "QUIT", False, 11),
    }
    for name, (size, label, green, text_size) in specs.items():
        for state in ("normal", "mouseOver", "pressed", "disabled"):
            button(output / f"{name}-{state}.png", size, label, state, green, text_size)
    build_check(output / "check-0.png", False)
    build_check(output / "check-1.png", True)
    print(f"Generated complete EverLeaf login theme in {output}")


if __name__ == "__main__":
    main()
