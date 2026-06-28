# -*- coding: utf-8 -*-
"""EUROMAG — генератор каталога: products.json + content.json + изображения товаров/hero."""
import os, json, math, re
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
PIMG = os.path.join(BASE, "assets", "img", "products")
HIMG = os.path.join(BASE, "assets", "img", "hero")
for d in (PIMG, HIMG): os.makedirs(d, exist_ok=True)

def load(n):
    with open(os.path.join(DATA, n), encoding="utf-8") as f: return json.load(f)
marketing = load("marketing.json"); reviews = load("reviews.json")
seo = load("seo.json"); copy = load("copy.json")

GEO  = "/System/Library/Fonts/Supplemental/Georgia.ttf"
GEOB = "/System/Library/Fonts/Supplemental/Georgia Bold.ttf"
ARI  = "/System/Library/Fonts/Supplemental/Arial.ttf"
ARIB = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
def font(p, s):
    try: return ImageFont.truetype(p, s)
    except: return ImageFont.load_default()

RATE = 80  # USD → MDL премиум-розница (с доставкой/таможней/наценкой)

# ---------- ДАННЫЕ: архетипы по категориям (RO) ----------
# (name_ro, usd, feat_ro, mount_ro[, material_ro])
CATS = [
 {"id":"smesitel","name":"Baterii pentru baie","tint":(31,26,18),
  "fin":["auriu","negru mat","crom","auriu periat","gun metal"],"target":18,"material":"Alamă masivă",
  "arch":[
   ("Baterie pentru lavoar cu senzor și afișaj LED",42,"Senzor infraroșu cu afișaj de temperatură","Pe blat"),
   ("Baterie cu efect cascadă pentru lavoar",32,"Jet tip cascadă, lat și liniștit","Pe blat"),
   ("Baterie pentru lavoar cu inserție de marmură",68,"Element decorativ din piatră naturală","Pe blat"),
   ("Baterie digitală smart cu panou tactil",130,"Panou tactil și termostat digital","Pe blat"),
   ("Baterie înaltă pentru lavoar tip vas",38,"Corp înalt pentru lavoare tip blat","Pe blat"),
   ("Baterie încastrată în perete",36,"Montaj ascuns, design minimalist","În perete"),
   ("Baterie pentru lavoar cu iluminare LED 3 culori",28,"LED alimentat de debitul apei","Pe blat"),
   ("Baterie de design cu finisaj piatră",80,"Corp cu textură de piatră naturală","Pe blat"),
   ("Baterie termostatică cu afișaj digital",88,"Termostat cu ecran și anti-opărire","Pe perete"),
   ("Baterie cu activare prin atingere (touch)",52,"Pornire/oprire la o simplă atingere","Pe blat"),
  ]},
 {"id":"unitaz","name":"Vase WC","tint":(26,24,22),
  "fin":["alb lucios","negru mat","auriu","gri bej"],"target":16,"material":"Porțelan sanitar",
  "arch":[
   ("Vas WC inteligent cu bideu și telecomandă",230,"Bideu, uscare, încălzire, telecomandă","Pe pardoseală"),
   ("Vas WC inteligent fără ramă cu capac automat",280,"Deschidere automată fără atingere","Pe pardoseală"),
   ("Vas WC suspendat fără ramă cu rezervor încastrat",210,"Rimless, soft-close, rezervor ascuns","Suspendat"),
   ("Vas WC pe pardoseală fără ramă, dublă spălare",75,"Rimless, spălare economică 3/6 l","Pe pardoseală"),
   ("Vas WC inteligent monobloc fără rezervor",390,"Încălzire instant, ecran, autosmyw","Pe pardoseală"),
   ("Capac WC inteligent electronic cu bideu",68,"Bideu, încălzire, telecomandă","Universal"),
   ("Vas WC suspendat inteligent cu bideu",330,"Suspendat cu funcții smart complete","Suspendat"),
   ("Vas WC fără ramă cu senzor de spălare",155,"Spălare automată fără atingere","Pe pardoseală"),
   ("Vas WC cu sterilizare UV și autocurățare",260,"Sterilizare UV, glazură nano","Pe pardoseală"),
   ("Vas WC de design colorat din porțelan fin",180,"Culoare mată premium, statement","Pe pardoseală"),
  ]},
 {"id":"rakovina","name":"Lavoare","tint":(28,25,20),
  "fin":["alb","crem","gri","negru"],"target":16,"material":"Piatră naturală",
  "arch":[
   ("Lavoar tip vas din marmură naturală, oval",68,"Marmură naturală, vene unice","Pe blat","Marmură naturală"),
   ("Lavoar din onix cu iluminare, rotund",120,"Onix translucid, efect backlit","Pe blat","Onix natural"),
   ("Lavoar din granit negru, dreptunghiular",58,"Granit rezistent, finisaj honed","Pe blat","Granit natural"),
   ("Lavoar din travertin lucrat manual",82,"Travertin sculptat manual","Pe blat","Travertin natural"),
   ("Lavoar din porțelan cu margine aurie, oval",40,"Porțelan fin, margine aurie","Pe blat","Porțelan fin"),
   ("Lavoar din compozit de marmură (terrazzo)",45,"Compozit ușor, calitate uniformă","Pe blat","Compozit marmură"),
   ("Lavoar dintr-un bloc de marmură, pătrat",90,"Sculptat dintr-un singur bloc","Pe blat","Marmură masivă"),
   ("Lavoar din porțelan negru mat cu scurgere aurie",38,"Porțelan fin, accente aurii","Pe blat","Porțelan fin"),
   ("Lavoar din marmură rară verde/roz, vas",105,"Marmură rară, accent exclusiv","Pe blat","Marmură naturală"),
   ("Blat-lavoar din marmură cu chiuvetă integrată",200,"Blat slab cu chiuvetă integrată","Pe blat","Marmură masivă"),
  ]},
 {"id":"polotenec","name":"Uscătoare de prosoape","tint":(27,25,21),
  "fin":["auriu","negru mat","crom","inox","auriu roze"],"target":16,"material":"Oțel inoxidabil",
  "arch":[
   ("Uscător de prosoape electric cu termostat",70,"Termostat și protecție supraîncălzire","Pe perete"),
   ("Uscător smart Wi-Fi tip scară",90,"Control din aplicație, programare","Pe perete"),
   ("Uscător mixt (apă + electric)",78,"Funcționare dublă apă/electric","Pe perete"),
   ("Uscător rotativ cu secțiuni mobile",52,"Secțiuni rotative, rezistență ascunsă","Pe perete"),
   ("Uscător de design fagure/romb",108,"Design autor, indicator LED","Pe perete"),
   ("Uscător panou vertical, suprafață mare",120,"Suprafață mare de uscare","Pe perete"),
   ("Uscător compact cu termostat",45,"Conectare ascunsă, compact","Pe perete"),
   ("Uscător smart cu ecran LCD",128,"Ecran LCD, temperatură precisă","Pe perete"),
   ("Uscător cascadă tubular cu acoperire PVD",98,"Acoperire PVD anticoroziune","Pe perete"),
   ("Uscător 2-în-1 podea/perete",105,"Montaj flexibil, ambalaj premium","Podea/perete"),
  ]},
 {"id":"dush","name":"Sisteme de duș","tint":(22,26,27),
  "fin":["crom","negru mat","auriu","gun metal","auriu periat"],"target":16,"material":"Alamă & inox",
  "arch":[
   ("Sistem de duș termostatic cu efect ploaie",95,"Cartuș termostatic, anti-opărire","Pe perete"),
   ("Sistem de duș cu iluminare LED",110,"LED după temperatura apei","Pe perete"),
   ("Panou de duș digital smart",180,"Ecran digital, presetări","Pe perete"),
   ("Sistem de duș cu duș de igienă",135,"3 funcții: sus + manual + igienă","Pe perete"),
   ("Sistem de duș cascadă + ploaie",120,"Cascadă waterfall + rain","Pe perete"),
   ("Coloană de duș cu termostat și raft",80,"Raft integrat, înălțime reglabilă","Pe perete"),
   ("Set de duș încastrat cu termostat",150,"Montaj ascuns, 2-3 ieșiri","Încastrat"),
   ("Panou de duș smart LED + Bluetooth",250,"Ecran tactil, muzică, termostat","Pe perete"),
   ("Duș tip ploaie XL Ø40 cm",128,"Pâlnie mare air-injection","Pe perete"),
   ("Sistem de duș cu duș manual 3 jeturi",75,"Duze anticalcar, jet reglabil","Pe perete"),
  ]},
 {"id":"kuhnya","name":"Baterii de bucătărie","tint":(29,24,18),
  "fin":["negru mat","crom","auriu PVD","gun metal","alb mat"],"target":18,"material":"Alamă masivă",
  "arch":[
   ("Baterie de bucătărie cu cap extractibil",26,"Furtun extensibil 360°, 2 jeturi","Pe blat"),
   ("Baterie cu braț flexibil tip arc",36,"Pull-down profesional, rotire 360°","Pe blat"),
   ("Robinet filtru 3-în-1 pentru apă potabilă",31,"Circuit separat de apă filtrată","Pe blat"),
   ("Robinet apă clocotită instant 3 căi",105,"Apă clocotită/caldă/rece, boiler","Pe blat"),
   ("Baterie de bucătărie cu senzor (touchless)",48,"Senzor infraroșu, fără atingere","Pe blat"),
   ("Baterie cu cap extractibil, finisaj PVD",40,"Pull-out, acoperire PVD","Pe blat"),
   ("Baterie cu jet cascadă",43,"Jet cascadă, finisaj premium","Pe blat"),
   ("Baterie pliabilă pentru sub fereastră",27,"Se pliază la 90°, pervaz jos","Pe blat"),
   ("Baterie cu duș pull-out și aerator",34,"2 jeturi, accente aurii","Pe blat"),
   ("Baterie cu afișaj de temperatură LED",58,"Indicator LED, termostat","Pe blat"),
  ]},
]

FIN_MULT = {"auriu":1.15,"auriu periat":1.12,"auriu PVD":1.15,"auriu roze":1.13,
 "negru mat":1.08,"gun metal":1.10,"crom":1.0,"inox":1.02,"alb mat":1.04,
 "alb lucios":1.0,"alb":1.0,"crem":1.05,"gri":1.0,"gri bej":1.03,"negru":1.06}
FIN_COLOR = {"auriu":(200,162,76),"auriu periat":(203,174,106),"auriu PVD":(200,162,76),
 "auriu roze":(217,160,122),"negru mat":(42,42,42),"gun metal":(91,96,104),"crom":(207,212,216),
 "inox":(195,200,204),"alb mat":(236,234,229),"alb lucios":(243,241,236),"alb":(240,238,233),
 "crem":(232,221,200),"gri":(184,188,192),"gri bej":(207,198,180),"negru":(42,42,42),"verde":(95,122,99)}

def nice(v):
    v = int(round(v))
    return int(round(v/10)*10) if v < 1000 else int(round(v/50)*50)

def slugify(s):
    tr = str.maketrans("ăâîșțĂÂÎȘȚ","aaistAAIST")
    s = s.translate(tr).lower()
    return re.sub(r"-+","-", re.sub(r"[^a-z0-9]+","-", s)).strip("-")

# ---------- ИЗОБРАЖЕНИЯ ----------
S = 760
def droplet(d, cx, cy, r, color, w=4):
    d.pieslice([cx-r, cy-r+int(r*0.25), cx+r, cy+r], 30, 150, outline=color, width=w)
    d.polygon([(cx, cy-int(r*1.15)),(cx-int(r*0.74), cy+int(r*0.30)),(cx+int(r*0.74), cy+int(r*0.30))],
              outline=color)
    # обвести верх линиями
    d.line([(cx, cy-int(r*1.15)),(cx-int(r*0.74), cy+int(r*0.30))], fill=color, width=w)
    d.line([(cx, cy-int(r*1.15)),(cx+int(r*0.74), cy+int(r*0.30))], fill=color, width=w)

def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur+" "+wd).strip()
        if d.textlength(t, font=f) <= maxw: cur = t
        else: lines.append(cur); cur = wd
    if cur: lines.append(cur)
    return lines

def make_img(path, cat_name, name, finish, sku, tint):
    img = Image.new("RGB",(S,S), tint)
    d = ImageDraw.Draw(img)
    for y in range(S):
        t=y/S; k=1-0.45*t
        d.line([(0,y),(S,y)], fill=(int(tint[0]*k+6),int(tint[1]*k+5),int(tint[2]*k+4)))
    GOLD=(200,162,76); GOLDL=(227,200,121); MUT=(150,138,114)
    d.rectangle([18,18,S-18,S-18], outline=(74,61,40), width=2)
    d.rectangle([30,30,S-30,S-30], outline=(111,90,52), width=1)
    fb=font(GEOB,30); fc=font(ARIB,16); fn=font(GEO,27); ff=font(ARIB,18); fs=font(ARI,15)
    # brand
    s="EUROMAG"; d.text(((S-d.textlength(s,font=fb))/2,52), s, font=fb, fill=GOLDL)
    sp=font(ARI,12); s2="·  MAGAZIN UNIVERSAL  ·"
    d.text(((S-d.textlength(s2,font=sp))/2,96), s2, font=sp, fill=MUT)
    d.line([(S/2-70,120),(S/2+70,120)], fill=GOLD, width=1)
    # medallion + droplet (finish-colored ring)
    fcol=FIN_COLOR.get(finish,GOLD); cx,cy=S//2,300
    d.ellipse([cx-118,cy-118,cx+118,cy+118], outline=GOLD, width=2)
    d.ellipse([cx-104,cy-104,cx+104,cy+104], outline=fcol, width=4)
    droplet(d, cx, cy-6, 56, GOLDL, 4)
    # category
    s=cat_name.upper(); d.text(((S-d.textlength(s,font=fc))/2,438), s, font=fc, fill=GOLD)
    # name (wrap)
    y=474
    for ln in wrap(d, name, fn, S-150)[:3]:
        d.text(((S-d.textlength(ln,font=fn))/2,y), ln, font=fn, fill=(224,214,194)); y+=34
    # finish swatch + label
    y=min(y+6, 612)
    lbl=f"Finisaj: {finish}"; tw=d.textlength(lbl,font=ff); sw=18
    x0=(S-(tw+sw+10))/2
    d.ellipse([x0,y+1,x0+sw,y+1+sw], fill=fcol, outline=(90,78,54))
    d.text((x0+sw+10,y), lbl, font=ff, fill=GOLDL)
    # footer
    s=f"Foto demo · {sku}  ·  înlocuiește cu fotografia furnizorului"
    d.text(((S-d.textlength(s,font=fs))/2,S-58), s, font=fs, fill=(120,108,86))
    img.save(path,"JPEG",quality=86)

def make_hero(path, tint, accent):
    W,H=1640,780; img=Image.new("RGB",(W,H),tint); d=ImageDraw.Draw(img)
    for y in range(H):
        t=y/H; k=1-0.4*t
        d.line([(0,y),(W,y)], fill=(int(tint[0]*k+8),int(tint[1]*k+6),int(tint[2]*k+4)))
    GOLD=(200,162,76)
    # большая бледная капля справа
    droplet(d, int(W*0.8), int(H*0.5), 230, (int(accent[0]*0.5),int(accent[1]*0.5),int(accent[2]*0.5)), 3)
    d.ellipse([int(W*0.8)-300,int(H*0.5)-300,int(W*0.8)+300,int(H*0.5)+300], outline=(70,58,38), width=2)
    img.save(path,"JPEG",quality=84)

# ---------- ГЕНЕРАЦИЯ ТОВАРОВ ----------
products=[]; cats_meta=[]
for c in CATS:
    arch, fins, target = c["arch"], c["fin"], c["target"]
    combos=[(a, fins[0]) for a in arch]
    for fi in fins[1:]:
        for a in arch: combos.append((a, fi))
    combos=combos[:target]
    n=0
    for idx,(a,finish) in enumerate(combos):
        n+=1; sku=f"{c['id']}-{n:02d}"
        name = a[0]
        usd  = a[1]; feat=a[2]; mount=a[3]
        material = a[4] if len(a)>4 else c["material"]
        full = f"{name}, {finish}"
        price = nice(usd*RATE*FIN_MULT.get(finish,1.0))
        # скидка на части товаров
        disc = 0; old=0
        if idx%3==1: disc = 15 + (idx*7)%16; old = nice(price/(1-disc/100))
        # бейдж
        if disc: badge="sale"
        elif idx<2: badge="hot"
        elif idx%7==3: badge="new"
        elif idx%9==4: badge="limited"
        else: badge=""
        rating = round(4.5 + ((idx*13)%5)/10.0, 1); rating=min(rating,5.0)
        revc = 8 + (idx*17)%55
        warranty = "5 ani" if usd>=80 else "3 ani"
        make_img(os.path.join(PIMG, sku+".jpg"), c["name"], name, finish, sku, c["tint"])
        products.append({
          "id":sku,"cat":c["id"],"cat_name":c["name"],
          "name":full,"slug":slugify(full)+"-"+sku,
          "price":price,"old_price":old,"discount":disc,
          "img":f"assets/img/products/{sku}.jpg",
          "badge":badge,"rating":rating,"reviews":revc,
          "feat":feat,
          "specs":{"Material":material,"Finisaj":finish,"Montare":mount,
                   "Garanție":warranty,"Origine":"Import premium"}
        })
    cats_meta.append({"id":c["id"],"name":c["name"],"count":target})

# hero images
make_hero(os.path.join(HIMG,"hero1.jpg"),(20,17,12),(200,162,76))
make_hero(os.path.join(HIMG,"hero2.jpg"),(22,24,26),(120,150,160))
make_hero(os.path.join(HIMG,"hero3.jpg"),(26,22,18),(180,140,90))

# ---------- ЗАПИСЬ ----------
with open(os.path.join(DATA,"products.json"),"w",encoding="utf-8") as f:
    json.dump(products, f, ensure_ascii=False)

content = {
 "brand":"EUROMAG","city":"Chișinău","currency":"lei","free_delivery":3000,
 "phone":"+373 60 000 000","whatsapp":"37360000000","email":"comenzi@euromag.md",
 "address":"Chișinău, bd. Ștefan cel Mare 1",
 "cats":cats_meta,"marketing":marketing,"reviews":reviews,"seo":seo,"copy":copy
}
with open(os.path.join(DATA,"content.json"),"w",encoding="utf-8") as f:
    json.dump(content, f, ensure_ascii=False)

print(f"Товаров: {len(products)}  |  изображений: {len(products)+3}")
print("Категории:", ", ".join(f"{m['name']}={m['count']}" for m in cats_meta))
