/* EUROMAG service worker — offline cache */
const CACHE = "euromag-v1";
const CORE = [
  "./", "./index.html", "./catalog.html", "./cos.html",
  "./assets/css/style.css", "./assets/js/site.js", "./assets/js/data.js", "./assets/js/config.js"
];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE).catch(() => {})));
  self.skipWaiting();
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))));
  self.clients.claim();
});
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET") return;
  const u = new URL(e.request.url);
  if (u.origin !== location.origin) return;            // API / external images → network
  e.respondWith(
    caches.match(e.request).then(r =>
      r || fetch(e.request).then(resp => {
        const cp = resp.clone();
        caches.open(CACHE).then(c => c.put(e.request, cp).catch(() => {}));
        return resp;
      }).catch(() => caches.match("./index.html"))
    )
  );
});
