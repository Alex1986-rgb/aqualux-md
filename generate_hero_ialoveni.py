# -*- coding: utf-8 -*-
"""Современные hero-изображения в стиле города Яловены (Молдова):
зелёные холмы / виноградники + тёплый закат + премиум-золото. Modern, trendy."""
import math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

HERO = Path(__file__).resolve().parent/"assets/img/hero"
HERO.mkdir(parents=True, exist_ok=True)
W, H = 1640, 780

def lerp(a, b, t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))

def hero(path, sky_top, sky_bot, hills, sun, sunpos=(0.74, 0.46)):
    img = Image.new("RGB", (W, H), sky_top)
    d = ImageDraw.Draw(img)
    # небо-градиент
    for y in range(H):
        d.line([(0, y), (W, y)], fill=lerp(sky_top, sky_bot, y/H))
    # солнце (мягкое сияние)
    sx, sy = int(W*sunpos[0]), int(H*sunpos[1])
    glow = Image.new("RGB", (W, H), (0,0,0)); gd = ImageDraw.Draw(glow)
    for r in range(260, 0, -6):
        t = r/260
        gd.ellipse([sx-r, sy-r, sx+r, sy+r], fill=lerp(sun, (0,0,0), t))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    img = Image.blend(img, Image.composite(Image.new("RGB",(W,H),sun), img,
          glow.convert("L").point(lambda v:int(v*0.9))), 0.55)
    d = ImageDraw.Draw(img)
    d.ellipse([sx-46, sy-46, sx+46, sy+46], fill=lerp(sun,(255,250,230),0.4))
    # слои холмов Яловен (виноградники)
    layers = [
        (0.62, hills[0], 0.030, 38),
        (0.72, hills[1], 0.045, 60),
        (0.83, hills[2], 0.028, 22),
    ]
    for base, col, amp, phase in layers:
        pts = [(0, H)]
        for x in range(0, W+1, 8):
            y = int(H*base + math.sin(x/170.0+phase)*H*amp + math.sin(x/53.0)*H*0.012)
            pts.append((x, y))
        pts.append((W, H))
        d.polygon(pts, fill=col)
    # ряды виноградника на ближнем холме (тонкие штрихи)
    g = hills[2]; gl = lerp(g,(255,255,255),0.10)
    for x in range(0, W, 26):
        d.line([(x, int(H*0.86)),(x+40, H)], fill=gl, width=1)
    # тонкая золотая линия горизонта
    d.line([(0, int(H*0.83)),(W, int(H*0.83))], fill=(200,162,76), width=1)
    img.save(path, "JPEG", quality=88)

# 1 — рассвет над виноградниками (тёпло-золотой)
hero(HERO/"hero1.jpg", (28,30,34), (94,70,40), [(40,52,46),(30,42,38),(20,30,26)], (235,180,90), (0.78,0.44))
# 2 — изумрудные холмы Яловен (зелёно-премиум)
hero(HERO/"hero2.jpg", (22,32,33), (40,66,58), [(34,58,50),(24,46,40),(16,32,28)], (210,200,120), (0.24,0.40))
# 3 — премиум закат (тёмный+золото)
hero(HERO/"hero3.jpg", (20,18,16), (70,46,26), [(38,34,28),(28,24,20),(18,16,13)], (224,150,70), (0.70,0.50))
print("hero1/2/3.jpg — Ialoveni edition готовы")
