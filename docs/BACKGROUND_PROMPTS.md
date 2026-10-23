# Промпты для фонов квестбука (ChatGPT, стиль Minecraft)

## Как пользоваться

1. Откройте **один** чат с ChatGPT и генерируйте все картинки в нём по очереди — так серия выйдет
   ровнее по стилю.
2. Копируйте блок промпта целиком: стиль, цвет, формат и запреты уже внутри.
3. Скачайте картинку и назовите её как в заголовке (`bg_global.png`, `bg_chronicle.png`, …).
4. Пришлите картинки в чат или положите в репозиторий в папку `art/backgrounds/`.

ChatGPT Images 2.0 рисует в соотношениях от 3:1 до 1:3, поэтому в каждом промпте указано точное
соотношение сторон главы (по реальным границам её графа). Если в ChatGPT есть переключатель соотношения
сторон, выставьте то же значение. Небольшое расхождение не страшно — подгоню сам. Яркость, контраст
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

Соотношение сторон: 16:9 (горизонтальная).

```
Create a background image. Scene: a blocky night sky over dark rolling hills seen from far away, scattered stars, a faint aurora low on the horizon, thick fog in the valleys; almost black, nothing in the middle. Color mood: almost black with a cold blue-violet hint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 16:9 (wide horizontal image).
```

### `bg_chronicle.png` — Летопись Первой экспедиции

Соотношение сторон: 5:3 (горизонтальная).

```
Create a background image. Scene: an abandoned expedition camp on a cliff at night: blocky tents, a cold campfire with a thin smoke trail, scattered crates and a lectern with an open book along the bottom edge, distant ruins on the horizon. Color mood: faint amber lantern glow. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 5:3 (wide horizontal image).
```

### `bg_life.png` — Дом, к которому возвращаются

Соотношение сторон: 7:5 (горизонтальная).

```
Create a background image. Scene: a small blocky homestead at dusk in the bottom-left corner: farmland with crops, a stone well, beehives, a cozy cottage with warm windows. Color mood: faint fresh green tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 7:5 (wide horizontal image).
```

### `bg_village.png` — Люди нашего поселения

Соотношение сторон: 5:4 (горизонтальная).

```
Create a background image. Scene: a blocky village on hills at sunset seen from afar along the bottom edge: a bell tower, market stalls with lanterns, distant fields. Color mood: faint warm peach tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 5:4 (wide horizontal image).
```

### `bg_exploration.png` — Дорога за горизонт

Соотношение сторон: 1:1 (квадрат).

```
Create a background image. Scene: a blocky path winding across different biomes toward a far horizon, shown around the edges: a volcano, a cherry blossom grove, an amethyst canyon, a glacier. Color mood: faint teal tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 1:1 (square image).
```

### `bg_archeology.png` — Археология — по следам Холма

Соотношение сторон: 6:5 (горизонтальная).

```
Create a background image. Scene: a blocky archaeological dig site at dusk along the bottom: suspicious sand, brushes, decorated clay pots, half-buried sandstone ruins. Color mood: faint sand-gold tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 6:5 (wide horizontal image).
```

### `bg_compass.png` — Атлас Линд — дальние экспедиции

Соотношение сторон: 1:1 (квадрат).

```
Create a background image. Scene: view from a high blocky mountain over a vast world at night: distant dungeon towers, a floating sky island and a lighthouse at the edges. Color mood: faint periwinkle blue tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 1:1 (square image).
```

### `bg_defense.png` — Звери и стражи старого мира

Соотношение сторон: 4:5 (вертикальная).

```
Create a background image. Scene: a misty blocky snowy forest at night: the silhouette of a giant frost beast at one edge, a tribal sun-mask totem at the other, an empty iron armor statue in the fog. Color mood: faint ember orange tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 4:5 (tall vertical image).
```

### `bg_ocean.png` — Океан — проводник и монумент

Соотношение сторон: 2:1 (горизонтальная).

```
Create a background image. Scene: a dark blocky underwater scene: prismarine ocean monument ruins along the bottom, a sunken shipwreck, kelp, faint light shafts from above. Color mood: faint cyan tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 2:1 (wide horizontal image).
```

### `bg_netheritage.png` — Нижний мир — огонь и черепа

Соотношение сторон: 8:7 (горизонтальная).

```
Create a background image. Scene: the Nether: blocky basalt pillars, the silhouette of a nether fortress bridge, dim lava falls at the edges, blue soul fire. Color mood: faint deep red-orange tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 8:7 (wide horizontal image).
```

### `bg_create.png` — Мастерская — первые машины

Соотношение сторон: 1:1 (квадрат).

```
Create a background image. Scene: a blocky workshop at night: large brass cogwheels, shafts, belts, a windmill and a waterwheel around the edges. Color mood: faint brass orange tint with a hint of cyan. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 1:1 (square image).
```

### `bg_industry.png` — Промышленность и артиллерия

Соотношение сторон: 7:6 (горизонтальная).

```
Create a background image. Scene: a blocky industrial complex at night: smokestacks, diesel engines, large cannons on stone walls, pipes along the edges. Color mood: faint acid yellow-green haze. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 7:6 (wide horizontal image).
```

### `bg_transport.png` — Дороги нового мира — рельсы и крылья

Соотношение сторон: 11:10 (горизонтальная).

```
Create a background image. Scene: a blocky steam train crossing a stone arch bridge at dusk, a small propeller biplane among blocky clouds, rails curving away at the edges. Color mood: faint sky blue tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 11:10 (wide horizontal image).
```

### `bg_economy.png` — Торговый дом

Соотношение сторон: 5:2 (горизонтальная).

```
Create a background image. Scene: a blocky market square at dusk along the bottom: striped awnings, barrels, emerald blocks, a llama caravan at the far edge. Color mood: faint emerald green tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 5:2 (wide horizontal image).
```

### `bg_grand_projects.png` — Великие проекты — база оживает

Соотношение сторон: 3:2 (горизонтальная).

```
Create a background image. Scene: a blocky factory town at night along the bottom edge: chimneys, conveyor bridges, glowing windows. Color mood: faint magenta haze. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 3:2 (wide horizontal image).
```

### `bg_legends.png` — Легенды глубин — шесть потерянных миров

Соотношение сторон: 11:10 (горизонтальная).

```
Create a background image. Scene: six underground cave worlds around the edges: magnetic ruins with floating blocks, a glowing toxic green cave, a deep abyssal trench, a candy-like cavern, a primordial jungle cave with giant bones, dark forlorn hollows. Color mood: faint violet tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 11:10 (wide horizontal image).
```

### `bg_cataclysm.png` — Восемь очей Зодчих

Соотношение сторон: 7:6 (горизонтальная).

```
Create a background image. Scene: dark ancient blocky citadels and ruins under a blood-red night sky, eight faint glowing eyes in a wide ring around an empty dark center. Color mood: faint crimson tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 7:6 (wide horizontal image).
```

### `bg_finale.png` — Край — конец пути

Соотношение сторон: 1:1 (квадрат).

```
Create a background image. Scene: the End dimension: blocky end stone islands floating over a black void, purpur towers of an end city, obsidian pillars, a distant ender dragon silhouette. Color mood: faint violet tint with a hint of teal. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 1:1 (square image).
```

### `bg_guild.png` — Бестиарий Ингрид Берг

Соотношение сторон: 1:1 (квадрат).

```
Create a background image. Scene: a blocky wildlife panorama around the edges, savanna, jungle and coast: a bison, an eagle, a gorilla, an elephant, a crocodile and seagulls. Color mood: faint leaf green tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 1:1 (square image).
```

### `bg_relics.png` — Кабинет редкостей

Соотношение сторон: 4:3 (горизонтальная).

```
Create a background image. Scene: a dim blocky treasure room: shelves, item frames and chests with strange trinkets, a magic mirror glowing faintly at the edge. Color mood: faint violet-blue tint. Minecraft-style blocky voxel world: everything is built from cubic blocks with crisp 16x16 pixel textures. Cinematic shader lighting at dusk or night, dark moody atmosphere, very low contrast, muted desaturated colors, deep shadows, soft distance fog and a soft vignette. This is a background for a quest map, so leave a wide, calm, empty dark area in the center of the image (sky, fog or darkness) and keep all details near the edges and the bottom. No text, no letters, no logos, no game interface (no hotbar, no crosshair, no inventory, no health bar), no player character, no frame or border, no watermark. Aspect ratio: 4:3 (wide horizontal image).
```

## Что я сделаю с готовыми картинками

- подгоню под точную пропорцию главы (если вышло чуть иначе) и уменьшу до 2048 пикселей по длинной стороне;
- измерю яркость и при необходимости затемню: снижу экспозицию, контраст и насыщенность, усилю
  виньетку и отдельно притушу середину, где стоят квесты;
- слегка размою мелкие пиксельные детали за графом, чтобы они не спорили со значками квестов;
- соберу превью «граф главы поверх фона» для каждой главы и покажу его до подключения;
- подключу их: общий фон — свойством темы книги (лежит под всем), фоны глав — картинками главы.
  Картинка главы в FTB Quests 2001.4.22 рисуется поверх линий зависимостей (проверено по байткоду),
  поэтому я сделаю её полупрозрачной (около 25–35 %), чтобы линии оставались видны.

Как это выглядит в настоящем интерфейсе FTB, нужно будет посмотреть в игре.
