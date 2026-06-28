/* ===== AQUALUX storefront engine ===== */
(function(){
"use strict";
const C = window.AQ_CONTENT, P = window.AQ_PRODUCTS;
const API = (window.AQ_API || "").replace(/\/$/, "");   // headless backend (опц.)
const PCACHE = {};                                       // кэш карточек (для корзины из API)
const CART_KEY = "aqualux_cart_v1";
const FREE = C.free_delivery, DELIV = 200, CITIES = ["Chișinău","Bălți","Cahul","Orhei","Ungheni","Comrat","Soroca","Edineț","Hîncești","Strășeni","Căușeni","Drochia"];
const ICON = {
 cart:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="9" cy="20" r="1.4"/><circle cx="18" cy="20" r="1.4"/><path d="M2 3h2.2l2.3 12.2a1.5 1.5 0 0 0 1.5 1.2h8.6a1.5 1.5 0 0 0 1.5-1.2L21 7H6"/></svg>',
 search:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4-4"/></svg>',
 heart:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M12 21s-7-4.6-9.3-9C1.2 9 2.5 5.5 6 5.5c2 0 3.2 1.2 4 2.3.8-1.1 2-2.3 4-2.3 3.5 0 4.8 3.5 3.3 6.5C19 16.4 12 21 12 21z"/></svg>',
 user:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-6 8-6s8 2 8 6"/></svg>',
 phone:'<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3 19.5 19.5 0 0 1-6-6 19.8 19.8 0 0 1-3-8.6A2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 2 .7 2.9a2 2 0 0 1-.5 2.1L8.1 9.9a16 16 0 0 0 6 6l1.2-1.2a2 2 0 0 1 2.1-.5c.9.3 1.9.6 2.9.7a2 2 0 0 1 1.7 2z"/></svg>'
};
const CICON = {smesitel:"01",unitaz:"02",rakovina:"03",polotenec:"04",dush:"05",kuhnya:"06"};

/* ---------- helpers ---------- */
const $ = (s,r=document)=>r.querySelector(s);
const $$ = (s,r=document)=>Array.from(r.querySelectorAll(s));
const esc = s => (s||"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const money = n => Number(n).toString().replace(/\B(?=(\d{3})+(?!\d))/g," ")+" lei";
const stars = r => {const f=Math.round(r);return "★".repeat(f)+"☆".repeat(5-f);};
const pById = id => P.find(p=>p.id===id);
const param = k => new URLSearchParams(location.search).get(k);
function getCart(){try{return JSON.parse(localStorage.getItem(CART_KEY))||{};}catch(e){return {};}}
function saveCart(c){localStorage.setItem(CART_KEY,JSON.stringify(c));updateCartCount();}
function cartCount(){return Object.values(getCart()).reduce((a,b)=>a+b,0);}
function snaps(){try{return JSON.parse(localStorage.getItem("aqualux_snap"))||{};}catch(e){return {};}}
function saveSnap(p){if(!p)return;const s=snaps();s[p.id]={id:p.id,name:p.name,price:p.price,img:p.img,cat:p.cat,cat_name:p.cat_name,specs:p.specs,feat:p.feat,rating:p.rating,reviews:p.reviews,old_price:p.old_price,discount:p.discount};localStorage.setItem("aqualux_snap",JSON.stringify(s));}
function resolve(id){return pById(id)||PCACHE[id]||snaps()[id]||null;}
function cartItems(){const c=getCart();return Object.keys(c).map(id=>({p:resolve(id),q:c[id]})).filter(x=>x.p);}
function cartSub(){return cartItems().reduce((s,x)=>s+x.p.price*x.q,0);}
function addToCart(id,q=1){const c=getCart();c[id]=(c[id]||0)+q;saveCart(c);saveSnap(PCACHE[id]||pById(id));toast("Adăugat în coș ✓");}
function setQty(id,q){const c=getCart();if(q<=0)delete c[id];else c[id]=q;saveCart(c);}
function updateCartCount(){const n=cartCount();$$(".cart-count").forEach(e=>{e.textContent=n;e.style.display=n?"flex":"none";});}
let toastT;function toast(m){let t=$("#toast");if(!t){t=document.createElement("div");t.id="toast";t.className="toast";document.body.appendChild(t);}t.textContent=m;t.classList.add("show");clearTimeout(toastT);toastT=setTimeout(()=>t.classList.remove("show"),2200);}
function discPct(p){return p.discount?p.discount:(p.old_price?Math.round((1-p.price/p.old_price)*100):0);}

/* ---------- product card ---------- */
function card(p){
 PCACHE[p.id]=p;
 const b=p.badge?`<div class="badges"><span class="bdg ${p.badge}">${esc(C.copy.badges_ro[p.badge]||"")}${p.badge==="sale"?" -"+discPct(p)+"%":""}</span></div>`:"";
 const old=p.old_price?`<span class="old">${money(p.old_price)}</span><span class="disc">-${discPct(p)}%</span>`:"";
 return `<div class="pcard">
   <a class="pimg" href="produs.html?id=${p.id}"><img src="${p.img}" alt="${esc(p.name)}" loading="lazy">${b}</a>
   <button class="wish" title="Favorite">${ICON.heart}</button>
   <div class="pb">
     <span class="cat">${esc(p.cat_name)}</span>
     <a class="pn" href="produs.html?id=${p.id}">${esc(p.name)}</a>
     <div class="stars">${stars(p.rating)} <small>(${p.reviews})</small></div>
     <div class="price"><span class="now">${money(p.price)}</span>${old}</div>
     <div class="add"><button class="btn btn-gold" data-add="${p.id}">${esc(C.copy.add_to_cart_ro)}</button></div>
   </div></div>`;
}
function rowOf(list){return `<div class="crow"><button class="car prev">‹</button><div class="ctrack">${list.map(card).join("")}</div><button class="car next">›</button></div>`;}

/* ---------- header / footer / fab ---------- */
function buildHeader(){
 const navItems = C.cats.map(c=>`<a href="catalog.html?cat=${c.id}">${esc(c.name)}</a>`).join("");
 const h=`<div class="topbar"><div class="wrap">
    <div>${ICON.phone.replace('<svg','<svg style="width:13px;height:13px;display:inline;vertical-align:-2px"')} <a href="tel:${C.phone.replace(/ /g,'')}">${C.phone}</a> · ${esc(C.address)}</div>
    <div class="tb-r"><span>${esc(C.copy.delivery_badge_ro)}</span><span class="lang">Limba: <b>RO</b> / RU</span></div>
  </div></div>
  <header class="hdr"><div class="wrap hdr-main">
    <a class="logo" href="index.html"><span class="dot">A</span><span>AQUALUX<small>SANITEHNICĂ PREMIUM</small></span></a>
    <form class="search" onsubmit="location.href='catalog.html?q='+encodeURIComponent(this.q.value);return false;">
      <input name="q" placeholder="Caută: baterie, vas WC, lavoar marmură…" value="${esc(param('q')||'')}">
      <button type="submit">${ICON.search}</button>
    </form>
    <div class="hdr-icons">
      <a class="hicon" href="contacte.html">${ICON.user}<span>Cont</span></a>
      <a class="hicon" href="cos.html">${ICON.cart}<span class="cart-count">0</span><span>Coș</span></a>
    </div>
  </div></header>
  <nav class="nav"><div class="wrap"><a class="all" href="catalog.html">Toate produsele</a>${navItems}<a href="livrare.html">Livrare</a><a href="despre.html">Despre</a><a href="contacte.html">Contacte</a></div></nav>`;
 const el=$("#site-header"); if(el) el.innerHTML=h;
 const cur=document.body.dataset.cat;
 if(cur) $$(".nav a").forEach(a=>{if(a.getAttribute("href").includes("cat="+cur))a.classList.add("active");});
}
function buildFooter(){
 const m=C.marketing, cats=C.cats.map(c=>`<a href="catalog.html?cat=${c.id}">${esc(c.name)}</a>`).join("");
 const h=`<footer class="ftr"><div class="wrap"><div class="ftr-cols">
   <div><div class="logo" style="font-family:Georgia,serif;font-size:24px;font-weight:700">AQUALUX<small style="display:block;font-family:Arial;font-size:9px;letter-spacing:3px">SANITEHNICĂ PREMIUM</small></div>
     <p style="font-size:13px;max-width:260px">${esc(m.footer_blurb_ro)}</p>
     <div class="pays"><span>Ramburs</span><span>Card / Visa</span><span>Mastercard</span><span>Transfer</span></div></div>
   <div><h4>Catalog</h4>${cats}</div>
   <div><h4>Informații</h4><a href="despre.html">Despre noi</a><a href="livrare.html">Livrare & plată</a><a href="garantie.html">Garanție & retur</a><a href="contacte.html">Contacte</a></div>
   <div><h4>Contacte</h4><a href="tel:${C.phone.replace(/ /g,'')}">${C.phone}</a><a href="mailto:${C.email}">${C.email}</a><p style="font-size:13px;margin:8px 0">${esc(C.address)}</p><p style="font-size:12px;color:#9b917c">Luni–Vineri 09:00–18:00<br>Sâmbătă 10:00–15:00</p></div>
 </div><div class="ftr-bot"><span>© 2026 AQUALUX Moldova. Toate drepturile rezervate.</span><span>Import direct · Dropshipping · Chișinău</span></div></div></footer>`;
 const el=$("#site-footer"); if(el) el.innerHTML=h;
}
function buildFab(){const d=document.createElement("div");d.className="fab";
 d.innerHTML=`<a class="wa" href="https://wa.me/${C.whatsapp}" target="_blank" title="WhatsApp"><svg viewBox="0 0 24 24" width="24" height="24" fill="currentColor"><path d="M12 2a10 10 0 0 0-8.6 15l-1.3 4.7 4.8-1.3A10 10 0 1 0 12 2zm0 18a8 8 0 0 1-4.1-1.1l-.3-.2-2.8.8.7-2.7-.2-.3A8 8 0 1 1 12 20zm4.4-6c-.2-.1-1.4-.7-1.6-.8-.2-.1-.4-.1-.5.1l-.7.9c-.1.2-.3.2-.5.1a6.5 6.5 0 0 1-3.2-2.8c-.1-.2 0-.4.1-.5l.4-.5c.1-.2.1-.3 0-.5l-.7-1.7c-.2-.4-.4-.4-.5-.4h-.5c-.2 0-.4.1-.6.3a3 3 0 0 0-.9 2.2c0 1.3 1 2.6 1.1 2.8.1.2 1.9 3 4.7 4.1 1.7.7 2.3.7 3.1.6.5 0 1.4-.6 1.6-1.1.2-.6.2-1 .1-1.1z"/></svg></a>
 <button class="up" title="Sus" onclick="scrollTo({top:0,behavior:'smooth'})">↑</button>`;
 document.body.appendChild(d);}

/* ---------- carousels ---------- */
function wireRows(root=document){
 $$(".crow",root).forEach(cr=>{const tr=$(".ctrack",cr);
   $(".prev",cr).onclick=()=>tr.scrollBy({left:-560,behavior:"smooth"});
   $(".next",cr).onclick=()=>tr.scrollBy({left:560,behavior:"smooth"});});
}
function heroCarousel(el){
 const slides=$$(".hero-slide",el); let i=0;
 const tr=$(".hero-track",el), dots=$$(".hero-dots span",el);
 const go=n=>{i=(n+slides.length)%slides.length;tr.style.transform=`translateX(-${i*100}%)`;dots.forEach((d,k)=>d.classList.toggle("on",k===i));};
 $(".next",el).onclick=()=>go(i+1); $(".prev",el).onclick=()=>go(i-1);
 dots.forEach((d,k)=>d.onclick=()=>go(k));
 let t=setInterval(()=>go(i+1),6000);
 el.onmouseenter=()=>clearInterval(t); el.onmouseleave=()=>t=setInterval(()=>go(i+1),6000);
}

/* ---------- HOME ---------- */
function pageHome(){
 const m=C.marketing, root=$("#home");
 const heroes=["assets/img/hero/hero1.jpg?v=iv","assets/img/hero/hero2.jpg?v=iv","assets/img/hero/hero3.jpg?v=iv"];
 const slides=m.hero.map((s,k)=>`<div class="hero-slide" style="background-image:url('${heroes[k]}')"><div class="hero-c">
   <div class="k">AQUALUX · ${esc(C.city)}</div><h1>${esc(s.title_ro)}</h1><p>${esc(s.subtitle_ro)}</p>
   <a class="btn btn-gold" href="catalog.html">${esc(s.cta_ro)}</a></div></div>`).join("");
 const usp=m.usp.map((u,k)=>`<div class="u"><div class="ic">${["✦","♦","⛟","✓"][k]||"✦"}</div><div><b>${esc(u.title_ro)}</b><span>${esc(u.text_ro)}</span></div></div>`).join("");
 const catcards=C.cats.map(c=>`<div class="catcard"><div class="ic">${ICON.search.replace('<svg','<svg width=26 height=26')}</div><h3>${esc(c.name)}</h3><span>${c.count} produse →</span><a class="go" href="catalog.html?cat=${c.id}"></a></div>`).join("");
 const hot=P.filter(p=>p.badge==="hot"||p.rating>=4.8).slice(0,10);
 const sale=P.filter(p=>p.old_price).slice(0,10);
 const neu=P.filter(p=>p.badge==="new").slice(0,10);
 const vf0=P.filter(p=>p.real&&p.img.indexOf(".webp")>-1).slice(0,6).map(p=>p.img);
 const vf=vf0.length>=2?vf0:P.slice(0,6).map(p=>p.img);
 const revs=C.reviews.map(r=>`<div class="rev"><div class="stars">${stars(r.rating)}</div><p>„${esc(r.text_ro)}”</p><div class="who"><div class="av">${esc(r.name[0])}</div><div><b>${esc(r.name)}</b><span>${esc(r.city)} · ${esc(r.product)}</span></div></div></div>`).join("");
 const faq=m.faq.map(f=>`<div class="q"><div class="h">${esc(f.q_ro)}<span class="pl">+</span></div><div class="a">${esc(f.a_ro)}</div></div>`).join("");
 root.innerHTML=`
 <section class="hero"><div class="hero-track">${slides}</div><button class="hero-ar prev">‹</button><button class="hero-ar next">›</button><div class="hero-dots">${m.hero.map((_,k)=>`<span class="${k?'':'on'}"></span>`).join("")}</div></section>
 <section class="ustrip"><div class="wrap">${usp}</div></section>
 <div class="flash"><div class="wrap"><span>🔥 <b>Reduceri de sezon</b> — până la −25% la sanitehnică premium. Se termină în:</span><div class="cd" id="cd"><div class="u"><span id="cd-h">00</span><small>ore</small></div><div class="u"><span id="cd-m">00</span><small>min</small></div><div class="u"><span id="cd-s">00</span><small>sec</small></div></div><a class="btn btn-gold" href="catalog.html">Vezi ofertele</a></div></div>
 <section class="sec"><div class="wrap"><div class="sec-t"><div class="k">Colecții</div><h2>Categorii premium</h2></div><div class="cats-grid">${catcards}</div></div></section>
 <section class="sec"><div class="wrap"><div class="citybanner" style="background:url('assets/img/hero/hero2.jpg?v=iv') center/cover">
   <div class="cc"><span class="tag">Showroom · Ialoveni · Moldova</span>
     <h2>AQUALUX Ialoveni —<br>sanitehnică premium</h2>
     <p>Din inima orașului Ialoveni aducem baterii, lavoare din marmură și sisteme de duș de lux, cu livrare rapidă în toată Moldova.</p>
     <div class="meta"><div><b>2–5 zile</b>livrare în Moldova</div><div><b>100+</b>produse premium</div><div><b>Ramburs</b>plata la livrare</div></div>
     <a class="btn btn-gold" href="catalog.html">Vezi colecția</a></div>
 </div></div></section>
 <section class="sec bg-soft"><div class="wrap"><div class="sec-t"><div class="k">Cele mai dorite</div><h2>Top vânzări</h2></div>${rowOf(hot)}</div></section>
 ${sale.length?`<section class="sec"><div class="wrap"><div class="sec-t"><div class="k">Oferte</div><h2>Reduceri speciale</h2><p>Prețuri premium reduse pe stoc limitat.</p></div>${rowOf(sale)}</div></section>`:""}
 <section class="sec bg-soft"><div class="wrap"><div class="sec-t"><div class="k">Noutăți</div><h2>Adăugate recent</h2></div>${rowOf(neu.length?neu:P.slice(20,30))}</div></section>
 <section class="sec"><div class="wrap"><div class="trust">
   <div class="t"><div class="ic">⛟</div><b>Livrare în toată Moldova</b><span>Curier rapid, ramburs disponibil</span></div>
   <div class="t"><div class="ic">✓</div><b>Produse 100% originale</b><span>Direct de la producători verificați</span></div>
   <div class="t"><div class="ic">⟲</div><b>14 zile retur</b><span>Garanție oficială producător</span></div>
   <div class="t"><div class="ic">☎</div><b>Consultanță expertă</b><span>Te ajutăm să alegi corect</span></div>
 </div></div></section>
 <section class="sec"><div class="wrap"><div class="promo-banner"><h2>−10% la prima comandă</h2><p>Folosește codul la finalizarea comenzii și primești reducere instant la orice produs premium AQUALUX. În plus — livrare gratuită peste 3000 lei.</p><span class="code">AQUA10</span></div></div></section>
 <section class="sec"><div class="wrap"><div class="video-show"><div class="frames" id="vframes">${vf.map((u,i)=>`<img class="${i===0?"on":""}" src="${u}" alt="">`).join("")}</div><div class="vc"><div class="k">AQUALUX Showroom</div><h2>Sanitehnică premium în mișcare</h2><p>Baterii din alamă, lavoare din marmură și sisteme de duș de lux — colecția în acțiune.</p><button class="play" id="playBtn">▶</button><a class="btn btn-ghost" style="color:#fff;border-color:rgba(255,255,255,.6)" href="catalog.html">Explorează catalogul</a></div></div></div></section>
 <section class="sec bg-soft"><div class="wrap"><div class="sec-t"><div class="k">Recenzii</div><h2>Ce spun clienții noștri</h2></div>${rowOf2(revs)}</div></section>
 <section class="sec"><div class="wrap"><div class="sec-t"><div class="k">Întrebări frecvente</div><h2>FAQ</h2></div><div class="faq">${faq}</div></div></section>
 <section class="sec"><div class="wrap"><div class="news"><h2>Reduceri exclusive pe email</h2><p>Abonează-te și primești -10% la prima comandă.</p><form onsubmit="window.__news(this);return false;"><input type="email" required placeholder="Email-ul tău"><button class="btn btn-gold">Abonează-mă</button></form></div></div></section>`;
 heroCarousel($(".hero",root)); wireRows(root);
 $$(".faq .q .h",root).forEach(h=>h.onclick=()=>h.parentElement.classList.toggle("open"));
 (function(){var end=new Date();end.setHours(23,59,59,999);function t(){var d=Math.max(0,end-new Date());var H=$("#cd-h");if(!H)return;H.textContent=String(Math.floor(d/3.6e6)).padStart(2,"0");$("#cd-m").textContent=String(Math.floor(d%3.6e6/6e4)).padStart(2,"0");$("#cd-s").textContent=String(Math.floor(d%6e4/1e3)).padStart(2,"0");}t();setInterval(t,1000);})();
 (function(){var f=$$("#vframes img");if(f.length<2)return;var i=0;setInterval(function(){f[i].classList.remove("on");i=(i+1)%f.length;f[i].classList.add("on");},3000);})();
 var pb=$("#playBtn");if(pb)pb.onclick=function(){window.open("https://www.youtube.com/results?search_query=premium+bathroom+faucet+showroom","_blank");};
}
function rowOf2(html){return `<div class="crow"><button class="car prev">‹</button><div class="ctrack">${html}</div><button class="car next">›</button></div>`;}
window.__news=f=>{toast("Mulțumim! Codul -10% a fost trimis pe email ✓");f.reset();};

/* ---------- CATALOG (headless API mode) ---------- */
function pageCatalogAPI(){
 const root=$("#catalog");
 let cat=param("cat"), q=param("q")||"", sort="pop", page=1, per=24;
 const title=cat?(C.cats.find(c=>c.id===cat)||{}).name||"Catalog":(q?`Rezultate: „${esc(q)}”`:"Toate produsele");
 const intro=cat&&C.seo.category_intros&&C.seo.category_intros[cat]?`<p>${esc(C.seo.category_intros[cat])}</p>`:"";
 const catBoxes=C.cats.map(c=>`<label><input type="radio" name="apicat" value="${c.id}" ${cat===c.id?"checked":""}> ${esc(c.name)} <span class="cnt">${c.count}</span></label>`).join("");
 root.innerHTML=`<div class="page-head"><div class="wrap"><h1>${esc(title)}</h1>${intro}<p class="small" style="color:#3c7a4a;font-weight:700">⚡ Live din backend API · paginare pe server (5000+)</p></div></div>
  <div class="wrap" style="padding-top:26px;padding-bottom:40px"><div class="catalog">
   <aside class="filters"><h4>Categorii</h4><label><input type="radio" name="apicat" value="" ${!cat?"checked":""}> Toate produsele</label>${catBoxes}</aside>
   <div><div class="top"><span class="found" id="cat-found"></span><div>Sortează: <select id="cat-sort"><option value="pop">Populare</option><option value="asc">Preț crescător</option><option value="desc">Preț descrescător</option></select></div></div>
     <div class="pgrid" id="cat-grid"></div><div class="pager" id="cat-pager"></div></div>
 </div></div>`;
 async function load(){
   $("#cat-grid").innerHTML='<p class="muted" style="padding:30px">Se încarcă din backend…</p>';
   try{
     const u=`${API}/api/products?page=${page}&per=${per}`+(cat?`&cat=${cat}`:"")+(q?`&q=${encodeURIComponent(q)}`:"")+(sort!=="pop"?`&sort=${sort}`:"");
     const d=await (await fetch(u)).json();
     $("#cat-found").textContent=`${d.total} produse`;
     $("#cat-grid").innerHTML=(d.items&&d.items.length)?d.items.map(card).join(""):`<div class="empty"><div class="big">🔍</div><p>Niciun produs.</p></div>`;
     const pages=d.pages||1; let pg="";
     const lo=Math.max(1,page-3),hi=Math.min(pages,page+3);
     if(page>1)pg+=`<button data-pg="${page-1}">‹</button>`;
     if(lo>1)pg+=`<button data-pg="1">1</button>`+(lo>2?'<span style="padding:0 6px">…</span>':'');
     for(let i=lo;i<=hi;i++)pg+=`<button class="${i===page?'on':''}" data-pg="${i}">${i}</button>`;
     if(hi<pages)pg+=(hi<pages-1?'<span style="padding:0 6px">…</span>':'')+`<button data-pg="${pages}">${pages}</button>`;
     if(page<pages)pg+=`<button data-pg="${page+1}">›</button>`;
     $("#cat-pager").innerHTML=pages>1?pg:"";
     $$("#cat-pager button").forEach(b=>b.onclick=()=>{page=+b.dataset.pg;load();scrollTo({top:200,behavior:"smooth"});});
   }catch(e){$("#cat-grid").innerHTML=`<div class="empty"><div class="big">⚠️</div><p>Backend indisponibil — folosesc catalogul local.</p></div>`;window.__noapi=1;pageCatalog();}
 }
 $$('input[name=apicat]').forEach(r=>r.onchange=()=>{cat=r.value;page=1;load();});
 $("#cat-sort").onchange=e=>{sort=e.target.value;page=1;load();};
 load();
}
/* ---------- CATALOG ---------- */
function pageCatalog(){
 if(API && !window.__noapi) return pageCatalogAPI();
 const root=$("#catalog");
 let cat=param("cat"), q=(param("q")||"").toLowerCase(), sort="pop", page=1, per=12;
 const sel={cats:cat?[cat]:[], mats:[], price:""};
 const allMats=[...new Set(P.map(p=>p.specs.Material))];
 const priceB=[["0-3000","sub 3 000 lei"],["3000-7000","3 000 – 7 000 lei"],["7000-15000","7 000 – 15 000 lei"],["15000-999999","peste 15 000 lei"]];
 function filtered(){
   let l=P.slice();
   if(sel.cats.length) l=l.filter(p=>sel.cats.includes(p.cat));
   if(sel.mats.length) l=l.filter(p=>sel.mats.includes(p.specs.Material));
   if(sel.price){const[a,b]=sel.price.split("-").map(Number);l=l.filter(p=>p.price>=a&&p.price<=b);}
   if(q) l=l.filter(p=>(p.name+" "+p.cat_name+" "+p.specs.Material).toLowerCase().includes(q));
   if(sort==="asc") l.sort((a,b)=>a.price-b.price);
   else if(sort==="desc") l.sort((a,b)=>b.price-a.price);
   else if(sort==="disc") l.sort((a,b)=>discPct(b)-discPct(a));
   else l.sort((a,b)=>((b.real?1e7:0)+b.rating*b.reviews)-((a.real?1e7:0)+a.rating*a.reviews));
   return l;
 }
 function render(){
   const l=filtered(), pages=Math.max(1,Math.ceil(l.length/per));
   if(page>pages)page=pages;
   const slice=l.slice((page-1)*per,page*per);
   $("#cat-found").textContent=`${l.length} produse`;
   $("#cat-grid").innerHTML=slice.length?slice.map(card).join(""):`<div class="empty"><div class="big">🔍</div><p>Niciun produs găsit. Încearcă alte filtre.</p></div>`;
   let pg="";for(let i=1;i<=pages;i++)pg+=`<button class="${i===page?'on':''}" data-pg="${i}">${i}</button>`;
   $("#cat-pager").innerHTML=pages>1?pg:"";
   $$("#cat-pager button").forEach(b=>b.onclick=()=>{page=+b.dataset.pg;render();scrollTo({top:200,behavior:"smooth"});});
 }
 const catBoxes=C.cats.map(c=>`<label><input type="checkbox" data-f="cat" value="${c.id}" ${sel.cats.includes(c.id)?"checked":""}> ${esc(c.name)} <span class="cnt">${c.count}</span></label>`).join("");
 const matBoxes=allMats.map(mt=>`<label><input type="checkbox" data-f="mat" value="${esc(mt)}"> ${esc(mt)}</label>`).join("");
 const priceBoxes=priceB.map(([v,l])=>`<label><input type="radio" name="price" data-f="price" value="${v}"> ${l}</label>`).join("");
 const title=cat?(C.cats.find(c=>c.id===cat)||{}).name||"Catalog":(q?`Rezultate: „${esc(q)}”`:"Toate produsele");
 const intro=cat&&C.seo.category_intros[cat]?`<p>${esc(C.seo.category_intros[cat])}</p>`:"";
 root.innerHTML=`<div class="page-head"><div class="wrap"><h1>${esc(title)}</h1>${intro}</div></div>
  <div class="wrap" style="padding-top:26px;padding-bottom:40px"><div class="catalog">
   <aside class="filters">
     <h4>Categorii</h4>${catBoxes}
     <h4>Preț</h4>${priceBoxes}
     <h4>Material</h4>${matBoxes}
   </aside>
   <div><div class="top"><span class="found" id="cat-found"></span>
     <div>Sortează: <select id="cat-sort"><option value="pop">Populare</option><option value="asc">Preț crescător</option><option value="desc">Preț descrescător</option><option value="disc">Reduceri</option></select></div></div>
     <div class="pgrid" id="cat-grid"></div><div class="pager" id="cat-pager"></div></div>
  </div></div>`;
 $$('[data-f]',root).forEach(inp=>inp.onchange=()=>{
   const f=inp.dataset.f,v=inp.value;
   if(f==="cat"){sel.cats=$$('[data-f=cat]:checked').map(x=>x.value);}
   else if(f==="mat"){sel.mats=$$('[data-f=mat]:checked').map(x=>x.value);}
   else if(f==="price"){sel.price=v;}
   page=1;render();
 });
 $("#cat-sort").onchange=e=>{sort=e.target.value;render();};
 render();
}

/* ---------- PRODUCT ---------- */
function pageProduct(){
 const id=param("id"); let p=pById(id)||snaps()[id];
 if(!p && API){fetch(API+"/api/product/"+encodeURIComponent(id)).then(r=>r.ok?r.json():null).then(pr=>{if(pr)PCACHE[pr.id]=pr;renderProduct(pr);}).catch(()=>renderProduct(null));return;}
 renderProduct(p);
}
function renderProduct(p){
 const root=$("#product");
 if(!p){root.innerHTML=`<div class="wrap"><div class="empty"><div class="big">😕</div><p>Produsul nu a fost găsit.</p><a class="btn btn-gold" href="catalog.html">Înapoi la catalog</a></div></div>`;return;}
 document.title=p.name+" | AQUALUX Chișinău";
 const cc=C.copy.category[p.cat], save=p.old_price?p.old_price-p.price:0;
 const specRows=Object.entries(p.specs).map(([k,v])=>`<tr><td>${esc(k)}</td><td>${esc(v)}</td></tr>`).join("");
 const bullets=cc.bullets_ro.map(b=>`<li>${esc(b)}</li>`).join("");
 const pills=p.feat.split(/,|·/).map(s=>s.trim()).filter(Boolean).map(s=>`<span>${esc(s)}</span>`).join("");
 const related=P.filter(x=>x.cat===p.cat&&x.id!==p.id).slice(0,10);
 const prevs=C.reviews.filter(r=>r.rating>=4).slice(0,4).map(r=>`<div class="rev"><div class="stars">${stars(r.rating)}</div><p>„${esc(r.text_ro)}”</p><div class="who"><div class="av">${esc(r.name[0])}</div><div><b>${esc(r.name)}</b><span>${esc(r.city)}</span></div></div></div>`).join("");
 root.innerHTML=`<div class="wrap"><div class="bcrumb"><a href="index.html">Acasă</a> / <a href="catalog.html?cat=${p.cat}">${esc(p.cat_name)}</a> / ${esc(p.name)}</div>
 <div class="pdp">
   <div class="gallery">
     <div class="main"><img id="gmain" src="${p.img}" alt="${esc(p.name)}"></div>
     <div class="thumbs"><img class="on" src="${p.img}" onclick="document.getElementById('gmain').src=this.src"><img src="assets/img/hero/hero1.jpg?v=iv" onclick="document.getElementById('gmain').src=this.src" style="object-position:center"><img src="assets/img/hero/hero3.jpg?v=iv" onclick="document.getElementById('gmain').src=this.src"></div>
   </div>
   <div class="info">
     <span class="cat">${esc(p.cat_name)}</span><h1>${esc(p.name)}</h1>
     <div class="rowrate"><span class="stars">${stars(p.rating)}</span> <span>${p.rating} · ${p.reviews} recenzii</span> <span>· Cod: ${p.id}</span></div>
     <div class="feat-pills">${pills}</div>
     <div class="pbox">
       <div class="price"><span class="now">${money(p.price)}</span>${p.old_price?`<span class="old">${money(p.old_price)}</span><span class="disc">-${discPct(p)}%</span>`:""}</div>
       ${save?`<div class="savemsg">Economisești ${money(save)}</div>`:""}
       <div class="deliv">⛟ <span><b>${esc(C.copy.delivery_badge_ro)}.</b> Livrare în 2–5 zile (stoc) sau la comandă.</span></div>
       <div class="buyrow">
         <div class="qty"><button data-q="-">−</button><input id="pq" value="1" inputmode="numeric"><button data-q="+">+</button></div>
         <button class="btn btn-gold" style="flex:1" id="padd">${esc(C.copy.add_to_cart_ro)}</button>
       </div>
       <button class="btn btn-dark btn-block" id="pbuy">${esc(C.copy.buy_now_ro)}</button>
     </div>
     <div style="display:flex;gap:18px;font-size:12.5px;color:var(--muted);flex-wrap:wrap">
       <span>✓ Produs original</span><span>✓ Garanție ${esc(p.specs["Garanție"])}</span><span>✓ Ramburs disponibil</span><span>✓ 14 zile retur</span></div>
   </div>
 </div>
 <div class="tabs">
   <div class="heads"><button class="on" data-t="d">Descriere</button><button data-t="s">Specificații</button><button data-t="v">Video</button><button data-t="l">Livrare</button><button data-t="r">Recenzii</button></div>
   <div class="body" id="tb-d"><div class="prose"><p>${esc(cc.intro_ro)} ${esc(p.feat)}.</p><ul>${bullets}</ul><p style="color:var(--muted);font-size:13px">${esc(cc.care_ro)}</p></div></div>
   <div class="body" id="tb-s" hidden><table class="spec-tbl">${specRows}</table></div>
   <div class="body" id="tb-v" hidden><div class="videobox"><div style="font-size:40px">▶</div><div>Prezentare video — se adaugă din panoul de administrare</div></div></div>
   <div class="body" id="tb-l" hidden><div class="prose"><p>${esc(C.marketing.delivery_ro)}</p><p>${esc(C.marketing.returns_ro)}</p></div></div>
   <div class="body" id="tb-r" hidden><div class="crow"><button class="car prev">‹</button><div class="ctrack">${prevs}</div><button class="car next">›</button></div></div>
 </div>
 <section class="sec"><div class="sec-t" style="text-align:left"><h2>${esc(C.copy.cross_sell_title_ro)}</h2></div>${rowOf(related)}</section>
 </div>`;
 // JSON-LD
 const ld={"@context":"https://schema.org/","@type":"Product","name":p.name,"image":[location.origin+"/"+p.img],"description":p.feat,"sku":p.id,"brand":{"@type":"Brand","name":"AQUALUX"},"aggregateRating":{"@type":"AggregateRating","ratingValue":p.rating,"reviewCount":p.reviews},"offers":{"@type":"Offer","priceCurrency":"MDL","price":p.price,"availability":"https://schema.org/InStock"}};
 const s=document.createElement("script");s.type="application/ld+json";s.textContent=JSON.stringify(ld);document.head.appendChild(s);
 // interactions
 const pq=$("#pq");
 $$('[data-q]',root).forEach(b=>b.onclick=()=>{let v=Math.max(1,(+pq.value||1)+(b.dataset.q==="+"?1:-1));pq.value=v;});
 $("#padd").onclick=()=>addToCart(p.id,Math.max(1,+pq.value||1));
 $("#pbuy").onclick=()=>{addToCart(p.id,Math.max(1,+pq.value||1));location.href="checkout.html";};
 $$(".tabs .heads button",root).forEach(b=>b.onclick=()=>{$$(".tabs .heads button").forEach(x=>x.classList.remove("on"));b.classList.add("on");$$(".tabs .body").forEach(x=>x.hidden=true);$("#tb-"+b.dataset.t).hidden=false;wireRows();});
 wireRows(root);
}

/* ---------- CART ---------- */
function pageCart(){
 const root=$("#cart");
 function render(){
   const items=cartItems();
   if(!items.length){root.innerHTML=`<div class="wrap"><div class="empty"><div class="big">🛒</div><h2>Coșul este gol</h2><p>Adaugă produse premium din catalog.</p><a class="btn btn-gold" href="catalog.html">Spre catalog</a></div></div>`;return;}
   const sub=cartSub(), deliv=sub>=FREE?0:DELIV, total=sub+deliv, left=Math.max(0,FREE-sub), prog=Math.min(100,sub/FREE*100);
   const rows=items.map(({p,q})=>`<div class="cart-item"><img src="${p.img}"><div><div class="nm"><a href="produs.html?id=${p.id}">${esc(p.name)}</a></div><div style="font-size:12.5px;color:var(--muted)">${esc(p.specs.Material)} · ${esc(p.specs.Finisaj)}</div><div class="qty" style="margin-top:8px"><button data-m="${p.id}">−</button><input value="${q}" data-i="${p.id}" inputmode="numeric"><button data-p2="${p.id}">+</button></div><button class="rm" data-rm="${p.id}">Șterge</button></div><div class="ip">${money(p.price*q)}</div></div>`).join("");
   root.innerHTML=`<div class="page-head"><div class="wrap"><h1>Coșul tău</h1></div></div>
   <div class="wrap" style="padding:26px 20px 50px"><div class="cart-grid"><div>${rows}</div>
     <aside class="summary"><h3>Sumar comandă</h3>
       ${left>0?`<div style="font-size:12.5px;color:var(--muted)">Mai adaugă <b>${money(left)}</b> pentru livrare gratuită</div><div class="progress"><i style="width:${prog}%"></i></div>`:`<div style="color:var(--green);font-size:13px;font-weight:600">✓ Ai livrare gratuită!</div>`}
       <div class="row"><span>Subtotal</span><span>${money(sub)}</span></div>
       <div class="row"><span>Livrare</span><span>${deliv?money(deliv):"Gratuit"}</span></div>
       <div class="promo"><input id="promo" placeholder="Cod promo (AQUA10)"><button class="btn btn-ghost" id="promoB">Aplică</button></div>
       <div class="row total"><span>Total</span><span id="ctotal">${money(total)}</span></div>
       <a class="btn btn-gold btn-block" href="checkout.html" style="margin-top:14px">Finalizează comanda</a>
       <a class="btn btn-ghost btn-block" href="catalog.html" style="margin-top:8px">Continuă cumpărăturile</a>
     </aside></div></div>`;
   $$('[data-rm]').forEach(b=>b.onclick=()=>{setQty(b.dataset.rm,0);render();});
   $$('[data-m]').forEach(b=>b.onclick=()=>{const c=getCart();setQty(b.dataset.m,(c[b.dataset.m]||1)-1);render();});
   $$('[data-p2]').forEach(b=>b.onclick=()=>{const c=getCart();setQty(b.dataset.p2,(c[b.dataset.p2]||1)+1);render();});
   $$('[data-i]').forEach(inp=>inp.onchange=()=>{setQty(inp.dataset.i,Math.max(0,parseInt(inp.value)||0));render();});
   $("#promoB").onclick=()=>{if(($("#promo").value||"").toUpperCase()==="AQUA10"){const t=Math.round((sub*0.9+deliv));$("#ctotal").textContent=money(t);toast("Cod aplicat: -10% ✓");}else toast("Cod invalid");};
 }
 render();
}

/* ---------- CHECKOUT ---------- */
function pageCheckout(){
 const root=$("#checkout"), items=cartItems();
 if(!items.length){root.innerHTML=`<div class="wrap"><div class="empty"><div class="big">🛒</div><p>Coșul este gol.</p><a class="btn btn-gold" href="catalog.html">Spre catalog</a></div></div>`;return;}
 const sub=cartSub(), deliv=sub>=FREE?0:DELIV, total=sub+deliv;
 const sumRows=items.map(({p,q})=>`<div class="row"><span>${esc(p.name)} × ${q}</span><span>${money(p.price*q)}</span></div>`).join("");
 const cityOpts=CITIES.map(c=>`<option>${c}</option>`).join("");
 root.innerHTML=`<div class="page-head"><div class="wrap"><h1>Finalizare comandă</h1></div></div>
 <div class="wrap" style="padding:26px 20px 50px"><form id="coForm" class="co-grid">
   <div>
     <div class="co-card"><h3>Date de contact</h3>
       <div class="row2"><div class="field"><label>Nume complet <span class="req">*</span></label><input name="name" required></div>
       <div class="field"><label>Telefon <span class="req">*</span></label><input name="phone" required placeholder="+373 ..."></div></div>
       <div class="field"><label>Email</label><input name="email" type="email"></div>
     </div>
     <div class="co-card"><h3>Livrare</h3>
       <div class="row2"><div class="field"><label>Oraș <span class="req">*</span></label><select name="city">${cityOpts}</select></div>
       <div class="field"><label>Adresă <span class="req">*</span></label><input name="addr" required></div></div>
       <label class="opt sel"><input type="radio" name="dm" value="Curier Chișinău" checked><div><b>Curier Chișinău</b> — <span>2–3 zile, ${money(deliv||0)}</span></div></label>
       <label class="opt"><input type="radio" name="dm" value="Curier regiuni"><div><b>Curier în regiuni</b> — <span>3–5 zile</span></div></label>
       <label class="opt"><input type="radio" name="dm" value="Ridicare showroom"><div><b>Ridicare din showroom</b> — <span>Gratuit, Chișinău, bd. Ștefan cel Mare 1</span></div></label>
     </div>
     <div class="co-card"><h3>Plată</h3>
       <label class="opt sel"><input type="radio" name="pm" value="Ramburs" checked><div><b>Ramburs la livrare</b> — <span>Plătești la primirea coletului</span></div></label>
       <label class="opt"><input type="radio" name="pm" value="Card online"><div><b>Card bancar online</b> — <span>Visa / Mastercard (securizat)</span></div></label>
       <label class="opt"><input type="radio" name="pm" value="Transfer bancar"><div><b>Transfer bancar</b> — <span>Factură pentru persoane juridice</span></div></label>
     </div>
     <div class="co-card"><h3>Comentariu</h3><div class="field"><textarea name="note" rows="3" placeholder="Detalii suplimentare (opțional)"></textarea></div></div>
   </div>
   <aside class="summary"><h3>Comanda ta</h3>${sumRows}
     <div class="row"><span>Subtotal</span><span>${money(sub)}</span></div>
     <div class="row"><span>Livrare</span><span>${deliv?money(deliv):"Gratuit"}</span></div>
     <div class="row total"><span>Total</span><span>${money(total)}</span></div>
     <button class="btn btn-gold btn-block" type="submit" style="margin-top:14px">Plasează comanda</button>
     <p style="font-size:11.5px;color:var(--muted);margin-top:10px">Prin plasarea comenzii accepți termenii și politica de confidențialitate AQUALUX.</p>
   </aside>
 </form></div>`;
 $$(".opt input").forEach(r=>r.onchange=()=>{const nm=r.name;$$(`.opt input[name=${nm}]`).forEach(x=>x.closest(".opt").classList.toggle("sel",x.checked));});
 $("#coForm").onsubmit=e=>{e.preventDefault();const f=e.target;
   if(!f.name.value||!f.phone.value||!f.addr.value){toast("Completează câmpurile obligatorii");return;}
   const ord="AQ-"+Date.now().toString().slice(-6);
   const lines=items.map(x=>`${x.p.name} × ${x.q} = ${money(x.p.price*x.q)}`).join("%0A");
   const wa=`https://wa.me/${C.whatsapp}?text=${encodeURIComponent("Comandă nouă "+ord+" — AQUALUX")}%0A${lines}%0ATotal: ${money(total).replace(' ','%20')}%0AClient: ${encodeURIComponent(f.name.value+", "+f.phone.value+", "+f.city.value)}`;
   localStorage.removeItem(CART_KEY);updateCartCount();
   root.innerHTML=`<div class="wrap"><div class="okbox"><div class="circle">✓</div><h1>Comandă plasată!</h1>
     <p style="color:var(--muted);max-width:480px;margin:10px auto">Numărul comenzii tale: <b>${ord}</b>. Un consultant AQUALUX te va contacta în scurt timp pentru confirmare.</p>
     <div style="display:flex;gap:10px;justify-content:center;margin-top:20px;flex-wrap:wrap">
       <a class="btn btn-gold" href="${wa}" target="_blank">Trimite comanda pe WhatsApp</a>
       <a class="btn btn-ghost" href="index.html">Înapoi acasă</a></div>
     <p style="font-size:12px;color:var(--muted);margin-top:18px">Metoda de plată: ${f.pm.value} · Livrare: ${f.dm.value}</p></div></div>`;
   scrollTo({top:0});
 };
}

/* ---------- INFO PAGES ---------- */
function pageInfo(){
 const root=$("#info"), kind=document.body.dataset.info, m=C.marketing;
 const blocks={
  despre:{t:"Despre AQUALUX",h:m.about_ro.split("\\n\\n").map(p=>`<p>${esc(p)}</p>`).join("")+
    `<h3>De ce AQUALUX</h3><ul>${m.usp.map(u=>`<li><b>${esc(u.title_ro)}</b> — ${esc(u.text_ro)}</li>`).join("")}</ul>`},
  livrare:{t:"Livrare & plată",h:`<p>${esc(m.delivery_ro)}</p><h3>Metode de plată</h3><ul><li><b>Ramburs</b> — plata la livrare, direct curierului.</li><li><b>Card online</b> — Visa / Mastercard, plată securizată.</li><li><b>Transfer bancar</b> — pentru persoane juridice, cu factură.</li></ul><h3>Termene</h3><ul><li>Produse din stoc: <b>2–5 zile</b> în toată Moldova.</li><li>La comandă (import direct): <b>10–30 zile</b>, comunicat înainte de confirmare.</li><li>Livrare gratuită la comenzi peste <b>${money(FREE)}</b>.</li></ul>`},
  garantie:{t:"Garanție & retur",h:`<p>${esc(m.returns_ro)}</p><h3>Condiții de retur</h3><ul><li>14 zile pentru retur, produsul în stare originală și ambalaj intact.</li><li>Garanție oficială de la producător pentru fiecare produs.</li><li>Asistență AQUALUX pe tot parcursul procesului.</li></ul>`}
 };
 const b=blocks[kind]||blocks.despre;
 root.innerHTML=`<div class="page-head"><div class="wrap"><h1>${esc(b.t)}</h1></div></div><div class="wrap" style="padding:30px 20px 50px"><div class="prose">${b.h}</div></div>`;
}

/* ---------- CONTACTS ---------- */
function pageContacts(){
 const root=$("#contacts");
 root.innerHTML=`<div class="page-head"><div class="wrap"><h1>Contacte</h1><p>Suntem aici să te ajutăm să alegi sanitehnica premium potrivită.</p></div></div>
 <div class="wrap" style="padding:30px 20px 50px"><div class="co-grid">
   <div class="co-card"><h3>Scrie-ne</h3>
     <form onsubmit="window.__contact(this);return false;">
       <div class="row2"><div class="field"><label>Nume</label><input required></div><div class="field"><label>Telefon</label><input required></div></div>
       <div class="field"><label>Mesaj</label><textarea rows="4" required></textarea></div>
       <button class="btn btn-gold">Trimite mesajul</button></form></div>
   <aside class="co-card"><h3>Date de contact</h3>
     <p>📞 <a href="tel:${C.phone.replace(/ /g,'')}">${C.phone}</a></p>
     <p>✉️ <a href="mailto:${C.email}">${C.email}</a></p>
     <p>📍 ${esc(C.address)}</p>
     <p>🕘 Luni–Vineri 09:00–18:00<br>Sâmbătă 10:00–15:00</p>
     <a class="btn btn-gold btn-block" href="https://wa.me/${C.whatsapp}" target="_blank" style="margin-top:10px">Scrie pe WhatsApp</a>
     <div style="margin-top:14px;height:200px;border-radius:8px;background:linear-gradient(135deg,#1f1a13,#16130e);display:flex;align-items:center;justify-content:center;color:#c8a24c">📍 Showroom Chișinău</div>
   </aside></div></div>`;
}
window.__contact=f=>{toast("Mulțumim! Te contactăm în curând ✓");f.reset();};

/* ---------- boot ---------- */
document.addEventListener("DOMContentLoaded",()=>{
 buildHeader();buildFooter();buildFab();updateCartCount();
 document.addEventListener("click",e=>{const a=e.target.closest("[data-add]");if(a){addToCart(a.dataset.add);}
   const w=e.target.closest(".wish");if(w){w.style.color=w.style.color?"":"#b8463c";toast("Adăugat la favorite ♥");}});
 const pg=document.body.dataset.page;
 ({home:pageHome,catalog:pageCatalog,product:pageProduct,cart:pageCart,checkout:pageCheckout,info:pageInfo,contacts:pageContacts}[pg]||(()=>{}))();
});
})();
