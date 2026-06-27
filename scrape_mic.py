# -*- coding: utf-8 -*-
"""Скрапит реальные товары (название, цена US$, фото) с Made-in-China по 6 категориям,
скачивает фото и формирует data/import.csv для импорта в магазин AQUALUX."""
import os, re, csv, subprocess, time, html as H
from concurrent.futures import ThreadPoolExecutor

BASE=os.path.dirname(os.path.abspath(__file__)); PIMG=os.path.join(BASE,"assets","img","products")
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CATS=[
 ("smesitel","smart sensor bathroom faucet brass","Alamă masivă","Pe blat"),
 ("unitaz","smart toilet bidet intelligent","Porțelan sanitar","Pe pardoseală"),
 ("rakovina","marble stone wash basin sink","Piatră naturală","Pe blat"),
 ("polotenec","electric heated towel rail stainless","Oțel inoxidabil","Pe perete"),
 ("dush","thermostatic rain shower system set","Alamă & inox","Pe perete"),
 ("kuhnya","pull out kitchen faucet brass","Alamă masivă","Pe blat"),
]
PER=17
def fetch(url):
    try: return subprocess.run(["curl","-s","-m","25","-A",UA,url],capture_output=True,text=True,errors="ignore").stdout
    except Exception as e: return ""
def nice(v):
    v=int(round(v)); return int(round(v/10)*10) if v<1000 else int(round(v/50)*50)
def finish_of(name):
    n=name.lower()
    for k,v in [("gold","auriu"),("black","negru mat"),("chrome","crom"),("brushed","auriu periat"),
                ("matte","negru mat"),("white","alb"),("rose","auriu roze"),("gun","gun metal")]:
        if k in n: return v
    return "premium"
def clean(slug):
    s=slug.replace("-"," ").strip()
    s=re.sub(r"^(China|OEM|Wholesale|Hot Sale|Factory|New|2024|2025|2026)\s+","",s,flags=re.I)
    s=re.sub(r"\s+"," ",s)
    return (s[:70]).strip()

rows=[]; dl=[]
for cat,q,material,mount in CATS:
    url="https://www.made-in-china.com/productdirectory.do?word="+q.replace(" ","+")+"&subaction=hunt"
    h=fetch(url)
    if not h or len(h)<200000: print("!! пусто/блок:",cat,len(h)); continue
    # все фото с CDN (нормализуем схему)
    allimg=re.findall(r'(?:https?:)?//image\.made-in-china\.com/[A-Za-z0-9]+/[A-Za-z0-9\-_%.]+?\.(?:jpg|jpeg|png)',h)
    allimg=[("https:"+u if u.startswith("//") else u) for u in allimg]
    # упорядоченные уникальные товары
    seen=set(); items=[]
    for m in re.finditer(r'/product/([A-Za-z0-9]+)/([A-Za-z0-9\-]+)\.html',h):
        pid=m.group(1)
        if pid in seen: continue
        seen.add(pid); items.append((m.start(),pid,m.group(2)))
    n=0; usedimg=set()
    for i,(pos,pid,slug) in enumerate(items):
        key=slug[:24]
        img=next((u for u in allimg if key in u and u not in usedimg),None) \
            or next((u for u in allimg if key in u),None)
        pm=re.search(r'US\$<span>([\d.]+)',h[pos:pos+3500])
        if not img: continue
        usedimg.add(img)
        usd=float(pm.group(1)) if pm else 0
        name=clean(slug)
        if len(name)<8: continue
        n+=1
        fn=f"mic-{cat}-{n:02d}.jpg"
        dl.append((img,os.path.join(PIMG,fn)))
        price=nice(usd*80) if usd else nice({"smesitel":40,"unitaz":230,"rakovina":75,"polotenec":80,"dush":110,"kuhnya":38}[cat]*80)
        old=nice(price*1.28) if n%3==1 else 0
        badge="sale" if old else ("hot" if n<=2 else ("new" if n%5==3 else ""))
        rows.append({"category":cat,"name":name,"finish":finish_of(name),"material":material,
          "price":price,"old_price":old,"opt_usd":usd or "","feat":name,"image":fn,"badge":badge,
          "rating":round(4.6+(n%4)/10,1),"reviews":8+(n*7)%50,"warranty":"5 ani" if (usd or 50)>=80 else "3 ani",
          "mount":mount,"alibaba_url":"https://www.made-in-china.com"+ "/product/"+pid+"/"+slug+".html"})
        if n>=PER: break
    print(f"{cat}: {n} товаров")
    time.sleep(3)

# скачать фото параллельно
def grab(t):
    u,p=t; subprocess.run(["curl","-s","-m","30","-A",UA,"-o",p,u]); return os.path.getsize(p) if os.path.exists(p) else 0
print("Скачиваю фото:",len(dl),"…")
with ThreadPoolExecutor(max_workers=10) as ex:
    sizes=list(ex.map(grab,dl))
ok=sum(1 for s in sizes if s>3000)
print(f"Фото скачано: {ok}/{len(dl)} (валидных)")

cols=["category","name","finish","material","price","old_price","opt_usd","feat","image","badge","rating","reviews","warranty","mount","alibaba_url"]
with open(os.path.join(BASE,"data","import.csv"),"w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader()
    for r in rows: w.writerow(r)
print("Готово: data/import.csv —",len(rows),"товаров")
