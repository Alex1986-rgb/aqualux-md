# EUROMAG — premium интернет-магазин сантехники (Молдова)

Профессиональный магазин премиум-сантехники для рынка Молдовы (язык: română, валюта: **lei / MDL**), модель **дропшиппинг**. Статический сайт без сборки — открывается двойным кликом и разворачивается на любом хостинге / GitHub Pages.

## Что внутри
- **100 товаров** в 6 категориях (baterii baie, vase WC, lavoare, uscătoare prosoape, sisteme duș, baterii bucătărie)
- Корзина (localStorage), оформление заказа, выбор доставки и оплаты (ramburs / card / transfer + отправка в WhatsApp)
- Карусели (hero, top-vânzări, reduceri, noutăți, отзывы), фильтры, сортировка, пагинация, поиск
- Карточка товара: галерея, табы (описание/спецификации/видео/доставка/отзывы), related, JSON-LD
- Маркетинг: бейджи (Reducere/Top/Nou/Stoc limitat), старые цены, скидки, прогресс бесплатной доставки, промокод `AQUA10`, отзывы, FAQ, newsletter, плавающая кнопка WhatsApp
- SEO: уникальные title/description на страницу, OpenGraph, Schema.org (Store + Product), `sitemap.xml` (112 URL), `robots.txt`

## Запуск локально
```bash
cd ~/Downloads/aqualux-md
python3 -m http.server 8099
# открой http://localhost:8099
```
(Двойной клик по `index.html` тоже работает — данные в `assets/js/data.js`, без fetch.)

## Структура
```
index / catalog / produs / cos / checkout / despre / livrare / garantie / contacte .html
assets/css/style.css       — премиум-тема
assets/js/site.js          — движок (корзина, рендер, карусели)
assets/js/data.js          — товары + контент (генерируется)
assets/img/products/*.jpg  — 100 фото-плейсхолдеров по SKU
data/*.json                — исходные данные (products, content, seo, отзывы…)
build.py                   — генератор товаров + изображений
make_pages.py              — генератор HTML + sitemap + robots
```

## Заменить плейсхолдеры на реальные фото Alibaba
1. На карточке поставщика (Verified Supplier + Trade Assurance) скачай фото товара.
2. Сохрани в `assets/img/products/` **под именем SKU**, например `smesitel-01.jpg` (заменив плейсхолдер). SKU видно на каждом изображении и на странице товара (поле «Cod»).
3. Обнови `assets/js/data.js`: `python3 build.py && python3 -c "import json;p=open('data/products.json').read();c=open('data/content.json').read();open('assets/js/data.js','w').write('window.AQ_PRODUCTS='+p+';\nwindow.AQ_CONTENT='+c+';')"`
   (фото можно менять и без перегенерации — имена файлов те же.)

## Редактировать товары / цены
Правишь архетипы и цены в `build.py` (раздел `CATS`), затем:
```bash
python3 build.py && python3 make_pages.py
```

## Деплой на GitHub Pages
```bash
cd ~/Downloads/aqualux-md && git init && git add -A && git commit -m "EUROMAG store"
# создай репозиторий и:
git remote add origin <repo-url> && git push -u origin main
# Settings → Pages → Branch: main / root
```
Поменяй `SITE` в `make_pages.py` на реальный домен и перегенерируй для корректных canonical/sitemap.

## Что нужно для «боевого» запуска
- **Реальные фото/видео** товаров от поставщиков (сейчас премиум-плейсхолдеры).
- **Онлайн-оплата картой**: подключить молдавский платёжный шлюз (maib, Victoriabank, **PayNet**) — нужен мерчант-аккаунт и backend. Сейчас checkout формирует заказ + отправку в WhatsApp; `ramburs` (наложенный платёж) работает сразу.
- **Цены — рыночные оценки** (веб-поиск был недоступен): сверь закупку по реальным карточкам Alibaba и пересчитай розницу.
- Реальные контакты, телефон, адрес showroom, домен `.md`.

## Примечание про «импорт с Alibaba»
Массовый автоимпорт карточек требует Alibaba API/парсинга, что в этой сессии было недоступно (веб-поиск лежал). Поэтому собран реалистичный каталог из 100 SKU с румынскими названиями, характеристиками и ценами в MDL. Когда веб-доступ вернётся — можно автоматически подтянуть реальные листинги и фото по артикулам.
