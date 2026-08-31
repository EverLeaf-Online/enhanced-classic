#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH = 800
HEIGHT = 600


def load_font(size: int, bold: bool = False):
    candidates = []
    if os.name == "nt":
        candidates += [
            rf"C:\Windows\Fonts\{'georgiab.ttf' if bold else 'georgia.ttf'}",
            rf"C:\Windows\Fonts\{'segoeuib.ttf' if bold else 'segoeui.ttf'}",
        ]
    else:
        candidates += [
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        ]
    for path in candidates:
        if Path(path).is_file():
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()


def vertical_gradient(top, bottom):
    image = Image.new("RGB", (WIDTH, HEIGHT))
    px = image.load()
    for y in range(HEIGHT):
        t = y / (HEIGHT - 1)
        # slightly brighten the middle for a misty clearing
        mist = math.sin(t * math.pi) * 0.10
        for x in range(WIDTH):
            vignette = abs(x - WIDTH / 2) / (WIDTH / 2)
            k = max(0.0, min(1.0, t + vignette * 0.06 - mist))
            px[x, y] = tuple(int(top[i] * (1 - k) + bottom[i] * k) for i in range(3))
    return image


def draw_leaf(draw: ImageDraw.ImageDraw, cx: float, cy: float, radius: float, angle: float, fill):
    points = []
    for i in range(24):
        a = (i / 24) * math.tau
        # tapered ellipse/leaf profile
        x = math.cos(a) * radius
        y = math.sin(a) * radius * 0.52
        ca, sa = math.cos(angle), math.sin(angle)
        points.append((cx + x * ca - y * sa, cy + x * sa + y * ca))
    draw.polygon(points, fill=fill)


def build_background(path: Path):
    random.seed(830250)
    image = vertical_gradient((76, 142, 112), (20, 55, 43))

    # Soft distant glow/mist.
    mist = Image.new("RGBA", image.size, (0, 0, 0, 0))
    md = ImageDraw.Draw(mist)
    for _ in range(16):
        x = random.randint(120, 720)
        y = random.randint(90, 420)
        rx = random.randint(90, 220)
        ry = random.randint(30, 90)
        md.ellipse((x-rx, y-ry, x+rx, y+ry), fill=(220, 244, 226, random.randint(8, 18)))
    mist = mist.filter(ImageFilter.GaussianBlur(24))
    image = Image.alpha_composite(image.convert("RGBA"), mist)

    # Distant forest silhouettes.
    layer = Image.new("RGBA", image.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x in range(-30, 850, 55):
        h = random.randint(185, 315)
        base = 510
        trunk_w = random.randint(18, 30)
        d.rounded_rectangle((x, base-h, x+trunk_w, base+35), radius=8, fill=(24, 67, 50, 165))
        for j in range(7):
            cy = base-h+35+j*32
            spread = 65-j*4
            d.polygon([(x+trunk_w/2, cy-48), (x-spread, cy+38), (x+trunk_w+spread, cy+38)], fill=(26, 83, 58, 100))
    image = Image.alpha_composite(image, layer.filter(ImageFilter.GaussianBlur(2.2)))

    # Foreground giant tree, rooted on the left, with a clean clearing on the right for the stock signboard.
    fg = Image.new("RGBA", image.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(fg)
    d.polygon([(0, 600), (0, 0), (86, 0), (112, 94), (99, 205), (142, 326), (119, 600)], fill=(57, 64, 35, 255))
    d.polygon([(26, 600), (58, 0), (125, 0), (145, 112), (129, 218), (175, 362), (151, 600)], fill=(87, 83, 42, 235))
    d.polygon([(72, 600), (100, 0), (145, 0), (162, 130), (148, 260), (187, 410), (170, 600)], fill=(113, 96, 52, 180))
    # bark highlights
    for _ in range(18):
        x = random.randint(30, 155)
        y = random.randint(-30, 590)
        d.line((x, y, x+random.randint(-8, 12), y+random.randint(55, 130)), fill=(169, 145, 81, 80), width=random.randint(2, 5))

    # Grass bank and stones.
    d.polygon([(0, 515), (205, 485), (390, 500), (590, 478), (800, 500), (800, 600), (0, 600)], fill=(44, 91, 54, 255))
    d.polygon([(0, 541), (230, 505), (440, 525), (620, 500), (800, 518), (800, 600), (0, 600)], fill=(37, 75, 48, 210))
    for _ in range(26):
        x = random.randint(120, 760)
        y = random.randint(490, 585)
        r = random.randint(6, 17)
        d.ellipse((x-r, y-r//2, x+r, y+r//2), fill=(95, 112, 88, random.randint(70, 150)))

    # Foreground leaves around the corners, but not over the central login panel.
    leaf_palette = [(63, 137, 78, 220), (89, 158, 88, 210), (45, 111, 69, 230), (118, 170, 88, 185)]
    for _ in range(62):
        if random.random() < 0.68:
            cx = random.choice([random.randint(-10, 210), random.randint(700, 825)])
        else:
            cx = random.randint(0, 800)
        cy = random.choice([random.randint(-15, 115), random.randint(470, 625)])
        draw_leaf(d, cx, cy, random.randint(7, 18), random.random()*math.pi, random.choice(leaf_palette))

    image = Image.alpha_composite(image, fg)

    # Subtle EverLeaf signature in the lower-left, separate from the main logo node.
    d = ImageDraw.Draw(image)
    font = load_font(17, bold=True)
    d.text((32, 552), "EVERLEAF", font=font, fill=(232, 244, 222, 185), stroke_width=1, stroke_fill=(20, 49, 35, 150))
    d.text((33, 574), "ENHANCED CLASSIC", font=load_font(9, bold=True), fill=(199, 221, 188, 150))

    path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(path, format="PNG", optimize=True)


def build_logo(path: Path):
    canvas = Image.new("RGBA", (430, 132), (0, 0, 0, 0))
    d = ImageDraw.Draw(canvas)

    # Soft shadow plate behind the wordmark improves readability on old v83 blending.
    d.rounded_rectangle((19, 23, 410, 110), radius=38, fill=(9, 35, 24, 95), outline=(222, 236, 192, 55), width=2)

    title = "EverLeaf"
    title_font = load_font(62, bold=True)
    bbox = d.textbbox((0, 0), title, font=title_font, stroke_width=1)
    tw = bbox[2] - bbox[0]
    x = (430 - tw) // 2 + 7
    y = 26
    d.text((x+3, y+4), title, font=title_font, fill=(7, 25, 17, 175), stroke_width=3, stroke_fill=(7, 25, 17, 120))
    d.text((x, y), title, font=title_font, fill=(235, 245, 208, 255), stroke_width=2, stroke_fill=(44, 98, 56, 255))

    # Leaf accent over the final word.
    draw_leaf(d, 357, 27, 22, -0.52, (108, 177, 92, 255))
    d.line((346, 39, 369, 15), fill=(229, 244, 205, 220), width=2)

    sub = "ENHANCED CLASSIC"
    sf = load_font(12, bold=True)
    sb = d.textbbox((0, 0), sub, font=sf)
    sw = sb[2] - sb[0]
    d.text(((430-sw)//2, 102), sub, font=sf, fill=(206, 227, 188, 235))

    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="client/branding/login/generated")
    args = parser.parse_args()
    output = Path(args.output)
    build_background(output / "background.png")
    build_logo(output / "logo.png")
    print(f"Generated {output / 'background.png'} and {output / 'logo.png'}")


if __name__ == "__main__":
    main()
