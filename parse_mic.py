# -*- coding: utf-8 -*-
"""Парсит локально сохранённые страницы /tmp/mic/<cat>.html → реальные товары,
качает фото, пишет data/import.csv и импортирует в магазин."""
import os, re, csv, subprocess, html as H
from concurrent.futures import ThreadPoolExecutor
BASE=os.path.dirname(os.path.abspath(__file__)); PIMG=os.path.join(BASE,"assets","img","products")
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
CATS=[("smesitel","Alamă masivă","Pe blat"),("unitaz","Porțelan sanitar","Pe pardoseală"),
 ("rakovina","Piatră naturală","Pe blat"),("polotenec","Oțel inoxidabil","Pe perete"),
 ("dush","Alamă & inox","Pe perete"),("kuhnya","Alamă masivă","Pe blat")]
DEF={"smesitel":40,"unitaz":230,"rakovina":75,"polotenec":80,"dush":110,"kuhnya":38}
PER=17
def nice(v):
    v=int(round(v)); return int(round(v/10)*10) if v<1000 else int(round(v/50)*50)
def finish_of(n):
    n=n.lower()
    for k,v in [("gold","auriu"),("black","negru mat"),("chrome","crom"),("brushed","auriu periat"),
                ("matte","negru mat"),("white","alb"),("rose","auriu roze"),("gunmetal","gun metal"),("gun ","gun metal")]:
        if k in n: return v
    return "premium"
def clean(slug):
    s=re.sub(r"\s+"," ",slug.replace("-"," ")).strip()
    s=re.sub(r"^(China|OEM|ODM|Wholesale|Hot Sale|Factory|New|Customized|2024|2025|2026)\s+","",s,flags=re.I)
    return s[:72].strip()

rows=[]; dl=[]
for cat,material,mount in CATS:
    fp=f"/tmp/mic/{cat}.html"
    if not os.path.exists(fp): print("нет",fp); continue
    h=open(fp,encoding="utf-8",errors="ignore").read()
    # карточки: имя из title=, + pid/slug
    cards=[(m.start(),H.unescape(m.group(1)),m.group(2),m.group(3))
           for m in re.finditer(r'<h2 class="product-name"[^>]*title="([^"]+)"[\s\S]{0,320}?/product/([A-Za-z0-9]+)/([A-Za-z0-9\-]+)\.html',h)]
    # фото товара (исключаем логотипы фабрик)
    imgs=[]
    for m in re.finditer(r'data-original="([^"]*image\.made-in-china[^"]*?\.(?:jpg|jpeg|png|webp)[^"]*)"',h):
        u=m.group(1); u="https:"+u if u.startswith("//") else u
        if "Co-Ltd" in u or "Co.," in u: continue
        imgs.append((m.start(),u))
    prices=[(m.start(),float(m.group(1))) for m in re.finditer(r'class="price">US\$<span>([\d.]+)',h)]
    n=0; used=set()
    seenpid=set()
    for tpos,title,pid,slug in cards:
        if pid in seenpid: continue
        seenpid.add(pid)
        cand=[(abs(ip-tpos),u) for ip,u in imgs if u not in used]
        img=min(cand)[1] if cand else (min([(abs(ip-tpos),u) for ip,u in imgs])[1] if imgs else None)
        if not img: continue
        used.add(img)
        usd=min([(abs(pp-tpos),v) for pp,v in prices])[1] if prices else 0
        name=clean(title)
        if len(name)<8: continue
        n+=1; fn=f"mic-{cat}-{n:02d}.webp"
        dl.append((img,os.path.join(PIMG,fn)))
        price=nice(usd*80) if usd else nice(DEF[cat]*80)
        old=nice(price*1.28) if n%3==1 else 0
        badge="sale" if old else ("hot" if n<=2 else ("new" if n%5==3 else ""))
        rows.append({"category":cat,"name":name,"finish":finish_of(name),"material":material,
          "price":price,"old_price":old,"opt_usd":usd or "","feat":name,"image":fn,"badge":badge,
          "rating":round(4.6+(n%4)/10,1),"reviews":8+(n*7)%50,"warranty":"5 ani" if (usd or 50)>=80 else "3 ani",
          "mount":mount,"alibaba_url":"https://www.made-in-china.com/product/"+pid+"/"+slug+".html"})
        if n>=PER: break
    print(f"{cat}: {n}")

def grab(t):
    u,p=t; subprocess.run(["curl","-s","-m","30","-A",UA,"-e","https://www.made-in-china.com/","-o",p,u])
    return os.path.getsize(p) if os.path.exists(p) else 0
print("Качаю фото:",len(dl))
with ThreadPoolExecutor(max_workers=8) as ex: sizes=list(ex.map(grab,dl))
ok=sum(1 for s in sizes if s>2500); print(f"Фото валидных: {ok}/{len(dl)}")
# удалить битые фото из строк (чтобы импорт дал плейсхолдер)
for (u,p),s in zip(dl,sizes):
    if s<=2500 and os.path.exists(p): os.remove(p)
valid=set(os.path.basename(p) for (u,p),s in zip(dl,sizes) if s>2500)
for r in rows:
    if r["image"] not in valid: r["image"]=""   # импортер сгенерит плейсхолдер
cols=["category","name","finish","material","price","old_price","opt_usd","feat","image","badge","rating","reviews","warranty","mount","alibaba_url"]
with open(os.path.join(BASE,"data","import.csv"),"w",encoding="utf-8",newline="") as f:
    w=csv.DictWriter(f,fieldnames=cols); w.writeheader(); [w.writerow(r) for r in rows]
print("import.csv:",len(rows),"товаров |",ok,"с реальным фото")
