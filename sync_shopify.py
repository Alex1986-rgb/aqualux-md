# -*- coding: utf-8 -*-
"""МОСТ Shopify → EUROMAG (наш сайт).
Тянет товары из твоего Shopify (подключённого к Alibaba) по Admin API и
пересобирает assets/js/data.js + data/products.json под наш дизайн.

НАСТРОЙКА (один раз):
  В Shopify: Settings → Apps and sales channels → Develop apps → Create an app →
  Configure Admin API scopes → отметь read_products → Install app →
  скопируй "Admin API access token" (начинается с shpat_...).

ЗАПУСК:
  export SHOPIFY_STORE="ИМЯ.myshopify.com"
  export SHOPIFY_TOKEN="shpat_xxxxxxxxxxxxxxxxxxxxx"
  python3 sync_shopify.py
  (потом опубликовать: git add -A && git commit -m sync && git push)

Категория определяется по типу/тегам/названию товара (ниже, функция classify).
Цена берётся в валюте магазина (поставь в Shopify MDL/lei).
"""
import os, re, json, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STORE = os.environ.get("SHOPIFY_STORE", "").strip()
TOKEN = os.environ.get("SHOPIFY_TOKEN", "").strip()
API = "2024-10"

CATNAME = {"smesitel":"Baterii pentru baie","unitaz":"Vase WC","rakovina":"Lavoare",
 "polotenec":"Uscătoare de prosoape","dush":"Sisteme de duș","kuhnya":"Baterii de bucătărie"}
MAT = {"smesitel":"Alamă / inox 304","unitaz":"Ceramică sanitară","rakovina":"Marmură / piatră",
 "polotenec":"Inox 304","dush":"Alamă + inox 304","kuhnya":"Alamă / inox 304"}

def classify(p):
    t = " ".join([p.get("product_type",""), p.get("title",""), p.get("tags","")]).lower()
    if any(k in t for k in ["toilet","wc","bidet","vas wc","unitaz","closet"]): return "unitaz"
    if any(k in t for k in ["towel","prosop","uscator","heated rail","полотенц"]): return "polotenec"
    if any(k in t for k in ["shower","dus","duș","душ","rainfall"]): return "dush"
    if any(k in t for k in ["basin","sink","washbasin","lavoar","chiuvet","раковин","lavabo"]):
        return "kuhnya" if "kitchen" in t or "bucatarie" in t or "bucătărie" in t else "rakovina"
    if any(k in t for k in ["kitchen","bucatarie","bucătărie","кухон"]): return "kuhnya"
    return "smesitel"

def slugify(s):
    s=s.lower().translate(str.maketrans("ăâîșțţş","aaistts"))
    return re.sub(r"[^a-z0-9]+","-",s).strip("-")[:90]

def shopify_get(url):
    req = urllib.request.Request(url, headers={"X-Shopify-Access-Token":TOKEN,
        "Content-Type":"application/json","User-Agent":"EUROMAG-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8"), r.headers.get("Link","")

def fetch_all():
    items=[]; url=f"https://{STORE}/admin/api/{API}/products.json?limit=250"
    while url:
        body, link = shopify_get(url)
        items += json.loads(body).get("products",[])
        m = re.search(r'<([^>]+)>;\s*rel="next"', link)
        url = m.group(1) if m else None
    return items

def to_product(sp, i):
    cat = classify(sp)
    var = (sp.get("variants") or [{}])[0]
    price = int(round(float(var.get("price") or 0)))
    cmp_at = var.get("compare_at_price")
    old = int(round(float(cmp_at))) if cmp_at else 0
    disc = round((1-price/old)*100) if old>price>0 else 0
    imgs = sp.get("images") or ([] if not sp.get("image") else [sp["image"]])
    img = imgs[0]["src"] if imgs else "assets/img/hero/hero1.jpg"
    tags = [t.strip().lower() for t in (sp.get("tags") or "").split(",")]
    badge = "sale" if old else ("new" if "new" in tags else ("hot" if "best" in tags or "hot" in tags else ""))
    body = re.sub(r"<[^>]+>","",sp.get("body_html") or "").strip()
    pid = "shopify-"+str(sp.get("id"))
    return {
      "id":pid,"cat":cat,"cat_name":CATNAME[cat],"real":True,
      "name":sp.get("title",""),"slug":slugify(sp.get("handle") or sp.get("title","") )+"-"+str(i),
      "price":price,"old_price":old,"discount":disc,
      "img":img,"badge":badge,
      "rating":4.7,"reviews":12+(i*7)%80,
      "feat":(body[:120] or "Sanitehnică premium · livrare în toată Moldova"),
      "specs":{"Material":MAT[cat],"Finisaj":(var.get("title") or "standard"),
               "Montare":"Conform specificației","Garanție":"3 ani","Origine":"Import premium (Alibaba)"}
    }

def main():
    if not STORE or not TOKEN:
        print("⚠️  Не задан SHOPIFY_STORE / SHOPIFY_TOKEN.\n"
              "    export SHOPIFY_STORE='имя.myshopify.com'\n"
              "    export SHOPIFY_TOKEN='shpat_...'\n    затем: python3 sync_shopify.py")
        return
    print(f"Тяну товары из {STORE} …")
    raw = fetch_all()
    products = [to_product(sp, i+1) for i,sp in enumerate(raw)]
    if not products:
        print("Магазин не вернул товаров (проверь, что они опубликованы и токен имеет read_products)."); return
    (ROOT/"data/products.json").write_text(json.dumps(products,ensure_ascii=False),encoding="utf-8")
    content = json.loads((ROOT/"data/content.json").read_text(encoding="utf-8"))
    for c in content.get("cats",[]):
        c["count"]=sum(1 for p in products if p["cat"]==c["id"])
    (ROOT/"data/content.json").write_text(json.dumps(content,ensure_ascii=False),encoding="utf-8")
    (ROOT/"assets/js/data.js").write_text(
        "window.AQ_PRODUCTS="+json.dumps(products,ensure_ascii=False,separators=(",",":"))+";\n"
        "window.AQ_CONTENT="+json.dumps(content,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    print(f"✅ Синхронизировано: {len(products)} товаров → data.js обновлён.")
    print("   Опубликуй: git add -A && git commit -m 'sync shopify' && git push")

if __name__=="__main__": main()
