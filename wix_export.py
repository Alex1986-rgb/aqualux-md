# -*- coding: utf-8 -*-
"""Экспорт каталога EUROMAG в CSV формата Wix Stores (импорт товаров).
Картинки берутся по live-URL с GitHub Pages (Wix их скачает при импорте)."""
import json, csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LIVE = "https://alex1986-rgb.github.io/aqualux-md/"
RIBBON = {"sale":"Reducere","hot":"Top vânzări","new":"Nou","limited":"Stoc limitat","premium":"Premium","":""}

products = json.loads((ROOT/"data/products.json").read_text(encoding="utf-8"))

# Заголовки CSV Wix Stores (импорт товаров)
cols = ["handleId","fieldType","name","description","productImageUrl","collection","sku","ribbon",
        "price","surcharge","visible","discountMode","discountValue","inventory","weight","cost","brand"]

rows = []
for p in products:
    sp = p.get("specs", {})
    desc = (f"{p.get('feat','')}. "
            f"Material: {sp.get('Material','')}. Finisaj: {sp.get('Finisaj','')}. "
            f"Montare: {sp.get('Montare','')}. Garanție: {sp.get('Garanție','')}. "
            f"Origine: {sp.get('Origine','')}.")
    img = LIVE + p["img"]
    rows.append({
        "handleId": p["id"], "fieldType": "Product",
        "name": p["name"], "description": desc,
        "productImageUrl": img, "collection": p["cat_name"],
        "sku": p["id"], "ribbon": RIBBON.get(p.get("badge",""), ""),
        "price": p["price"], "surcharge": "",
        "visible": "true", "discountMode": "", "discountValue": "",
        "inventory": "InStock", "weight": "", "cost": "",  # cost пусто — приватно
        "brand": "EUROMAG",
    })

out = ROOT/"data/wix_products_import.csv"
with open(out, "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)
print(f"Wix CSV готов: {out.name} — {len(rows)} товаров")
print("Коллекции:", ", ".join(sorted(set(p['cat_name'] for p in products))))
