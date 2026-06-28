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
    const tpos = c.index; let img = null, best = 1e15;
    for (const im of imgs) { if (used.has(im.url)) continue; const d = Math.abs(im.pos - tpos); if (d < best) { best = d; img = im; } }
    if (!img) for (const im of imgs) { const d = Math.abs(im.pos - tpos); if (d < best) { best = d; img = im; } }
    if (!img) continue; used.add(img.url);
    let usd = 0, pb = 1e15; for (const pr of prices) { const d = Math.abs(pr.pos - tpos); if (d < pb) { pb = d; usd = pr.usd; } }
    const name = decode(c[1]).replace(/\s+/g, " ").trim().slice(0, 72);
    if (name.length < 8) continue;
    out.push({ name, img: img.url, usd, price: usd ? Math.round(usd * 80 / 10) * 10 : 3200, cat });
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

app.get("/api/health", (_, res) => res.json({ ok: true, service: "aqualux-backend" }));
app.use(express.static(path.join(__dirname, "public"))); // опц. отдавать фронт

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`AQUALUX backend → http://localhost:${PORT}`));
