# -*- coding: utf-8 -*-
# Гибрид-режим: N товаров/категорию на live с полными карточками (галереи) без backend.
# data.js = slim-индекс (для каталога/главной); data/full/<cat>.json = полные карточки (галереи/видео/specs) для страницы товара.
import json, os, shutil
from collections import defaultdict
BASE = os.path.dirname(os.path.abspath(__file__))
N = 90
P = json.load(open(os.path.join(BASE, "data", "products.json"), encoding="utf-8"))
C = json.load(open(os.path.join(BASE, "data", "content.json"), encoding="utf-8"))
by = defaultdict(list)
for p in P:
    by[p.get("cat")].append(p)
FULLDIR = os.path.join(BASE, "data", "full")
if os.path.isdir(FULLDIR): shutil.rmtree(FULLDIR)
os.makedirs(FULLDIR)
LITE = ("id", "name", "price", "img", "cat", "cat_name", "rating", "reviews", "old_price", "badge")
FULLK = ("id", "name", "price", "img", "images", "video", "description", "specs", "feat", "cat", "cat_name", "rating", "reviews", "old_price", "badge")
sub = []
nfull = 0
totbytes = 0
for cat, items in by.items():
    chosen = items[:N]
    for p in chosen:
        sub.append({k: p.get(k) for k in LITE})
    full = {}
    for p in chosen:
        rec = {k: p.get(k) for k in FULLK}
        if rec.get("images"):
            rec["images"] = rec["images"][:8]
        full[p["id"]] = rec
    data = json.dumps(full, ensure_ascii=False, separators=(",", ":"))
    open(os.path.join(FULLDIR, f"{cat}.json"), "w", encoding="utf-8").write(data)
    totbytes += len(data.encode("utf-8"))
    nfull += len(chosen)
open(os.path.join(BASE, "assets", "js", "data.js"), "w", encoding="utf-8").write(
    "window.AQ_PRODUCTS=" + json.dumps(sub, ensure_ascii=False, separators=(",", ":")) +
    ";\nwindow.AQ_CONTENT=" + json.dumps(C, ensure_ascii=False, separators=(",", ":")) + ";\n")
djs = os.path.getsize(os.path.join(BASE, "assets", "js", "data.js"))
print(f"slim-индекс (data.js): {len(sub)} товаров, {round(djs/1024)} КБ")
print(f"полных карточек: {nfull} в {len(by)} файлах data/full/, ~{round(totbytes/1024/1024,1)} МБ")
