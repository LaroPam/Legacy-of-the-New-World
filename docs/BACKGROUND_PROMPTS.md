# Промпты для фонов квестбука (ChatGPT, стиль Minecraft)

## Как пользоваться

1. Откройте **один** чат с ChatGPT и генерируйте все картинки в нём по очереди — так серия выйдет
   ровнее по стилю.
2. Копируйте блок промпта целиком: стиль, цвет, формат и запреты уже внутри.
3. Скачайте картинку и назовите её как в заголовке (`bg_global.png`, `bg_chronicle.png`, …).
4. Пришлите картинки в чат или положите в репозиторий в папку `art/backgrounds/`.

Обычно ChatGPT рисует квадрат, горизонтальную 3:2 или вертикальную 2:3 картинку, поэтому в промптах указан
ближайший из этих форматов. До точной пропорции главы я обрежу картинку сам, так что формат не критичен. Яркость, контраст
и мелкие детали за графом тоже подгоню сам.

## Если картинка вышла не та

Пишите в тот же чат одной из фраз (можно копировать):

```
Make the same image darker and calmer: lower contrast, less saturation, keep the center empty.
```

```
Remove all text, letters and any game interface from the image, keep everything else.
```

```
Keep exactly the same style as the previous images in this chat.
```

Если ChatGPT откажется рисовать по слову «Minecraft», замените в промпте `Minecraft-style blocky voxel world`
на `blocky voxel world`.

## Промпты

### `bg_global.png` — Общий фон книги (под всеми главами)

Формат в ChatGPT: горизонтальная 3:2, потом обрежу до 16:9.

```
Create a background image. Scene: a blocky night sky over dark rolling hills seen from far away, scattered stars, a faint aurora low on the horizon, thick fog in the valleys; almost black, nothing in the middle. Color mood: almost black with a cold blue-violet hint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: wide landscape image, 3:2.
```

### `bg_chronicle.png` — Летопись Первой экспедиции

Формат в ChatGPT: горизонтальная 3:2, потом обрежу до 5:3.

```
Create a background image. Scene: an abandoned expedition camp on a cliff at night: blocky tents, a cold campfire with a thin smoke trail, scattered crates and a lectern with an open book along the bottom edge, distant ruins on the horizon. Color mood: faint amber lantern glow. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: wide landscape image, 3:2.
```

### `bg_life.png` — Дом, к которому возвращаются

Формат в ChatGPT: горизонтальная 3:2, потом обрежу до 7:5.

```
Create a background image. Scene: a small blocky homestead at dusk in the bottom-left corner: farmland with crops, a stone well, beehives, a cozy cottage with warm windows. Color mood: faint fresh green tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: wide landscape image, 3:2.
```

### `bg_village.png` — Люди нашего поселения

Формат в ChatGPT: горизонтальная 3:2, потом обрежу до 5:4.

```
Create a background image. Scene: a blocky village on hills at sunset seen from afar along the bottom edge: a bell tower, market stalls with lanterns, distant fields. Color mood: faint warm peach tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: wide landscape image, 3:2.
```

### `bg_exploration.png` — Дорога за горизонт

Формат в ChatGPT: квадрат, потом обрежу до 1:1.

```
Create a background image. Scene: a blocky path winding across different biomes toward a far horizon, shown around the edges: a volcano, a cherry blossom grove, an amethyst canyon, a glacier. Color mood: faint teal tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: square image, 1:1.
```

### `bg_archeology.png` — Археология — по следам Холма

Формат в ChatGPT: горизонтальная 3:2, потом обрежу до 6:5.

```
Create a background image. Scene: a blocky archaeological dig site at dusk along the bottom: suspicious sand, brushes, decorated clay pots, half-buried sandstone ruins. Color mood: faint sand-gold tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: wide landscape image, 3:2.
```

### `bg_compass.png` — Атлас Линд — дальние экспедиции

Формат в ChatGPT: квадрат, потом обрежу до 1:1.

```
Create a background image. Scene: view from a high blocky mountain over a vast world at night: distant dungeon towers, a floating sky island and a lighthouse at the edges. Color mood: faint periwinkle blue tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: square image, 1:1.
```

### `bg_defense.png` — Звери и стражи старого мира

Формат в ChatGPT: вертикальная 2:3, потом обрежу до 4:5.

```
Create a background image. Scene: a misty blocky snowy forest at night: the silhouette of a giant frost beast at one edge, a tribal sun-mask totem at the other, an empty iron armor statue in the fog. Color mood: faint ember orange tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: tall portrait image, 2:3.
```

### `bg_ocean.png` — Океан — проводник и монумент

Формат в ChatGPT: горизонтальная 3:2, потом обрежу до 2:1.

```
Create a background image. Scene: a dark blocky underwater scene: prismarine ocean monument ruins along the bottom, a sunken shipwreck, kelp, faint light shafts from above. Color mood: faint cyan tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: wide landscape image, 3:2.
```

### `bg_netheritage.png` — Нижний мир — огонь и черепа

Формат в ChatGPT: квадрат, потом обрежу до 8:7.

```
Create a background image. Scene: the Nether: blocky basalt pillars, the silhouette of a nether fortress bridge, dim lava falls at the edges, blue soul fire. Color mood: faint deep red-orange tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: square image, 1:1.
```

### `bg_create.png` — Мастерская — первые машины

Формат в ChatGPT: квадрат, потом обрежу до 1:1.

```
Create a background image. Scene: a blocky workshop at night: large brass cogwheels, shafts, belts, a windmill and a waterwheel around the edges. Color mood: faint brass orange tint with a hint of cyan. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: square image, 1:1.
```

### `bg_industry.png` — Промышленность и артиллерия

Формат в ChatGPT: квадрат, потом обрежу до 7:6.

```
Create a background image. Scene: a blocky industrial complex at night: smokestacks, diesel engines, large cannons on stone walls, pipes along the edges. Color mood: faint acid yellow-green haze. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: square image, 1:1.
```

### `bg_transport.png` — Дороги нового мира — рельсы и крылья

Формат в ChatGPT: квадрат, потом обрежу до 11:10.

```
Create a background image. Scene: a blocky steam train crossing a stone arch bridge at dusk, a small propeller biplane among blocky clouds, rails curving away at the edges. Color mood: faint sky blue tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: square image, 1:1.
```

### `bg_economy.png` — Торговый дом

Формат в ChatGPT: горизонтальная 3:2, потом обрежу до 5:2.

```
Create a background image. Scene: a blocky market square at dusk along the bottom: striped awnings, barrels, emerald blocks, a llama caravan at the far edge. Color mood: faint emerald green tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: wide landscape image, 3:2.
```

### `bg_grand_projects.png` — Великие проекты — база оживает

Формат в ChatGPT: горизонтальная 3:2, потом обрежу до 3:2.

```
Create a background image. Scene: a blocky factory town at night along the bottom edge: chimneys, conveyor bridges, glowing windows. Color mood: faint magenta haze. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: wide landscape image, 3:2.
```

### `bg_legends.png` — Легенды глубин — шесть потерянных миров

Формат в ChatGPT: квадрат, потом обрежу до 11:10.

```
Create a background image. Scene: six underground cave worlds around the edges: magnetic ruins with floating blocks, a glowing toxic green cave, a deep abyssal trench, a candy-like cavern, a primordial jungle cave with giant bones, dark forlorn hollows. Color mood: faint violet tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: square image, 1:1.
```

### `bg_cataclysm.png` — Восемь очей Зодчих

Формат в ChatGPT: квадрат, потом обрежу до 7:6.

```
Create a background image. Scene: dark ancient blocky citadels and ruins under a blood-red night sky, eight faint glowing eyes in a wide ring around an empty dark center. Color mood: faint crimson tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: square image, 1:1.
```

### `bg_finale.png` — Край — конец пути

Формат в ChatGPT: квадрат, потом обрежу до 1:1.

```
Create a background image. Scene: the End dimension: blocky end stone islands floating over a black void, purpur towers of an end city, obsidian pillars, a distant ender dragon silhouette. Color mood: faint violet tint with a hint of teal. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: square image, 1:1.
```

### `bg_guild.png` — Бестиарий Ингрид Берг

Формат в ChatGPT: квадрат, потом обрежу до 1:1.

```
Create a background image. Scene: a blocky wildlife panorama around the edges, savanna, jungle and coast: a bison, an eagle, a gorilla, an elephant, a crocodile and seagulls. Color mood: faint leaf green tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: square image, 1:1.
```

### `bg_relics.png` — Кабинет редкостей

Формат в ChatGPT: горизонтальная 3:2, потом обрежу до 4:3.

```
Create a background image. Scene: a dim blocky treasure room: shelves, item frames and chests with strange trinkets, a magic mirror glowing faintly at the edge. Color mood: faint violet-blue tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Format: wide landscape image, 3:2.
```

## Что я сделаю с готовыми картинками

- обрежу под точную пропорцию главы и уменьшу до 2048 пикселей по длинной стороне;
- измерю яркость и при необходимости затемню: снижу экспозицию, контраст и насыщенность, усилю
  виньетку и отдельно притушу середину, где стоят квесты;
- слегка размою мелкие пиксельные детали за графом, чтобы они не спорили со значками квестов;
- соберу превью «граф главы поверх фона» для каждой главы и покажу его до подключения;
- подключу их: общий фон — свойством темы книги (лежит под всем), фоны глав — картинками главы.
  Картинка главы в FTB Quests 2001.4.22 рисуется поверх линий зависимостей (проверено по байткоду),
  поэтому я сделаю её полупрозрачной (около 25–35 %), чтобы линии оставались видны.

Как это выглядит в настоящем интерфейсе FTB, нужно будет посмотреть в игре.
