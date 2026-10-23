# Промпты для фонов квестбука (стиль Minecraft)

## Как фоны работают в FTB Quests 2001.4.22 (проверено по байткоду)

- **Общий фон книги** — свойство темы `background`. Оно одно на всю книгу (FTB берёт его без привязки
  к главе), растягивается на весь экран и лежит **под всем**, включая линии зависимостей.
- **Подложка главы** — картинка главы (chapter image) под её графом. У каждой главы своя, значки квестов
  рисуются поверх неё, **но линии зависимостей — под ней**. Поэтому подложки будут полупрозрачными
  (примерно 25–35 %) и обязаны быть тёмными. Яркая подложка спрячет линии.

## Единый стиль серии

Все картинки — кадры мира Minecraft: всё из кубических блоков с пиксельными текстурами 16×16,
кинематографичный вечерний или ночной свет, туман вдали. У каждой главы — свой оттенок её цвета.
Обязательно: тёмная и малоконтрастная, без интерфейса игры, без текста, середина пустая и спокойная
(небо, туман или темнота — там будут квесты), детали — у краёв и внизу.

**Добавляйте в конец каждого промпта** (общий стиль):

```
Minecraft-style voxel world, everything built from cubic blocks with crisp 16x16 pixel textures, cinematic
shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors,
deep shadows, soft distance fog, soft vignette, a wide calm empty dark area in the center (sky, fog or
darkness), details only near the edges and the bottom, no players, no characters in the center,
no text, no letters, no logo, no UI, no hotbar, no crosshair, no inventory, no watermark, no frame
```

**Запрещающий промпт** (для Stable Diffusion, Leonardo и т. п., где он есть):

```
text, letters, words, logo, watermark, signature, frame, border, UI, HUD, hotbar, crosshair, health bar,
inventory, player character, Steve, bright colors, high contrast, daylight, glowing center, smooth round
shapes, realistic photo, blurry
```

**Midjourney:** в конце `--ar W:H --style raw --stylize 100 --no text, logo, UI, hotbar, crosshair, player, frame`.
Если генератор не умеет нужную пропорцию — берите ближайшую и чуть больше, я обрежу сам.
Если генератор отказывается от слова «Minecraft», замените первую строку стиля на
`blocky voxel world made of cubes with crisp 16x16 pixel textures`.

**Вариант «плоский пиксель-арт»** вместо 3D: замените первую строку стиля на
`16-bit pixel art in the Minecraft palette, blocky cube-based scenery` — выглядит проще, но спокойнее.
Смешивать два варианта в одной серии не стоит.

## Общий фон книги

Файл `bg_global.png`, 16:9, 1920×1080 или больше.

```
a blocky Minecraft night sky over dark rolling hills seen from far away, scattered stars, a faint aurora
low on the horizon, thick fog in the valleys, almost black, nothing in the middle
```

## Подложки глав

Пропорция посчитана по реальным границам графа каждой главы. Оттенок — цвет главы из палитры квестбука.

| Файл | Глава | Пропорция | Промпт (+ общий стиль) |
|---|---|---|---|
| `bg_chronicle.png` | Летопись Первой экспедиции | 5:3 | `an abandoned expedition camp on a cliff at night: blocky tents, a cold campfire with a thin smoke trail, scattered crates and a lectern with an open book along the bottom edge, distant ruins on the horizon, faint amber lantern glow` |
| `bg_life.png` | Дом, к которому возвращаются | 7:5 | `a small blocky homestead at dusk in the bottom-left corner: farmland with crops, a stone well, beehives, a cozy cottage with warm windows, faint fresh green tint` |
| `bg_village.png` | Люди нашего поселения | 5:4 | `a blocky village on hills at sunset seen from afar along the bottom edge: a bell tower, market stalls with lanterns, distant fields, faint warm peach tint` |
| `bg_exploration.png` | Дорога за горизонт | 1:1 | `a blocky path winding across different biomes toward a far horizon, shown around the edges: a volcano, a cherry blossom grove, an amethyst canyon, a glacier, faint teal tint` |
| `bg_archeology.png` | Археология — по следам Холма | 6:5 | `a blocky archaeological dig site at dusk along the bottom: suspicious sand, brushes, decorated pots, half-buried sandstone ruins, faint sand gold tint` |
| `bg_compass.png` | Атлас Линд — дальние экспедиции | 1:1 | `view from a high blocky mountain over a vast world at night: distant dungeon towers, a floating sky island and a lighthouse at the edges, faint periwinkle blue tint` |
| `bg_defense.png` | Звери и стражи старого мира | 4:5 | `a misty blocky snowy forest at night: the silhouette of a giant frost beast at one edge, a tribal sun-mask totem at the other, an empty iron armor statue in the fog, faint ember orange tint` |
| `bg_ocean.png` | Океан — проводник и монумент | 2:1 | `a dark blocky underwater scene: prismarine ocean monument ruins along the bottom, a sunken shipwreck, kelp, faint light shafts from above, faint cyan tint` |
| `bg_netheritage.png` | Нижний мир — огонь и черепа | 8:7 | `the Nether: blocky basalt pillars, the silhouette of a nether fortress bridge, dim lava falls at the edges, blue soul fire, faint deep red orange tint` |
| `bg_create.png` | Мастерская — первые машины | 1:1 | `a blocky workshop at night: large brass cogwheels, shafts, belts, a windmill and a waterwheel around the edges, faint brass orange tint with a hint of cyan` |
| `bg_industry.png` | Промышленность и артиллерия | 7:6 | `a blocky industrial complex at night: smokestacks, diesel engines, large cannons on stone walls, pipes along the edges, faint acid yellow-green haze` |
| `bg_transport.png` | Дороги нового мира | 11:10 | `a blocky steam train crossing a stone arch bridge at dusk, a small propeller biplane among blocky clouds, rails curving away at the edges, faint sky blue tint` |
| `bg_economy.png` | Торговый дом | 5:2 | `a blocky market square at dusk along the bottom: striped awnings, barrels, emerald blocks, a llama caravan at the far edge, faint emerald green tint` |
| `bg_grand_projects.png` | Великие проекты — база оживает | 3:2 | `a blocky factory town at night along the bottom edge: chimneys, conveyor bridges, glowing windows, faint magenta haze` |
| `bg_legends.png` | Легенды глубин — шесть потерянных миров | 11:10 | `six underground cave worlds around the edges: magnetic ruins with floating blocks, a glowing toxic green cave, a deep abyssal trench, a candy-like cavern, a primordial jungle cave with giant bones, dark forlorn hollows, faint violet tint` |
| `bg_cataclysm.png` | Восемь очей Зодчих | 7:6 | `dark ancient blocky citadels and ruins under a blood-red night sky, eight faint glowing eyes in a wide ring around an empty dark center, faint crimson tint` |
| `bg_finale.png` | Край — конец пути | 1:1 | `the End dimension: blocky end stone islands floating over a black void, purpur towers of an end city, obsidian pillars, a distant ender dragon silhouette, faint violet tint with a hint of teal` |
| `bg_guild.png` | Бестиарий Ингрид Берг | 1:1 | `a blocky wildlife panorama around the edges, savanna, jungle and coast: a bison, an eagle, a gorilla, an elephant, a crocodile and seagulls, faint leaf green tint` |
| `bg_relics.png` | Кабинет редкостей | 4:3 | `a dim blocky treasure room: shelves, item frames and chests with strange trinkets, a magic mirror glowing faintly at the edge, faint violet blue tint` |

## Что делать с готовыми картинками

Назовите файлы как в таблице и пришлите в чат или положите в репозиторий в папку `art/backgrounds/`.
Дальше я сам:

- обрежу под точную пропорцию главы и уменьшу до 2048 пикселей по длинной стороне;
- измерю яркость и при необходимости затемню: снижу экспозицию, контраст и насыщенность, усилю
  виньетку и отдельно притушу середину, где стоят квесты;
- слегка размою мелкие пиксельные детали за графом, чтобы они не спорили со значками квестов;
- соберу превью «граф главы поверх фона» для каждой главы и покажу его до подключения;
- подключу (`kubejs/assets/nasledie/textures/backgrounds/`) и подберу прозрачность подложек.

Как это выглядит в настоящем интерфейсе FTB, нужно будет посмотреть в игре.
