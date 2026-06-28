/* Конфиг витрины.
   AQ_API — адрес backend (Level 3). Если задан и доступен — каталог/товары тянутся с него
   (server-side пагинация, 5000+ без тормозов). Если пусто или недоступен — fallback на data.js.

   • Локально (localhost) — автоматически http://localhost:3000 (твой локальный backend).
   • На live-сайте — впиши сюда URL своего Render-сервиса, напр.:
       window.AQ_API = "https://aqualux-backend.onrender.com";
*/
window.AQ_API = (location.hostname === "localhost" || location.hostname === "127.0.0.1")
  ? "http://localhost:3000"
  : "";   // ← сюда вставь URL backend на Render, чтобы live-сайт стал headless
