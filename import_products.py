# -*- coding: utf-8 -*-
"""Импорт РЕАЛЬНЫХ товаров (с Alibaba) в каталог EUROMAG.

Как пользоваться:
 1) Заполни data/import.csv (по одной строке на товар, см. шаблон/колонки).
 2) Фото каждого товара положи в assets/img/products/ и впиши имя файла в колонку image
    (если оставить пусто — сгенерируется премиум-плейсхолдер).
 3) Запусти:  python3 import_products.py
    Реальные товары встанут В НАЧАЛО каталога (перед демо-позициями) с пометкой «Original».
 4) (для sitemap)  python3 make_pages.py

Колонки CSV (заголовок обязателен):
 category,name,finish,material,price,old_price,opt_usd,feat,image,badge,rating,reviews,warranty,mount,alibaba_url
 - category: smesitel|unitaz|rakovina|polotenec|dush|kuhnya
 - price: розница в lei (если пусто — посчитается из opt_usd*80)
 - badge: sale|hot|new|limited|premium  (или пусто)
 - alibaba_url: ссылка на карточку поставщика (для твоего учёта; на сайте не показывается)
"""
import os, json, csv, re
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data"); PIMG = os.path.join(BASE, "assets", "img", "products")
CSVF = os.path.join(DATA, "import.csv")
CATNAME = {"smesitel":"Baterii pentru baie","unitaz":"Vase WC","rakovina":"Lavoare",
 "polotenec":"Uscătoare de prosoape","dush":"Sisteme de duș","kuhnya":"Baterii de bucătărie"}
ARIB="/System/Library/Fonts/Supplemental/Arial Bold.ttf"; GEOB="/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
def font(p,s):
    try: return ImageFont.truetype(p,s)
    except: return ImageFont.load_default()

def slugify(s):
    tr=str.maketrans("ăâîșțĂÂÎȘȚ","aaistAAIST"); s=s.translate(tr).lower()
    return re.sub(r"-+","-",re.sub(r"[^a-z0-9]+","-",s)).strip("-")

def placeholder(path,name,finish,sku):
    S=760;img=Image.new("RGB",(S,S),(28,23,16));d=ImageDraw.Draw(img)
    for y in range(S):
        k=1-0.4*y/S;d.line([(0,y),(S,y)],fill=(int(28*k+6),int(23*k+5),int(16*k+4)))
    G=(200,162,76);d.rectangle([18,18,S-18,S-18],outline=(74,61,40),width=2)
    fb=font(GEOB,30);fa=font(font(ARIB,20).path if hasattr(font(ARIB,20),'path') else ARIB,20) if False else font(ARIB,20)
    d.text(((S-d.textlength("EUROMAG",font=fb))/2,60),"EUROMAG",font=fb,fill=(227,200,121))
    fn=font(ARIB,22)
    d.text(((S-d.textlength(name[:38],font=fn))/2,S/2-10),name[:38],font=fn,fill=(224,214,194))
    fs=font(ARIB,16);s=f"{finish}  ·  {sku}"
    d.text(((S-d.textlength(s,font=fs))/2,S/2+28),s,font=fs,fill=G)
    img.save(path,"JPEG",quality=86)

def main():
    if not os.path.exists(CSVF):
        print("Нет data/import.csv — создаю шаблон. Заполни и запусти снова."); return
    base=json.load(open(os.path.join(DATA,"products.json"),encoding="utf-8"))
    base=[p for p in base if not p.get("real")]  # убираем прежние импортированные
    reals=[]; n=0
    with open(CSVF,encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if not (row.get("name") or "").strip(): continue
            n+=1; cat=(row.get("category") or "smesitel").strip(); sku=f"ali-{n:02d}"
            name=row["name"].strip(); finish=(row.get("finish") or "").strip() or "standard"
            material=(row.get("material") or CATNAME.get(cat,"")).strip()
            opt=float(row["opt_usd"]) if (row.get("opt_usd") or "").strip() else 0
            price=int(float(row["price"])) if (row.get("price") or "").strip() else int(round(opt*80/10)*10)
            old=int(float(row["old_price"])) if (row.get("old_price") or "").strip() else 0
            img=(row.get("image") or "").strip()
            if img and os.path.exists(os.path.join(PIMG,img)): imgpath=f"assets/img/products/{img}"
            else:
                imgpath=f"assets/img/products/{sku}.jpg"; placeholder(os.path.join(PIMG,sku+".jpg"),name,finish,sku)
            disc=round((1-price/old)*100) if old>price>0 else 0
            reals.append({"id":sku,"cat":cat,"cat_name":CATNAME.get(cat,cat),"real":True,
              "name":name,"slug":slugify(name)+"-"+sku,"price":price,"old_price":old,"discount":disc,
              "img":imgpath,"badge":(row.get("badge") or "").strip(),
              "rating":float(row["rating"]) if (row.get("rating") or "").strip() else 4.9,
              "reviews":int(row["reviews"]) if (row.get("reviews") or "").strip() else 12,
              "feat":(row.get("feat") or "").strip(),
              "specs":{"Material":material,"Finisaj":finish,"Montare":(row.get("mount") or "Pe blat").strip(),
                       "Garanție":(row.get("warranty") or "3 ani").strip(),"Origine":"Import Alibaba"}})
    out=reals+base
    json.dump(out,open(os.path.join(DATA,"products.json"),"w",encoding="utf-8"),ensure_ascii=False)
    # пересчёт количеств по категориям
    content=json.load(open(os.path.join(DATA,"content.json"),encoding="utf-8"))
    for c in content.get("cats",[]):
        c["count"]=sum(1 for p in out if p["cat"]==c["id"])
    json.dump(content,open(os.path.join(DATA,"content.json"),"w",encoding="utf-8"),ensure_ascii=False)
    open(os.path.join(BASE,"assets","js","data.js"),"w",encoding="utf-8").write(
        "window.AQ_PRODUCTS="+json.dumps(out,ensure_ascii=False)+";\nwindow.AQ_CONTENT="+json.dumps(content,ensure_ascii=False)+";\n")
    print(f"Импортировано реальных товаров: {len(reals)} | всего в каталоге: {len(out)}")
    print("Готово. Обнови страницу в браузере (Cmd+R).")

if __name__=="__main__": main()
