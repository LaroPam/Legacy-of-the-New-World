# Промпты для фонов квестбука

## Как фоны работают в FTB Quests 2001.4.22 (проверено по байткоду)

- **Общий фон книги** — свойство темы `background`. Оно одно на всю книгу (FTB берёт его без привязки
  к главе), растягивается на весь экран и лежит **под всем**, включая линии зависимостей.
- **Подложка главы** — картинка главы (chapter image) под её графом. У каждой главы своя, значки квестов
  рисуются поверх неё, **но линии зависимостей — под ней**. Поэтому подложки будут полупрозрачными
  (примерно 25–35 %) и обязаны быть тёмными. Яркая подложка спрячет линии.

## Единый стиль серии

Все картинки — словно страницы и наброски из полевого дневника Первой экспедиции: тушь и приглушённая
акварель на тёмной старой бумаге, у каждой главы — лёгкий оттенок её цвета. Обязательно:
тёмная и малоконтрастная, без текста, середина пустая и спокойная (там будут квесты), детали — у краёв.

**Добавляйте в конец каждого промпта** (общий стиль):

```
ink and muted watercolor sketch on dark aged parchment, charcoal and sepia tones, very low contrast,
dark overall with deep shadows and no bright areas, soft vignette, large calm empty space in the center,
details only near the edges, subtle paper grain, hand-drawn explorer's field-journal illustration,
no text, no letters, no handwriting, no numbers, no labels, no signature, no watermark, no frame, no border,
no people, no faces, no UI
```

**Запрещающий промпт** (для Stable Diffusion, Leonardo и т. п., где он есть):

```
text, letters, words, handwriting, numbers, signature, watermark, logo, frame, border, UI, bright colors,
high contrast, white background, glowing center, people, faces, hands, photo, 3d render, blurry
```

**Midjourney:** в конце `--ar W:H --style raw --stylize 100 --no text, letters, handwriting, signature, frame, people`.
Если генератор не умеет нужную пропорцию — берите ближайшую и чуть больше, я обрежу сам.
Если хочется намёка на Minecraft, добавьте `with subtly blocky, cube-based terrain and buildings`, но
проверьте результат: генераторы часто делают это неаккуратно.

## Общий фон книги

Файл `bg_global.png`, 16:9, 1920×1080 или больше.

```
an almost black surface of worn leather and old map paper, faint topographic contour lines and a barely
visible compass rose in one corner, scattered dust, deep heavy vignette, nothing in the middle
```

## Подложки глав

Пропорция посчитана по реальным границам графа каждой главы. Оттенок — цвет главы из палитры квестбука.

| Файл | Глава | Пропорция | Промпт (+ общий стиль) |
|---|---|---|---|
| `bg_chronicle.png` | Летопись Первой экспедиции | 5:3 | `an open expedition journal spread, pressed fern leaf, a broken brass compass, a cracked wax seal and a faded route line winding across the pages to the far right edge, faint amber gold tint` |
| `bg_life.png` | Дом, к которому возвращаются | 7:5 | `a small homestead at dusk sketched along the bottom and left edges: vegetable beds, a stone well, beehives, a cooking pot over a campfire, faint fresh green tint` |
| `bg_village.png` | Люди нашего поселения | 5:4 | `village rooftops and a bell tower at sunset drawn along the upper and lower edges, market lanterns, distant fields, faint warm peach tint` |
| `bg_exploration.png` | Дорога за горизонт | 1:1 | `a winding road to a far horizon through changing lands drawn around the edges: a volcano, a cherry blossom grove, an amethyst canyon, a glacier, faint teal tint` |
| `bg_archeology.png` | Археология — по следам Холма | 6:5 | `an excavation site study: brushes, trowels, pottery sherds, half-buried ruins in sand, faint measuring grid lines near the edges, faint sand gold tint` |
| `bg_compass.png` | Атлас Линд — дальние экспедиции | 1:1 | `a cartographer's chart with faded coastlines and contour lines, distant dungeon towers and a floating sky island in the margins, a compass rose in one corner, faint periwinkle blue tint` |
| `bg_defense.png` | Звери и стражи старого мира | 4:5 | `a hunter's study of great beasts emerging from mist at the edges: a frost-breathing giant, a bird with a sun mask, an empty suit of iron armor, faint ember orange tint` |
| `bg_ocean.png` | Океан — проводник и монумент | 2:1 | `a deep sea chart: sunken monument ruins, a shipwreck, light rays through water, kelp along the bottom edge, faint cyan tint` |
| `bg_netheritage.png` | Нижний мир — огонь и черепа | 8:7 | `an underworld sketch: basalt pillars, dark fortress bridges, distant lava glow, skulls on the margins, faint deep red orange tint` |
| `bg_create.png` | Мастерская — первые машины | 1:1 | `an engineering drafting sheet: brass cogwheels, shafts, belts, a windmill and a waterwheel in technical line art near the edges, faint brass orange tint with a hint of cyan` |
| `bg_industry.png` | Промышленность и артиллерия | 7:6 | `an industrial technical drawing: smokestacks, a diesel engine, a heavy cannon cross-section, pipes running along the edges, faint acid yellow-green tint` |
| `bg_transport.png` | Дороги нового мира | 11:10 | `a traveler's sketch: a steam locomotive on a stone arch bridge, a propeller biplane among clouds, rails curving away at the edges, faint sky blue tint` |
| `bg_economy.png` | Торговый дом | 5:2 | `merchant ledger margin art: striped market awnings, balance scales, sacks, emerald coins, a llama caravan at the far edge, faint emerald green tint` |
| `bg_grand_projects.png` | Великие проекты — база оживает | 3:2 | `a panorama of a living factory town at night along the bottom edge: chimneys, conveyor bridges, glowing windows, faint magenta tint` |
| `bg_legends.png` | Легенды глубин — шесть потерянных миров | 11:10 | `six underground worlds around the edges: magnetic ruins, a toxic green cave, an abyssal trench, a candy-like cavern, a primordial jungle cave, dark forlorn hollows, faint violet tint` |
| `bg_cataclysm.png` | Восемь очей Зодчих | 7:6 | `an ancient occult diagram: eight eyes in a wide circle around an empty center, each with a faint motif of flame, wave, storm, gear, skull, sand, ice and void, ruined citadel silhouettes at the edges, faint crimson tint` |
| `bg_finale.png` | Край — конец пути | 1:1 | `floating islands over a starless void, purpur towers, a distant dragon silhouette, faint violet tint with a hint of teal` |
| `bg_guild.png` | Бестиарий Ингрид Берг | 1:1 | `a naturalist's sketchbook: studies of a bison, an eagle, a gorilla, an elephant, a crocodile, a seagull and a mantis shrimp around the edges with botanical leaves, faint leaf green tint` |
| `bg_relics.png` | Кабинет редкостей | 4:3 | `a cabinet of curiosities around the edges: shelves and drawers with a magic mirror, a quiver, ice skates, a ring, a glass bottle and other strange trinkets, faint violet blue tint` |

## Что делать с готовыми картинками

Назовите файлы как в таблице и пришлите в чат или положите в репозиторий в папку `art/backgrounds/`.
Дальше я сам обрежу их под точные пропорции, уменьшу до 2048 пикселей по длинной стороне, при
необходимости затемню, подключу (`kubejs/assets/nasledie/textures/backgrounds/`) и подберу прозрачность
подложек. Как это выглядит в настоящем интерфейсе FTB, нужно будет посмотреть в игре.
