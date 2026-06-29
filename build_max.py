# -*- coding: utf-8 -*-
# МАКС-режим: ВСЕ товары на live без backend.
#  data/index.json      — полный lite-индекс всех товаров (для каталога: фильтр/поиск/пагинация клиентом) + поле s (номер шарда)
#  data/full/s<N>.json  — полные карточки (галерея до 8 фото / video / specs) шардами по SHARD штук
#  assets/js/data.js     — небольшой поднабор для главной (быстрая загрузка) + AQ_CONTENT
import json, os, shutil
from collections import defaultdict
BASE = os.path.dirname(os.path.abspath(__file__))
SHARD = 100
P = json.load(open(os.path.join(BASE, "data", "products.json"), encoding="utf-8"))
C = json.load(open(os.path.join(BASE, "data", "content.json"), encoding="utf-8"))
FULLDIR = os.path.join(BASE, "data", "full")
if os.path.isdir(FULLDIR): shutil.rmtree(FULLDIR)
os.makedirs(FULLDIR)
LITE = ("id", "name", "price", "img", "cat", "cat_name", "rating", "reviews", "old_price", "badge")
FULLK = ("id", "name", "price", "img", "images", "video", "description", "specs", "feat", "cat", "cat_name", "rating", "reviews", "old_price", "badge")
id2s = {}
index = []
totbytes = 0
for i in range(0, len(P), SHARD):
    chunk = P[i:i + SHARD]; sid = i // SHARD
    full = {}
    for p in chunk:
        rec = {k: p.get(k) for k in FULLK}
        if rec.get("images"): rec["images"] = rec["images"][:8]
        full[p["id"]] = rec
        id2s[p["id"]] = sid
    data = json.dumps(full, ensure_ascii=False, separators=(",", ":"))
    open(os.path.join(FULLDIR, f"s{sid}.json"), "w", encoding="utf-8").write(data)
    totbytes += len(data.encode("utf-8"))
for p in P:
    r = {k: p.get(k) for k in LITE}; r["s"] = id2s[p["id"]]; index.append(r)
ix = json.dumps(index, ensure_ascii=False, separators=(",", ":"))
open(os.path.join(BASE, "data", "index.json"), "w", encoding="utf-8").write(ix)
# поднабор для главной (12/кат) — с тем же s, чтобы ссылки вели сразу на нужный шард
by = defaultdict(list)
for p in P: by[p.get("cat")].append(p)
sub = []
for cat, items in by.items():
    for p in items[:12]:
        r = {k: p.get(k) for k in LITE}; r["s"] = id2s[p["id"]]; sub.append(r)
open(os.path.join(BASE, "assets", "js", "data.js"), "w", encoding="utf-8").write(
    "window.AQ_PRODUCTS=" + json.dumps(sub, ensure_ascii=False, separators=(",", ":")) +
    ";\nwindow.AQ_CONTENT=" + json.dumps(C, ensure_ascii=False, separators=(",", ":")) + ";\n")
nshard = (len(P) + SHARD - 1) // SHARD
print(f"index.json: {len(index)} товаров, {round(len(ix.encode())/1024/1024,1)} МБ")
print(f"шардов data/full/s*.json: {nshard}, ~{round(totbytes/1024/1024,1)} МБ")
print(f"data.js (главная): {len(sub)} товаров, {round(os.path.getsize(os.path.join(BASE,'assets','js','data.js'))/1024)} КБ")
