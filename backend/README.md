# EUROMAG — Level 3 Backend

Node.js (Express) сервер: API товаров с пагинацией, заказы → Telegram, **серверный парсер Made-in-China без лимитов прокси**, приватная статистика маржи под ключом.

## Что решает (по сравнению с Level 2 / статикой)
| Возможность | Статика (Level 2) | Этот backend (Level 3) |
|---|---|---|
| 5000+ товаров без тормозов | ❌ (грузит весь data.js) | ✅ API + пагинация |
| Парсер в один клик без лимитов | 🟡 best-effort (прокси 413) | ✅ сервер качает напрямую |
| Заказы → Telegram уведомление | ❌ | ✅ `/api/order` |
| Приватная маржа/закуп (с авторизацией) | 🟡 только локально | ✅ `/api/admin/stats` под ключом |
| Авто-обновление каждые N часов | 🟡 cron на Mac | ✅ серверный планировщик |

## Эндпоинты
- `GET  /api/products?cat=&q=&page=1&per=24&sort=asc` — товары с пагинацией
- `GET  /api/product/:id` — один товар
- `POST /api/order` — оформить заказ (тело JSON), шлёт в Telegram, пишет в `data/orders.json`
- `GET  /api/parse?kw=bathroom+faucet&cat=smesitel&max=15` — спарсить товары с Made-in-China (без прокси)
- `GET  /api/admin/stats` — приватная статистика маржи (заголовок `X-Admin-Key: <ADMIN_KEY>`)
- `GET  /api/health` — проверка

## Запуск локально
```bash
cd backend
cp ../data/products.json data/products.json
cp ../data/supply.json   data/supply.json     # приватный — НЕ коммить
cp .env.example .env                           # заполни TG_TOKEN/TG_CHAT/ADMIN_KEY
npm install
npm start          # http://localhost:3000/api/health
```

## Деплой на Render (бесплатно)
1. Залей папку `backend/` в отдельный GitHub-репозиторий (без `data/supply.json` и `.env`!).
2. На **render.com** → New → Web Service → подключи репозиторий.
3. Build command: `npm install` · Start command: `npm start`.
4. Environment → добавь `TG_TOKEN`, `TG_CHAT`, `ADMIN_KEY`.
5. Залей `data/products.json` (можно в репо) и `data/supply.json` через Render Secret Files (приватно).
6. Готово — API доступно по `https://твой-сервис.onrender.com/api/products`.

## Подключение нашего сайта к API (headless)
В `assets/js/site.js` заменить загрузку из `data.js` на `fetch('https://...onrender.com/api/products?...')`,
а checkout — на `POST /api/order`. Дизайн остаётся наш, данные и заказы — через backend.

## Безопасность
- `data/supply.json`, `.env`, `data/orders.json` — **никогда не коммить в публичный репозиторий**.
- `ADMIN_KEY` — длинный случайный; статистика маржи отдаётся только с этим ключом.
