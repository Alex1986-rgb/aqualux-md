# -*- coding: utf-8 -*-
import os, json
BASE=os.path.dirname(os.path.abspath(__file__))
seo=json.load(open(os.path.join(BASE,"data","seo.json"),encoding="utf-8"))
prods=json.load(open(os.path.join(BASE,"data","products.json"),encoding="utf-8"))
KW=", ".join(seo["keywords"][:14])
SITE="https://alex1986-rgb.github.io/aqualux-md/"

HEAD="""<!DOCTYPE html><html lang="ro"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="keywords" content="{kw}">
<meta name="robots" content="index,follow">
<link rel="canonical" href="{site}{file}">
<meta property="og:type" content="website"><meta property="og:locale" content="ro_MD">
<meta property="og:site_name" content="EUROMAG">
<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}">
<meta property="og:image" content="{site}assets/img/hero/hero1.jpg">
<meta property="og:url" content="{site}{file}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}"><meta name="twitter:description" content="{desc}">
<meta name="twitter:image" content="{site}assets/img/hero/hero1.jpg">
<link rel="manifest" href="manifest.json">
<meta name="theme-color" content="#16130e">
<link rel="stylesheet" href="assets/css/style.css">
<script type="application/ld+json">{org}</script>
</head><body data-page="{page}"{extra}>
<div id="site-header"></div>
<main id="{root}"></main>
<div id="site-footer"></div>
<script src="assets/js/config.js"></script>
<script src="assets/js/data.js"></script>
<script src="assets/js/site.js"></script>
</body></html>"""

ORG=json.dumps({"@context":"https://schema.org","@type":"Store","name":"EUROMAG","image":SITE+"assets/img/hero/hero1.jpg",
 "description":"Magazin online universal în Moldova — mii de produse cu livrare în toată țara.","url":SITE,"telephone":"+37360000000",
 "address":{"@type":"PostalAddress","addressLocality":"Ialoveni","addressCountry":"MD","streetAddress":"str. Alexandru cel Bun 45"},
 "priceRange":"$$$"},ensure_ascii=False)

PAGES=[
 ("index.html","home","home",seo["pages"]["home"],""),
 ("catalog.html","catalog","catalog",seo["pages"]["catalog"],""),
 ("produs.html","product","product",{"title":"Produs premium | EUROMAG Chișinău","description":seo["pages"]["catalog"]["description"]},""),
 ("cos.html","cart","cart",{"title":"Coș de cumpărături | EUROMAG","description":"Coșul tău de cumpărături EUROMAG — magazin universal cu livrare în Moldova."},""),
 ("checkout.html","checkout","checkout",{"title":"Finalizare comandă | EUROMAG","description":"Finalizează comanda EUROMAG: livrare în toată Moldova, ramburs, card sau transfer."},""),
 ("despre.html","info","info",seo["pages"]["despre"],' data-info="despre"'),
 ("livrare.html","info","info",{"title":"Livrare & Plată | EUROMAG Moldova","description":"Condiții de livrare și plată EUROMAG: curier în toată Moldova, ramburs, card, transfer bancar."},' data-info="livrare"'),
 ("garantie.html","info","info",{"title":"Garanție & Retur | EUROMAG","description":"Politica de garanție și retur EUROMAG: 14 zile retur, garanție oficială producător."},' data-info="garantie"'),
 ("contacte.html","contacts","contacts",seo["pages"]["contacte"],""),
]
for file,page,root,meta,extra in PAGES:
    html=HEAD.format(title=meta["title"].replace('"',"'"),desc=meta["description"].replace('"',"'"),
        kw=KW,site=SITE,file=file,page=page,root=root,extra=extra,org=ORG)
    open(os.path.join(BASE,file),"w",encoding="utf-8").write(html)

# robots.txt
open(os.path.join(BASE,"robots.txt"),"w").write("User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n"%SITE)

# sitemap.xml
urls=[("","1.0"),("catalog.html","0.9"),("despre.html","0.6"),("livrare.html","0.6"),("garantie.html","0.5"),("contacte.html","0.6")]
import urllib.parse as _up
_cats=json.load(open(os.path.join(BASE,"data","content.json"),encoding="utf-8"))["cats"]
urls+=[("catalog.html?cat=%s"%c["id"],"0.75") for c in _cats if c.get("count")]
urls+=[("catalog.html?group=%s"%_up.quote(g),"0.8") for g in sorted(set(c.get("group","") for c in _cats if c.get("group")))]
urls+=[("produs.html?id=%s"%p["id"],"0.7") for p in prods]
sm='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
for u,pr in urls:
    sm+='  <url><loc>%s%s</loc><changefreq>weekly</changefreq><priority>%s</priority></url>\n'%(SITE,u.replace("&","&amp;"),pr)
sm+='</urlset>\n'
open(os.path.join(BASE,"sitemap.xml"),"w",encoding="utf-8").write(sm)
print("Страниц:",len(PAGES),"| sitemap URL:",len(urls),"| robots.txt OK")
