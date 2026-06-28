# -*- coding: utf-8 -*-
"""МЕГА-каталог AQUALUX: ванная + кухня + мебель/стулья/столы/зеркала/аксессуары.
Публичный products.json/data.js — БЕЗ себестоимости.
Приватный data/supply.json — закуп+доставка, маржа, срок доставки (только локально, gitignored).
Масштабируется: меняй счётчики в COUNTS (до 5000 — тогда лучше backend Level 3)."""
import os, re, json, glob
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
PIMG = ROOT/"assets/img/products"; PIMG.mkdir(parents=True, exist_ok=True)
FX = 18.2  # USD→MDL

def slugify(s):
    s=s.lower().translate(str.maketrans("ăâîșțţş","aaistts"))
    return re.sub(r"[^a-z0-9]+","-",s).strip("-")[:80]
def nice(v):
    v=int(round(v)); return int(round(v/10)*10) if v<1000 else int(round(v/50)*50)

# реальные фото-пулы (с Made-in-China) для базовых категорий
def pool(cat): return sorted("assets/img/products/"+os.path.basename(p) for p in glob.glob(str(PIMG/f"mic-{cat}-*.webp")))
POOL={c:pool(c) for c in ["smesitel","kuhnya","unitaz","rakovina","polotenec","dush"]}

# премиум-плейсхолдер для новых категорий
def make_ph(path, label):
    S=760;img=Image.new("RGB",(S,S),(26,22,16));d=ImageDraw.Draw(img)
    for y in range(S):
        k=1-0.4*y/S;d.line([(0,y),(S,y)],fill=(int(26*k+6),int(22*k+5),int(16*k+4)))
    G=(200,162,76);d.rectangle([18,18,S-18,S-18],outline=(74,61,40),width=2);d.rectangle([30,30,S-30,S-30],outline=(111,90,52),width=1)
    d.ellipse([S//2-100,S//2-130,S//2+100,S//2+70],outline=G,width=3)
    from PIL import ImageFont
    def fnt(p,s):
        try:return ImageFont.truetype(p,s)
        except:return ImageFont.load_default()
    fb=fnt("/System/Library/Fonts/Supplemental/Georgia Bold.ttf",30)
    fl=fnt("/System/Library/Fonts/Supplemental/Arial Bold.ttf",22)
    d.text(((S-d.textlength("AQUALUX",font=fb))/2,60),"AQUALUX",font=fb,fill=(227,200,121))
    d.text(((S-d.textlength(label.upper(),font=fl))/2,S/2+100),label.upper(),font=fl,fill=G)
    img.save(path,"JPEG",quality=84)

FIN_BATH=["auriu","negru mat","crom","auriu periat","gun metal","alb mat"]
FIN_FURN=["alb lucios","stejar","nuc","gri antracit","negru mat","bej cașmir"]
SIZES_F=["","60 cm","80 cm","100 cm","120 cm"]
VARIANTS=["","Pro","Lux","Compact","XL","Smart","Premium","Plus","Max","Elite"]
VAR_MULT={"":1.0,"Pro":1.15,"Lux":1.4,"Compact":0.85,"XL":1.5,"Smart":1.6,"Premium":1.35,"Plus":1.1,"Max":1.7,"Elite":1.8}

# (id, nume, kind, base_usd, ship_usd, deliv(min,max), margin_k, material, mount, archetypes[(label,usd_mult)], finishes, sizes)
CATS=[
 ("smesitel","Baterii pentru baie","bath",40,12,(7,14),2.4,"Alamă / inox 304","Pe blat / perete",
  [("Baterie de lavoar cu senzor",1.0),("Baterie cu cascadă",0.8),("Baterie cu afișaj LED",1.5),("Baterie termostatică",1.8),("Baterie înaltă pentru vas",0.95),("Baterie încastrată",0.9)],FIN_BATH,[""]),
 ("kuhnya","Baterii de bucătărie","kitchen",35,12,(7,14),2.3,"Alamă / inox 304","Pe chiuvetă",
  [("Baterie cu cap extractibil",1.0),("Baterie cu braț flexibil",1.1),("Robinet filtru 3-în-1",0.9),("Robinet apă clocotită",3.0),("Baterie cu senzor",1.4),("Baterie cu duș pull-out",1.05)],FIN_BATH,[""]),
 ("unitaz","Vase WC","bath",180,55,(14,28),1.9,"Porțelan sanitar","Pardoseală / suspendat",
  [("Vas WC inteligent cu bideu",1.3),("Vas WC fără ramă",0.5),("Vas WC suspendat + rezervor",1.1),("Vas WC monobloc tankless",2.0),("Capac inteligent bideu",0.4),("Vas WC cu UV",1.4)],["alb lucios","negru mat","auriu","gri bej"],[""]),
 ("rakovina","Lavoare","bath",70,30,(14,30),2.2,"Marmură / piatră / porțelan","Pe blat / suspendat",
  [("Lavoar din marmură",1.0),("Lavoar din onix cu LED",1.7),("Lavoar din granit",0.85),("Lavoar din travertin",1.2),("Lavoar din malachit natural",2.2),("Lavoar din porțelan cu auriu",0.6),("Blat-lavoar slab",2.6)],["alb","crem","gri","negru","verde","malachit","onix verde"],[""]),
 ("polotenec","Uscătoare de prosoape","bath",80,18,(10,20),2.3,"Inox 304","Pe perete",
  [("Uscător electric cu termostat",1.0),("Uscător smart Wi-Fi",1.2),("Uscător mixt apă+electric",1.1),("Uscător panou vertical",1.5),("Uscător de design romb",1.4),("Uscător cascadă PVD",1.25)],["auriu","negru mat","crom","inox","auriu roze"],[""]),
 ("dush","Sisteme de duș","bath",110,30,(10,22),2.1,"Alamă + inox 304","Perete / încastrat",
  [("Sistem de duș termostatic",1.0),("Sistem cu LED",1.1),("Panou digital smart",1.7),("Set cu duș de igienă",1.25),("Sistem cascadă + ploaie",1.2),("Set încastrat termostatic",1.45)],["crom","negru mat","auriu","gun metal","auriu periat"],[""]),
 # ===== NOI =====
 ("cazi","Căzi de baie","bath",260,120,(20,35),1.8,"Acril sanitar / piatră","Pe pardoseală",
  [("Cadă freestanding ovală",1.0),("Cadă cu hidromasaj",1.6),("Cadă de colț",0.9),("Cadă din piatră artificială",1.8),("Cadă mini compactă",0.7),("Cadă cu LED și jacuzzi",2.0)],["alb lucios","negru mat","alb mat"],SIZES_F[1:]),
 ("cabine","Cabine de duș","bath",170,80,(18,32),1.9,"Sticlă securizată 8 mm","Pe pardoseală",
  [("Cabină glisantă fără ramă",1.0),("Cabină de colț pătrată",0.9),("Cabină walk-in",1.3),("Cabină cu hidromasaj și LED",1.9),("Paravan de duș fix",0.6),("Cabină rotundă",1.1)],["crom","negru mat","auriu"],["80 cm","90 cm","100 cm","120 cm"]),
 ("mobila_baie","Mobilier de baie","bath",120,80,(18,30),2.0,"PAL hidrofug / MDF","Suspendat / pe pardoseală",
  [("Set mobilier cu lavoar",1.4),("Dulap cu oglindă",0.8),("Comodă suspendată",1.0),("Coloană de depozitare",0.7),("Set complet cu blat marmură",2.2),("Dulap sub lavoar",0.75)],FIN_FURN,["60 cm","80 cm","100 cm","120 cm"]),
 ("oglinzi","Oglinzi","bath",45,20,(12,22),2.5,"Sticlă / aluminiu","Pe perete",
  [("Oglindă LED cu touch",1.0),("Oglindă cu dezaburire",1.3),("Oglindă rotundă cu ramă aurie",0.9),("Oglindă cu dulap",1.4),("Oglindă cu ceas și Bluetooth",1.6),("Oglindă decorativă mare",1.1)],["auriu","negru mat","argintiu","alb"],["50 cm","60 cm","80 cm","100 cm"]),
 ("mobila_buc","Mobilier de bucătărie","kitchen",220,110,(20,35),1.85,"PAL / MDF vopsit","Modular",
  [("Set bucătărie modular 2 m",1.4),("Corp suspendat",0.5),("Corp inferior cu sertare",0.7),("Insulă de bucătărie",1.8),("Dulap coloană",0.9),("Set complet cu blat",2.4)],FIN_FURN,["2 m","2.6 m","3 m"]),
 ("scaune","Scaune","kitchen",35,25,(12,24),2.4,"Lemn / metal / catifea","—",
  [("Scaun tapițat catifea",1.0),("Scaun de bar reglabil",1.1),("Scaun din lemn masiv",0.9),("Scaun ergonomic modern",1.2),("Set 2 scaune design",1.6),("Scaun metalic industrial",0.85)],["gri","bej","negru","verde smarald","albastru","nuc"],[""]),
 ("mese","Mese","kitchen",90,70,(18,30),2.0,"Lemn / sticlă / piatră","—",
  [("Masă extensibilă lemn",1.2),("Masă din sticlă securizată",1.0),("Masă cu blat de marmură",1.9),("Masă cu blat din malachit",2.6),("Masă rotundă compactă",0.8),("Masă bar înaltă",0.9),("Set masă + 4 scaune",2.2)],["stejar","nuc","alb","negru","marmură","malachit"],["120 cm","140 cm","160 cm","180 cm"]),
 ("accesorii","Accesorii","both",15,8,(7,16),2.6,"Inox / alamă","Pe perete",
  [("Set accesorii baie 6 piese",1.5),("Suport prosop dublu",0.6),("Dozator de săpun",0.5),("Etajeră de duș inox",0.8),("Suport hârtie igienică",0.5),("Cârlige decorative set",0.45),("Perie WC cu suport",0.55),("Coș de rufe design",1.2)],["auriu","negru mat","crom","inox"],[""]),
 ("malachit","Articole din malachit","both",180,40,(20,40),2.6,"Malachit natural / onix verde","Decorativ / pe blat",
  [("Lavoar din malachit",1.7),("Blat din malachit",2.4),("Vază decorativă din malachit",0.8),("Set de baie din malachit",1.5),("Placă decorativă din malachit",0.7),("Oglindă cu ramă din malachit",1.3),("Sfeșnic din malachit",0.5),("Cutie de bijuterii din malachit",0.45),("Tablou mozaic din malachit",1.1),("Blat de masă din malachit",2.2)],["verde malachit","verde regal","verde-negru","onix verde"],["","mic","mediu","mare"]),
 # ===== ОСВЕЩЕНИЕ / ЭЛЕКТРИКА =====
 ("iluminat","Corpuri de iluminat","both",30,15,(10,20),2.4,"Metal / sticlă / LED","Pe tavan / perete",
  [("Plafonieră LED",1.0),("Aplică de perete",0.8),("Corp suspendat (pendul)",1.2),("Lampă de masă",0.9),("Iluminat pentru oglindă",0.7),("Lampadar de podea",1.3)],["auriu","negru mat","crom","alb","alamă"],["","mic","mare"]),
 ("lustre","Candelabre & Lustre","both",90,40,(14,28),2.3,"Cristal / metal / LED","Pe tavan",
  [("Lustră de cristal",1.6),("Candelabru clasic",1.3),("Lustră LED modernă",1.1),("Lustră rustică",0.9),("Lustră cu abajururi",1.0),("Plafonieră mare cu cristale",1.4)],["auriu","crom","negru","cristal","alamă"],["Ø40","Ø60","Ø80","Ø100"]),
 ("becuri","Becuri LED","both",3,4,(7,14),3.0,"LED","E27 / E14 / GU10",
  [("Bec LED E27",1.0),("Bec LED E14",0.9),("Spot LED GU10",1.1),("Bec filament vintage",1.4),("Bec inteligent Wi-Fi",2.2),("Bec RGB color cu telecomandă",1.8)],["alb cald","alb rece","neutru","RGB"],["","set 4","set 10"]),
 ("prize","Prize și întrerupătoare","both",6,4,(7,14),2.8,"Policarbonat / sticlă","Încastrat",
  [("Priză simplă",1.0),("Priză dublă cu USB",1.6),("Întrerupător simplu",0.9),("Întrerupător dublu",1.1),("Priză cu capac IP44 (baie)",1.3),("Variator (dimmer)",1.5),("Ramă decorativă",0.6)],["alb","negru","auriu","sticlă neagră","argintiu"],[""]),
 ("carnize","Galerii & Carnize","both",18,12,(10,20),2.5,"Aluminiu / metal / lemn","Pe perete / tavan",
  [("Galerie dublă metalică",1.0),("Carniză de tavan",0.9),("Galerie cu inel decorativ",1.1),("Carniză electrică motorizată",2.4),("Galerie telescopică",0.8),("Carniză din lemn masiv",1.2)],["auriu","negru mat","crom","nuc","alb"],["1.5 m","2 m","2.5 m","3 m"]),
 ("benzi_led","Benzi LED","both",8,6,(7,14),2.6,"LED / silicon","Autoadeziv",
  [("Bandă LED RGB",1.2),("Bandă LED albă",1.0),("Bandă LED pentru mobilier",0.9),("Bandă LED cu senzor",1.3),("Bandă LED exterior IP65",1.4),("Kit bandă cu telecomandă",1.5)],["RGB","alb cald","alb rece","RGBW"],["3 m","5 m","10 m"]),
 ("spoturi","Spoturi & Proiectoare","both",12,8,(7,16),2.5,"Aluminiu / LED","Încastrat / aplicat",
  [("Spot LED încastrat",1.0),("Spot orientabil",1.1),("Proiector LED",1.4),("Spot pe șină",1.2),("Spot dublu",1.3),("Spot exterior IP65",1.5)],["alb","negru","auriu","crom","nichel"],["","set 3","set 6"]),
]
# счётчики на категорию — сумма 5000 (каталог отдаёт backend с пагинацией, не тормозит)
COUNTS={"smesitel":500,"kuhnya":450,"unitaz":350,"rakovina":450,"polotenec":300,"dush":400,
 "cazi":300,"cabine":280,"mobila_baie":320,"oglinzi":280,"mobila_buc":300,"scaune":280,"mese":240,"accesorii":250,"malachit":300,
 "iluminat":250,"lustre":220,"becuri":250,"prize":250,"carnize":200,"benzi_led":180,"spoturi":200}
FIN_MULT={"auriu":1.15,"auriu periat":1.12,"auriu roze":1.13,"negru mat":1.08,"gun metal":1.10,"crom":1.0,
 "inox":1.02,"alb mat":1.04,"alb lucios":1.0,"alb":1.0,"crem":1.05,"gri":1.0,"negru":1.06,"verde":1.04,
 "argintiu":1.0,"stejar":1.08,"nuc":1.12,"gri antracit":1.05,"bej cașmir":1.06,"bej":1.0,"verde smarald":1.1,
 "albastru":1.04,"marmură":1.3,"gri bej":1.03,"auriu PVD":1.15,
 "malachit":1.6,"onix verde":1.5,"verde malachit":1.6,"verde regal":1.65,"verde-negru":1.55,
 "alamă":1.12,"cristal":1.5,"alb cald":1.0,"alb rece":1.0,"neutru":1.0,"RGB":1.2,"RGBW":1.25,
 "sticlă neagră":1.15,"argintiu":1.0,"nichel":1.05}
SIZE_MULT={"":1.0,"50 cm":0.9,"60 cm":1.0,"80 cm":1.25,"90 cm":1.15,"100 cm":1.45,"120 cm":1.7,
 "140 cm":1.2,"160 cm":1.45,"180 cm":1.7,"2 m":1.0,"2.6 m":1.4,"3 m":1.5,"2.6 м":1.4,
 "mic":0.7,"mediu":1.0,"mare":1.55,"Ø40":0.9,"Ø60":1.15,"Ø80":1.4,"Ø100":1.7,
 "set 4":1.8,"set 10":3.5,"set 3":1.6,"set 6":2.8,"1.5 m":0.85,"2.5 m":1.25}
BADGES=["hot","new","","premium","limited","",""]

products=[]; supply={}; copy_cat={}; cats_meta=[]; idx=0
for cid,name,kind,base,ship,deliv,mk,mat,mount,arch,fins,sizes in CATS:
    # фото
    if POOL.get(cid): photos=POOL[cid]
    else:
        ph=f"assets/img/products/cat-{cid}.jpg"; make_ph(PIMG/f"cat-{cid}.jpg", name); photos=[ph]
    # копирайт для страницы товара
    copy_cat[cid]={"intro_ro":f"{name} premium AQUALUX — design modern, materiale durabile și finisaje de lux pentru casa ta.",
        "bullets_ro":[f"{name}: calitate premium, import direct","Materiale rezistente și finisaj impecabil","Design contemporan pentru orice interior","Garanție și suport AQUALUX","Livrare în toată Moldova"],
        "specs_labels_ro":{"material":"Material","finish":"Finisaj","mounting":"Montare","warranty":"Garanție","origin":"Origine"},
        "care_ro":"Curățați cu o lavetă moale; evitați substanțele abrazive pentru a păstra finisajul."}
    # комбинации (архетип × финиш × вариант модели × размер)
    combos=[]
    for v in VARIANTS:
        for fi in fins:
            for a in arch:
                for sz in sizes:
                    combos.append((a,fi,sz,v))
    target=COUNTS[cid]; L=len(combos); n=0; k=0
    while n<target:
        a,fin,sz,v=combos[k%L]; model=k//L; k+=1
        n+=1; idx+=1; pid=f"AQ-{idx:05d}"
        label,um=a
        nm=label+((" "+v) if v else "")+", "+fin+((" — "+sz) if sz else "")+((" · ed. "+str(model+1)) if model else "")
        cost=base*um*FIN_MULT.get(fin,1.0)*SIZE_MULT.get(sz,1.0)*VAR_MULT.get(v,1.0)*(1+0.03*model)
        sh=ship*SIZE_MULT.get(sz,1.0)
        landed=nice((cost+sh)*FX)
        retail=nice(landed*mk)
        old=nice(retail*1.25) if k%4==1 else 0
        margin=retail-landed; mpct=round(margin/retail*100) if retail else 0
        dd=deliv[0]+(k*7)%(deliv[1]-deliv[0]+1)
        badge="sale" if old else BADGES[k%len(BADGES)]
        imgs=[photos[(k+j)%len(photos)] for j in range(min(4,len(photos)))]
        products.append({"id":pid,"cat":cid,"cat_name":name,"real":True,
            "name":nm,"slug":slugify(nm)+"-"+pid.lower(),"price":retail,"old_price":old,
            "discount":(round((1-retail/old)*100) if old>retail else 0),"img":imgs[0],"images":imgs,"badge":badge,
            "rating":round(4.5+(k%5)/10,1),"reviews":8+(k*7)%90,"feat":f"{name} premium · finisaj {fin} · livrare în Moldova",
            "specs":{"Material":mat,"Finisaj":fin,"Montare":mount,"Mărime":sz or "standard","Garanție":"5 ani" if cid in("cazi","unitaz","rakovina","mobila_baie","mobila_buc") else "3 ani","Origine":"Import premium"}})
        # ПРИВАТНО
        supply[pid]={"cost_usd":round(cost,2),"ship_usd":round(sh,2),"landed_mdl":landed,
            "retail_mdl":retail,"margin_mdl":margin,"margin_pct":mpct,"delivery_days":dd}
    cats_meta.append({"id":cid,"name":name,"count":n})
    print(f"{name}: {n}")

# контент
content=json.loads((ROOT/"data/content.json").read_text(encoding="utf-8"))
content["cats"]=cats_meta
content["copy"]["category"]={**content["copy"].get("category",{}),**copy_cat}
(ROOT/"data/content.json").write_text(json.dumps(content,ensure_ascii=False),encoding="utf-8")
(ROOT/"data/products.json").write_text(json.dumps(products,ensure_ascii=False),encoding="utf-8")
(ROOT/"assets/js/data.js").write_text(
 "window.AQ_PRODUCTS="+json.dumps(products,ensure_ascii=False,separators=(",",":"))+";\n"
 "window.AQ_CONTENT="+json.dumps(content,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
# ПРИВАТНЫЙ файл (gitignored)
(ROOT/"data/supply.json").write_text(json.dumps(supply,ensure_ascii=False),encoding="utf-8")
tot_retail=sum(s["retail_mdl"] for s in supply.values())
tot_margin=sum(s["margin_mdl"] for s in supply.values())
print(f"\nВСЕГО: {len(products)} товаров, {len(cats_meta)} категорий")
print(f"Каталог (розница): {tot_retail:,} lei | потенц. маржа: {tot_margin:,} lei | средняя маржа: {round(tot_margin/tot_retail*100)}%")
print("Приватка: data/supply.json (закуп+доставка+маржа+срок) — gitignored, только локально")
