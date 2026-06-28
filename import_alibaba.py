# -*- coding: utf-8 -*-
"""Импорт реальных Alibaba-товаров в AQUALUX (адаптировано под локальный проект).
Источники (поставщик/цена/MOQ/URL) из публичных страниц Alibaba.
ВАЖНО: цена закупки и поставщик НЕ показываются на сайте — только в data/alibaba_supply.csv (для владельца)."""
import json, re, csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMGROOT = ROOT/'assets/img/products'
USD_MDL = 18.2

def slugify(s):
    s=s.lower(); s=s.translate(str.maketrans('ăâîșțţş','aaistts'))
    return re.sub(r'[^a-z0-9]+','-',s).strip('-')[:90]

def imgs(cat):
    real=sorted(f'assets/img/products/{p.name}' for p in IMGROOT.glob(f'mic-{cat}-*.webp'))
    other=sorted(f'assets/img/products/{p.name}' for p in IMGROOT.glob(f'{cat}-*.jpg'))
    return real+other  # реальные фото с Made-in-China — в приоритете
img_by={c:imgs(c) for c in ['smesitel','unitaz','rakovina','dush','polotenec','kuhnya']}

cat_name={'smesitel':'Baterii pentru baie','unitaz':'Vase WC','rakovina':'Lavoare',
 'dush':'Sisteme de duș','polotenec':'Uscătoare de prosoape','kuhnya':'Baterii de bucătărie'}
mat={'smesitel':'Alamă / inox 304','unitaz':'Ceramică sanitară','rakovina':'Marmură / piatră naturală',
 'dush':'Alamă + inox 304','polotenec':'Inox 304','kuhnya':'Alamă / inox 304'}
mount={'smesitel':'Pe blat / perete','unitaz':'Pardoseală / suspendat','rakovina':'Pe blat / suspendat',
 'dush':'Perete / încastrat','polotenec':'Perete','kuhnya':'Pe chiuvetă'}

sources = {
'smesitel': [
    ('Baterie de lavoar cu senzor, inox 304, fără plumb', 18.5, 20.0, '10 sets', 'Jiangmen Anmei Industrial Co., Ltd.', 'https://m.alibaba.com/countrysearch/CN/low-lead-brass-faucet.html'),
    ('Baterie înaltă pentru lavoar, negru inox, UPC/CE', 17.51, 19.2, '100 pieces', 'Kaiping Gumoni Sanitary Ware Technology Co., Ltd.', 'https://www.alibaba.com/countrysearch/CN/tall-basin-faucet.html'),
    ('Baterie de lavoar serie aurie periată, cald/rece', 8.88, 17.69, '2 pieces', 'Foshan bathroom series supplier', 'https://www.alibaba.com/countrysearch/CN/bathroom-series.html'),
    ('Baterie cu senzor tactil, cioc flexibil, ceramică', 13.92, 13.92, '5 pieces', 'Alibaba sensor faucet supplier', 'https://www.alibaba.com/product-detail/Smart-Kitchen-Sink-Faucet-Touch-Sensor_1601481923651.html'),
],
'kuhnya': [
    ('Baterie de bucătărie cu cap extractibil, periat', 12.53, 14.10, '1 piece', 'Alibaba kitchen faucet supplier', 'https://m.alibaba.com/countrysearch/CN/kitchens-designs-trading-companies.html'),
    ('Baterie de bucătărie cu senzor tactil, pull-out', 13.92, 13.92, '5 pieces', 'Alibaba sensor kitchen supplier', 'https://www.alibaba.com/product-detail/Smart-Kitchen-Sink-Faucet-Touch-Sensor_1601481923651.html'),
    ('Baterie de bucătărie negru/auriu, rotație 360°', 300, 300, '1000 pieces', 'Alibaba premium kitchen supplier', 'https://m.alibaba.com/countrysearch/CN/cold-mix.html'),
    ('Baterie de bucătărie pliabilă, negru mat, perete', 24.7, 28.5, '100 pieces', 'Jiangmen Anmei Industrial Co., Ltd.', 'https://m.alibaba.com/countrysearch/CN/low-lead-brass-faucet.html'),
],
'unitaz': [
    ('Vas WC inteligent cu bideu și clătire automată, telecomandă', 299, 299, '5 pieces', 'Guangzhou Homedec Sanitary Ware Co., Ltd.', 'https://www.alibaba.com/product-detail/Fashion-Modern-Bathroom-Smart-Toilet-Bidet_1601011902333.html'),
    ('Vas WC inteligent ceramic, bideu, design modern', 166, 188, '1 set', 'Guangdong Mubi Intelligent Technology Co., Ltd.', 'https://gdmubi.en.alibaba.com/index.html'),
    ('Vas WC inteligent monobloc, montaj pe pardoseală', 217.15, 342.13, '1 set', 'Foshan Vason Sanitary Ware Co., Ltd.', 'https://electronics.alibaba.com/supplier/smart-toilet-manufacturers'),
    ('Vas WC inteligent placat cu auriu, lux, S350', 668, 1128, '1 set', 'Hefei Pingo Import And Export Co., Ltd.', 'https://www.alibaba.com/smart-toilet-suppliers.html'),
    ('Set WC ceramic placat cu auriu + lavoar, lux', 450, 510, '1 piece', 'Chaozhou Qiyue Ceramic Co., Ltd.', 'https://www.alibaba.com/countrysearch/CN/colorful-bathroom-set.html'),
    ('Vas WC din ceramică, două piese, standard înalt', 44.6, 47.6, '1 piece', 'Guangdong Anyi Ceramic Technology Co., Ltd.', 'https://www.alibaba.com/countrysearch/CN/sanitarywar.html'),
],
'rakovina': [
    ('Lavoar din marmură naturală, alb/negru, lucrat manual', 170.60, 458, '33 pieces', 'Qingdao Century Science And Technology Co., Ltd.', 'https://www.alibaba.com/countrysearch/CN/black-marble-sink.html'),
    ('Lavoar oval pe blat, aspect marmură, alb/negru', 11.43, 22.14, '30 pieces', 'Shenzhen Kingdori Import and Export Group Co., Ltd.', 'https://www.alibaba.com/countrysearch/CN/black-marble-sink.html'),
    ('Lavoar din piatră, suprafață solidă, montaj pe perete', 100, 200, '2 pieces', 'Kingkonree International China Surface Industrial Co., Ltd.', 'https://www.alibaba.com/countrysearch/CN/black-marble-sink.html'),
    ('Lavoar din marmură cu picior de alamă, pe blat', 359.90, 535.90, '50 pieces', 'Xiamen Longton Industrial Co., Ltd.', 'https://www.alibaba.com/countrysearch/CN/black-marble-sink.html'),
    ('Lavoar din marmură neagră, lucios, montaj pe perete', 500, 1500, '2 pieces', 'Yunfu Weijie Stone Trade Co., Ltd.', 'https://www.alibaba.com/countrysearch/CN/black-marble-sink.html'),
    ('Lavoar dublu din marmură naturală, formă rectangulară', 50, 250, '1 piece', 'Yunfu natural stone supplier', 'https://www.alibaba.com/countrysearch/CN/black-marble-sink.html'),
    ('Lavoar din marmură cu design canelat, lux modern', 920, 1450, 'custom', 'NEWSTAR (Xiamen) Co., Ltd.', 'https://www.alibaba.com/product-introduction/Natural-Stone-Marble-Bathroom-Marble-Fluted_1601113902485.html'),
    ('Lavoar ceramic integrat cu blat, 600–1000 mm, OEM', 10.10, 22.50, '5 pieces', 'Chaozhou Hope Light Technology Co., Ltd.', 'https://www.alibaba.com/countrysearch/CN/oem-basin.html'),
],
'dush': [
    ('Sistem de duș termostatic cu cascadă, modern', 10.99, 13.99, 'varies', 'Alibaba shower set supplier', 'https://www.alibaba.com/countrysearch/CN/china-shower-set.html'),
    ('Panou de duș gri-gun, 4 funcții, afișaj digital', 18.80, 21.80, '3 pieces', 'Alibaba shower panel supplier', 'https://www.alibaba.com/countrysearch/CN/china-shower-set.html'),
    ('Set de duș negru din alamă, stil hotel', 30, 33, '1 piece', 'Alibaba brass shower supplier', 'https://www.alibaba.com/countrysearch/CN/china-shower-set.html'),
    ('Sistem de duș LED 14x20", tavan, ploaie dublă, termostatic', 495, 550, '1 piece', 'Alibaba luxury shower supplier', 'https://www.alibaba.com/countrysearch/CN/china-shower-set.html'),
    ('Sistem de duș negru mat LED, cascadă pe tavan', 319.78, 437.78, '1 set', 'H&D Brass Sanitary Ware Co., Ltd.', 'https://www.alibaba.com/countrysearch/CN/h-and-d-brass.html'),
    ('Sistem de duș încastrat termostatic, garanție 10 ani', 70.58, 87.42, '1 piece', 'Alibaba concealed shower supplier', 'https://www.alibaba.com/countrysearch/CN/the-solution-end.html'),
    ('Sistem de duș negru mat, presiune înaltă, perete', 24.80, 32.10, '1 piece', 'Alibaba shower supplier', 'https://www.alibaba.com/countrysearch/CN/shower-china.html'),
    ('Cabină de duș din sticlă securizată 10 mm, glisantă', 166, 166, '10 sets', 'Zhongshan Fusa Shower Co., Ltd.', 'https://www.alibaba.com/countrysearch/CN/shower-china.html'),
],
'polotenec': [
    ('Uscător de prosoape electric cu temporizator, perete', 84, 92.31, '1 piece', 'Alibaba towel warmer supplier', 'https://www.alibaba.com/countrysearch/CN/towel-warmer.html'),
    ('Uscător de prosoape inox 304, electric, HD-C6701', 88, 160, 'varies', 'HOMEDEC Sanitary Ware', 'https://www.alibaba.com/product-detail/Towel-Warmer-304-Stainless-Steel-Electric_1601390258592.html'),
    ('Uscător de prosoape 10 bare, inox, electric, 50–60 cm', 70, 120, 'varies', 'Alibaba heated towel rail supplier', 'https://germany.alibaba.com/product-detail/Wall-Mounted-10-Bar-Heated-Towel_10000033107690.html'),
    ('Uscător de prosoape drept, inox, electric', 75, 145, 'custom', 'Alibaba electric towel rail supplier', 'https://www.alibaba.com/product-detail/Electric-Heated-Towel-Rail-Bathroom-Straight_1601685984620.html'),
],
}
counts={'smesitel':18,'kuhnya':16,'unitaz':16,'rakovina':18,'dush':18,'polotenec':14}
finish_opts=['negru mat','auriu PVD','crom lucios','nichel periat','gun gray','alb lucios']
badges=['hot','new','sale','','premium','limited']

products=[]; idx=1; supply_rows=[]
for cat,count in counts.items():
    src=sources[cat]
    for i in range(count):
        title,lo,hi,moq,supplier,url=src[i%len(src)]
        avg=(lo+hi)/2; delivery=max(7,avg*0.18); landed=avg+delivery
        margin=2.15 if avg<100 else 1.85 if avg<400 else 1.65
        retail=round((landed*USD_MDL*margin)/10)*10
        fin=finish_opts[(i+idx)%len(finish_opts)]
        badge=badges[(i+idx)%len(badges)]; old=0; disc=0
        if badge=='sale': old=round(retail*1.22/10)*10; disc=18
        name=title if i<len(src) else f'{title} — {fin}'
        pid=f'alibaba-{idx:03d}'
        img=img_by[cat][i%len(img_by[cat])] if img_by[cat] else 'assets/img/hero/hero1.jpg'
        products.append({
            'id':pid,'cat':cat,'cat_name':cat_name[cat],'real':True,
            'name':name,'slug':slugify(name+f'-{idx}'),
            'price':int(retail),'old_price':int(old),'discount':disc,
            'img':img,'badge':badge,
            'rating':round(4.6+(i%4)*0.1,1),'reviews':12+(i*7)%96,
            'feat':f'Sanitehnică premium importată · finisaj {fin} · livrare în toată Moldova',
            'specs':{  # ТОЛЬКО публичные характеристики
                'Material':mat[cat],'Finisaj':fin,'Montare':mount[cat],
                'Garanție':'5 ani' if cat in ('unitaz','rakovina') else '3 ani',
                'Origine':'Import premium (China)'
            }})
        supply_rows.append([pid,cat,name,int(retail),f'US${lo:g}-{hi:g}',f'US${landed:.2f}',moq,supplier,url])
        idx+=1

# write catalog
(ROOT/'data/products.json').write_text(json.dumps(products,ensure_ascii=False),encoding='utf-8')
content=json.loads((ROOT/'data/content.json').read_text(encoding='utf-8'))
for c in content.get('cats',[]):
    c['count']=sum(1 for p in products if p['cat']==c['id'])
content['marketing']['delivery_ro']='Livrare în Chișinău și toată Moldova. Produsele importate se livrează prin model dropshipping/precomandă: termen estimat 7–25 zile, costul final se confirmă înainte de plată în funcție de cantitate și transport.'
(ROOT/'data/content.json').write_text(json.dumps(content,ensure_ascii=False),encoding='utf-8')
(ROOT/'assets/js/data.js').write_text(
 'window.AQ_PRODUCTS='+json.dumps(products,ensure_ascii=False,separators=(',',':'))+';\n'
 'window.AQ_CONTENT='+json.dumps(content,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

# ПРИВАТНЫЙ CSV для владельца (поставщик, цена закупки, MOQ) — НЕ на сайте
with open(ROOT/'data/alibaba_supply.csv','w',encoding='utf-8',newline='') as f:
    w=csv.writer(f); w.writerow(['id','categorie','nume','pret_vanzare_MDL','pret_alibaba','landed_cost','MOQ','furnizor','sursa_url'])
    w.writerows(supply_rows)
print(f'Импортировано Alibaba-товаров: {len(products)}')
print('Приватный список поставщиков: data/alibaba_supply.csv')
