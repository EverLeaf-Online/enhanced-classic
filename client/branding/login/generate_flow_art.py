#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def centered(draw: ImageDraw.ImageDraw, box, text: str, size: int, fill=(246, 244, 224), stroke=(28, 22, 10)):
    f = font(size, True)
    l, t, r, b = box
    bounds = draw.textbbox((0, 0), text, font=f, stroke_width=1)
    x = l + (r - l - (bounds[2] - bounds[0])) // 2
    y = t + (b - t - (bounds[3] - bounds[1])) // 2 - bounds[1]
    draw.text((x, y), text, font=f, fill=fill, stroke_width=1, stroke_fill=stroke)


def make_button(path: Path, size, label: str, state: str, green: bool = False):
    width, height = size
    wood = {
        "normal": ((67, 48, 23), (151, 111, 50)),
        "mouseOver": ((84, 62, 28), (193, 143, 61)),
        "pressed": ((48, 35, 16), (112, 82, 35)),
        "disabled": ((66, 63, 52), (105, 98, 79)),
    }
    leaf = {
        "normal": ((74, 112, 22), (156, 190, 58)),
        "mouseOver": ((96, 139, 27), (198, 220, 83)),
        "pressed": ((54, 83, 15), (121, 154, 39)),
        "disabled": ((68, 77, 57), (106, 116, 83)),
    }
    fill, edge = (leaf if green else wood)[state]
    image = Image.new("RGB", size, fill)
    draw = ImageDraw.Draw(image)
    radius = max(4, min(9, height // 6))
    draw.rounded_rectangle((1, 1, width - 2, height - 2), radius=radius, fill=fill, outline=(27, 21, 9), width=2)
    draw.rounded_rectangle((4, 4, width - 5, height - 5), radius=max(3, radius - 2), outline=edge, width=1)
    if state not in ("pressed", "disabled"):
        draw.line((7, 5, width - 8, 5), fill=(235, 221, 155), width=1)
    centered(draw, (2, 1, width - 2, height - 2), label, 11 if height < 50 else 13)
    image.save(path, "PNG", optimize=True)


def make_char_info(path: Path):
    size = (183, 115)
    image = Image.new("RGB", size, (44, 34, 17))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((1, 1, 181, 113), radius=9, fill=(44, 34, 17), outline=(28, 21, 9), width=2)
    draw.rounded_rectangle((5, 5, 177, 109), radius=7, outline=(137, 105, 47), width=1)
    draw.rectangle((9, 9, 173, 105), fill=(24, 33, 17), outline=(93, 126, 43), width=1)
    # Keep this panel text-free: the native client draws character data over it.
    image.save(path, "PNG", optimize=True)


def make_select_world(path: Path):
    size = (150, 57)
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((3, 5, 146, 51), radius=10, fill=(43, 34, 16, 235), outline=(151, 117, 52, 255), width=2)
    draw.rounded_rectangle((7, 9, 142, 47), radius=7, outline=(100, 139, 42, 230), width=1)
    centered(draw, (6, 7, 144, 49), "SELECT WORLD", 12, fill=(221, 237, 150, 255), stroke=(20, 34, 12, 255))
    image.save(path, "PNG", optimize=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.output)
    root.mkdir(parents=True, exist_ok=True)

    specs = {
        "world-select": {
            "normal": (123, 44), "mouseOver": (124, 44), "pressed": (123, 44), "disabled": (123, 44)
        },
        "start": {state: (124, 52) for state in ("normal", "mouseOver", "pressed", "disabled")},
        "exit": {state: (124, 52) for state in ("normal", "mouseOver", "pressed", "disabled")},
        "start2": {state: (124, 52) for state in ("normal", "mouseOver", "pressed", "disabled")},
    }
    labels = {"world-select": "WORLD SELECT", "start": "START", "exit": "EXIT", "start2": "START"}
    for name, states in specs.items():
        for state, size in states.items():
            make_button(root / f"flow-{name}-{state}.png", size, labels[name], state, green=name in ("start", "start2"))

    make_char_info(root / "flow-char-info.png")
    make_select_world(root / "flow-select-world.png")
    print(f"Generated EverLeaf world/character-flow UI art in {root}")


if __name__ == "__main__":
    main()
