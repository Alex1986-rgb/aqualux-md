/* ===== AQUALUX Level 3 backend =====
 * API товаров (с пагинацией), заказы → Telegram, серверный парсер Made-in-China (без лимитов прокси),
 * приватная статистика маржи (под ключом). Деплой: Render / Railway (free tier).
 *
 * ENV: PORT, TG_TOKEN, TG_CHAT, ADMIN_KEY  (см. .env.example)
 * data/: products.json (публичный), supply.json (приватный — закуп/маржа/доставка), orders.json (создаётся)
 */
const express = require("express");
const fs = require("fs");
const path = require("path");

const app = express();
app.use(express.json({ limit: "4mb" }));
// CORS (чтобы наш статичный сайт мог обращаться к API)
app.use((req, res, next) => {
  res.set("Access-Control-Allow-Origin", "*");
  res.set("Access-Control-Allow-Headers", "Content-Type, X-Admin-Key");
  res.set("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  if (req.method === "OPTIONS") return res.end();
  next();
});

const DATA = path.join(__dirname, "data");
const UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36";
const readJSON = (f, d) => { try { return JSON.parse(fs.readFileSync(path.join(DATA, f), "utf8")); } catch (e) { return d; } };

/* ---------- API: товары (пагинация + фильтры) ---------- */
app.get("/api/products", (req, res) => {
  let p = readJSON("products.json", []);
  const { cat, q, page = "1", per = "24", sort } = req.query;
  if (cat) p = p.filter(x => x.cat === cat);
  if (q) { const s = q.toLowerCase(); p = p.filter(x => (x.name || "").toLowerCase().includes(s)); }
  if (sort === "asc") p.sort((a, b) => a.price - b.price);
  else if (sort === "desc") p.sort((a, b) => b.price - a.price);
  const pg = Math.max(1, +page), pr = Math.min(100, +per), total = p.length;
  res.json({ total, page: pg, per: pr, pages: Math.ceil(total / pr), items: p.slice((pg - 1) * pr, pg * pr) });
});

app.get("/api/product/:id", (req, res) => {
  const p = readJSON("products.json", []).find(x => x.id === req.params.id);
  p ? res.json(p) : res.status(404).json({ error: "not found" });
});

/* ---------- API: заказ → Telegram + сохранение ---------- */
app.post("/api/order", async (req, res) => {
  const o = req.body || {};
  const orderId = "AQ-" + Date.now().toString().slice(-6);
  const txt =
    `🛒 *Comandă nouă AQUALUX* ${orderId}\n` +
    `👤 ${o.name || "-"}  ☎ ${o.phone || "-"}\n` +
    `📍 ${o.city || "-"}, ${o.addr || "-"}\n` +
    `💳 ${o.payment || "ramburs"} · 🚚 ${o.delivery || "curier"}\n` +
    `💰 Total: *${o.total || "-"} lei*\n` +
    (o.items || []).map(i => `• ${i.name} ×${i.qty} = ${i.sum || ""} lei`).join("\n");
  try {
    if (process.env.TG_TOKEN && process.env.TG_CHAT) {
      await fetch(`https://api.telegram.org/bot${process.env.TG_TOKEN}/sendMessage`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chat_id: process.env.TG_CHAT, text: txt, parse_mode: "Markdown" }),
      });
    }
    const orders = readJSON("orders.json", []);
    orders.push({ orderId, ...o, at: new Date().toISOString() });
    fs.writeFileSync(path.join(DATA, "orders.json"), JSON.stringify(orders, null, 2));
    res.json({ ok: true, orderId });
  } catch (e) { res.status(500).json({ ok: false, error: e.message }); }
});

/* ---------- API: серверный парсер Made-in-China (без лимитов прокси) ---------- */
function parseMIC(html, cat, limit) {
  const cards = [...html.matchAll(/<h2 class="product-name"[^>]*title="([^"]+)"[\s\S]{0,360}?\/product\/([A-Za-z0-9]+)\/([A-Za-z0-9\-]+)\.html/g)];
  const imgs = [...html.matchAll(/data-original="([^"]*image\.made-in-china[^"]*?\.(?:jpg|jpeg|png|webp)[^"]*)"/g)]
    .map(m => ({ pos: m.index, url: m[1].startsWith("//") ? "https:" + m[1] : m[1] }))
    .filter(o => !/Co-Ltd|Co\.,/.test(o.url));
  const prices = [...html.matchAll(/class="price">US\$<span>([\d.]+)/g)].map(m => ({ pos: m.index, usd: parseFloat(m[1]) }));
  const decode = s => s.replace(/&amp;/g, "&").replace(/&quot;/g, '"').replace(/&#39;/g, "'").replace(/&lt;/g, "<").replace(/&gt;/g, ">");
  const seen = new Set(), used = new Set(), out = [];
  for (const c of cards) {
    const pid = c[2]; if (seen.has(pid)) continue; seen.add(pid);
    const tpos = c.index;
    // галерея: до 6 ближайших неиспользованных фото = фото этого товара
    const cand = imgs.filter(im => !used.has(im.url)).map(im => ({ d: Math.abs(im.pos - tpos), url: im.url })).sort((a, b) => a.d - b.d).slice(0, 6);
    if (!cand.length) continue;
    const images = cand.map(x => x.url); images.forEach(u => used.add(u));
    let usd = 0, pb = 1e15; for (const pr of prices) { const d = Math.abs(pr.pos - tpos); if (d < pb) { pb = d; usd = pr.usd; } }
    const name = decode(c[1]).replace(/\s+/g, " ").trim().slice(0, 72);
    if (name.length < 8) continue;
    out.push({ name, img: images[0], images, usd, price: usd ? Math.round(usd * 80 / 10) * 10 : 3200, cat });
    if (out.length >= limit) break;
  }
  return out;
}
app.get("/api/parse", async (req, res) => {
  const { kw = "bathroom faucet", cat = "smesitel", max = "15" } = req.query;
  try {
    const url = `https://www.made-in-china.com/productdirectory.do?word=${encodeURIComponent(kw).replace(/%20/g, "+")}&subaction=hunt`;
    const r = await fetch(url, { headers: { "User-Agent": UA, "Referer": "https://www.made-in-china.com/" } });
    const html = await r.text();
    const items = parseMIC(html, cat, +max);
    res.json({ count: items.length, items });
  } catch (e) { res.status(500).json({ error: e.message }); }
});

/* ---------- API: приватная статистика маржи (под ключом) ---------- */
app.get("/api/admin/stats", (req, res) => {
  if (req.get("X-Admin-Key") !== process.env.ADMIN_KEY) return res.status(401).json({ error: "unauthorized" });
  const supply = readJSON("supply.json", {});
  const v = Object.values(supply);
  const retail = v.reduce((a, x) => a + (x.retail_mdl || 0), 0);
  const margin = v.reduce((a, x) => a + (x.margin_mdl || 0), 0);
  const landed = v.reduce((a, x) => a + (x.landed_mdl || 0), 0);
  res.json({ products: v.length, retail_total: retail, landed_total: landed, margin_total: margin,
    margin_pct: retail ? Math.round(margin / retail * 100) : 0, supply });
});

app.get("/api/admin/orders", (req, res) => {
  if (req.get("X-Admin-Key") !== process.env.ADMIN_KEY) return res.status(401).json({ error: "unauthorized" });
  res.json(readJSON("orders.json", []).reverse());
});

/* ---------- МАССОВЫЙ ИМПОРТ: все категории × пагинация ---------- */
const CAT_KW = { smesitel:"bathroom sensor faucet", kuhnya:"kitchen faucet pull out", unitaz:"smart toilet bidet",
  rakovina:"wash basin sink", polotenec:"heated towel rail", dush:"shower system set", cazi:"freestanding bathtub",
  cabine:"shower enclosure cabin", mobila_baie:"bathroom cabinet vanity", oglinzi:"led bathroom mirror",
  mobila_buc:"kitchen cabinet furniture", scaune:"dining chair modern", mese:"dining table modern", accesorii:"bathroom accessories set",
  malachit:"malachite stone product", iluminat:"ceiling light lamp modern", lustre:"crystal chandelier light", becuri:"led bulb lamp",
  prize:"wall socket switch", carnize:"curtain rod track", benzi_led:"led strip light", spoturi:"led spotlight downlight" };
const CAT_NAME = { smesitel:"Baterii pentru baie", kuhnya:"Baterii de bucătărie", unitaz:"Vase WC", rakovina:"Lavoare",
  polotenec:"Uscătoare de prosoape", dush:"Sisteme de duș", cazi:"Căzi de baie", cabine:"Cabine de duș",
  mobila_baie:"Mobilier de baie", oglinzi:"Oglinzi", mobila_buc:"Mobilier de bucătărie", scaune:"Scaune", mese:"Mese", accesorii:"Accesorii",
  malachit:"Articole din malachit", iluminat:"Corpuri de iluminat", lustre:"Candelabre & Lustre", becuri:"Becuri LED",
  prize:"Prize și întrerupătoare", carnize:"Galerii & Carnize", benzi_led:"Benzi LED", spoturi:"Spoturi & Proiectoare" };
const SHIP = { smesitel:12,kuhnya:12,unitaz:55,rakovina:30,polotenec:18,dush:30,cazi:120,cabine:80,mobila_baie:80,oglinzi:20,mobila_buc:110,scaune:25,mese:70,accesorii:8,
  malachit:40,iluminat:15,lustre:40,becuri:4,prize:4,carnize:12,benzi_led:6,spoturi:8 };
const MARGIN_K = { smesitel:2.4,kuhnya:2.3,unitaz:1.9,rakovina:2.2,polotenec:2.3,dush:2.1,cazi:1.8,cabine:1.9,mobila_baie:2.0,oglinzi:2.5,mobila_buc:1.85,scaune:2.4,mese:2.0,accesorii:2.6,
  malachit:2.6,iluminat:2.4,lustre:2.3,becuri:3.0,prize:2.8,carnize:2.5,benzi_led:2.6,spoturi:2.5 };
const FX = 18.2, HEAVY = ["cazi","cabine","mobila_baie","mobila_buc","mese"];
const sleep = ms => new Promise(r => setTimeout(r, ms));
const nice = v => { v = Math.round(v); return v < 1000 ? Math.round(v/10)*10 : Math.round(v/50)*50; };
async function fetchPage(kw, page) {
  const urls = [
    `https://www.made-in-china.com/multi-search/${encodeURIComponent(kw)}/F1/${page}.html`,
    `https://www.made-in-china.com/productdirectory.do?word=${encodeURIComponent(kw).replace(/%20/g,"+")}&subaction=hunt&page=${page}`,
  ];
  for (const u of urls) { try { const r = await fetch(u, { headers: { "User-Agent": UA, "Referer": "https://www.made-in-china.com/" } }); const t = await r.text(); if (t.length > 200000) return t; } catch (e) {} }
  return "";
}
app.get("/api/import-all", async (req, res) => {
  if (req.get("X-Admin-Key") !== process.env.ADMIN_KEY) return res.status(401).json({ error: "unauthorized" });
  const perCat = Math.min(400, Math.max(10, +(req.query.per_cat || 60)));
  const mode = req.query.mode === "append" ? "append" : "replace";
  const onlyCat = req.query.cat; // опц. одна категория
  const maxPages = Math.min(14, Math.ceil(perCat/30) + 2);
  let products = mode === "append" ? readJSON("products.json", []) : [];
  let supply = mode === "append" ? readJSON("supply.json", {}) : {};
  const seenImg = new Set(products.map(p => p.img));
  const summary = {}; let idx = products.length, blocked = 0;
  const cats = onlyCat ? { [onlyCat]: CAT_KW[onlyCat] } : CAT_KW;
  for (const [cat, kw] of Object.entries(cats)) {
    if (!kw) continue; let got = 0;
    for (let pg = 1; pg <= maxPages && got < perCat; pg++) {
      const html = await fetchPage(kw, pg);
      if (!html) { blocked++; break; }
      const items = parseMIC(html, cat, 1000); let added = 0;
      for (const it of items) {
        if (got >= perCat) break;
        if (seenImg.has(it.img)) continue; seenImg.add(it.img);
        idx++; got++; added++;
        const pid = `MIC-${idx}`, cost = it.usd || 40, ship = SHIP[cat] || 15;
        const landed = nice((cost + ship) * FX), retail = nice(landed * (MARGIN_K[cat] || 2.1)), margin = retail - landed;
        products.push({ id: pid, cat, cat_name: CAT_NAME[cat], real: true, name: it.name,
          slug: it.name.toLowerCase().replace(/[^a-z0-9]+/g,"-").slice(0,70) + "-" + pid.toLowerCase(),
          price: retail, old_price: 0, discount: 0, img: it.img, images: it.images || [it.img], badge: got <= 2 ? "hot" : "",
          rating: 4.7, reviews: 12 + got % 40, feat: it.name,
          specs: { Material: "Premium", Finisaj: "standard", Montare: "Standard", Garanție: "3 ani", Origine: "Import Made-in-China" } });
        supply[pid] = { cost_usd: Math.round(cost*100)/100, ship_usd: ship, landed_mdl: landed, retail_mdl: retail,
          margin_mdl: margin, margin_pct: Math.round(margin/retail*100), delivery_days: HEAVY.includes(cat) ? 25 : 12 };
      }
      if (added === 0) break;           // нет новых на странице — стоп (пагинация исчерпана/блок)
      await sleep(700);                 // пауза против антибота
    }
    summary[cat] = got;
  }
  fs.writeFileSync(path.join(DATA, "products.json"), JSON.stringify(products));
  fs.writeFileSync(path.join(DATA, "supply.json"), JSON.stringify(supply));
  res.json({ total: products.length, blocked, perCategory: summary });
});

/* ---------- АВТОПИЛОТ: фоновый импорт чанками ---------- */
const CAT_LIST = Object.keys(CAT_KW);
let AP = { running:false, target:5000, delay:12000, total:0, added:0, cursor:{ci:0,page:1}, roundEmpty:0, log:[], timer:null, startedAt:null };
function apSave(){ try{ fs.writeFileSync(path.join(DATA,"autopilot.json"), JSON.stringify({cursor:AP.cursor,target:AP.target,delay:AP.delay})); }catch(e){} }
function apLog(m){ AP.log.unshift("["+new Date().toISOString().slice(11,19)+"] "+m); AP.log = AP.log.slice(0,40); }
function mkProduct(cat, it){
  let products = readJSON("products.json", []), supply = readJSON("supply.json", {});
  let maxN = products.reduce((m,p)=>{ const mm=/^MIC-(\d+)$/.exec(p.id); return mm?Math.max(m,+mm[1]):m; }, 0);
  const pid = "MIC-"+(maxN+1), cost = it.usd||40, ship = SHIP[cat]||15;
  const landed = nice((cost+ship)*FX), retail = nice(landed*(MARGIN_K[cat]||2.1)), margin = retail-landed;
  products.push({ id:pid, cat, cat_name:CAT_NAME[cat], real:true, name:it.name,
    slug:it.name.toLowerCase().replace(/[^a-z0-9]+/g,"-").slice(0,70)+"-"+pid.toLowerCase(),
    price:retail, old_price:0, discount:0, img:it.img, images:it.images||[it.img], badge:"", rating:4.7, reviews:14, feat:it.name,
    specs:{ Material:"Premium", Finisaj:"standard", Montare:"Standard", Garanție:"3 ani", Origine:"Import Made-in-China" } });
  supply[pid] = { cost_usd:Math.round(cost*100)/100, ship_usd:ship, landed_mdl:landed, retail_mdl:retail,
    margin_mdl:margin, margin_pct:Math.round(margin/retail*100), delivery_days:HEAVY.includes(cat)?25:12 };
  return { products, supply };
}
async function importChunk(cat, page){
  const html = await fetchPage(CAT_KW[cat], page);
  if(!html) return { added:0, blocked:true, total:readJSON("products.json",[]).length };
  const items = parseMIC(html, cat, 1000);
  let products = readJSON("products.json", []), supply = readJSON("supply.json", {});
  const seen = new Set(products.map(p=>p.img));
  let added = 0;
  for(const it of items){
    if(seen.has(it.img)) continue; seen.add(it.img);
    const r = mkProduct(cat, it); products = r.products; supply = r.supply; added++;
  }
  if(added){ fs.writeFileSync(path.join(DATA,"products.json"), JSON.stringify(products)); fs.writeFileSync(path.join(DATA,"supply.json"), JSON.stringify(supply)); }
  return { added, blocked:false, total:products.length };
}
async function apTick(){
  if(!AP.running) return;
  const cat = CAT_LIST[AP.cursor.ci];
  try{
    const r = await importChunk(cat, AP.cursor.page);
    AP.total = r.total; AP.added += r.added;
    apLog(`${cat} p${AP.cursor.page}: +${r.added}${r.blocked?" ⛔блок":""} → ${AP.total}`);
    if(r.blocked || r.added===0){ AP.cursor.ci=(AP.cursor.ci+1)%CAT_LIST.length; AP.cursor.page=1; AP.roundEmpty = r.added===0?AP.roundEmpty+1:0; }
    else { AP.cursor.page++; AP.roundEmpty=0; }
    apSave();
    if(AP.total >= AP.target){ apLog("🎯 цель достигнута"); return apStop(); }
    if(AP.roundEmpty >= CAT_LIST.length){ apLog("⏹ все категории исчерпаны"); return apStop(); }
  }catch(e){ apLog("err: "+e.message); }
  AP.timer = setTimeout(apTick, AP.delay);
}
function apStart(target, delay){
  if(AP.running) return;
  const s = readJSON("autopilot.json", {});
  AP.cursor = s.cursor || { ci:0, page:1 };
  AP.target = target || s.target || 5000;
  AP.delay = Math.max(5000, (delay||12)*1000);
  AP.total = readJSON("products.json", []).length;
  AP.added = 0; AP.roundEmpty = 0; AP.running = true; AP.startedAt = Date.now();
  apLog("▶ автопилот старт · цель "+AP.target+" · пауза "+(AP.delay/1000)+"с");
  apTick();
}
function apStop(){ AP.running=false; if(AP.timer) clearTimeout(AP.timer); apLog("⏸ автопилот стоп"); }
const apAuth = (req,res)=>{ if(req.get("X-Admin-Key")!==process.env.ADMIN_KEY){ res.status(401).json({error:"unauthorized"}); return false; } return true; };
app.post("/api/autopilot/start", (req,res)=>{ if(!apAuth(req,res))return; apStart(+(req.query.target||5000), +(req.query.delay||12)); res.json({ok:true, running:AP.running, target:AP.target}); });
app.post("/api/autopilot/stop", (req,res)=>{ if(!apAuth(req,res))return; apStop(); res.json({ok:true, running:false}); });
app.get("/api/autopilot/status", (req,res)=>{ if(!apAuth(req,res))return; res.json({ running:AP.running, total:AP.total||readJSON("products.json",[]).length, target:AP.target, added:AP.added, cursor:AP.cursor, cat:CAT_LIST[AP.cursor.ci], cat_name:CAT_NAME[CAT_LIST[AP.cursor.ci]], log:AP.log, startedAt:AP.startedAt }); });

app.get("/api/health", (_, res) => res.json({ ok: true, service: "aqualux-backend" }));
app.use(express.static(path.join(__dirname, "public"))); // опц. отдавать фронт

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`AQUALUX backend → http://localhost:${PORT}`));
