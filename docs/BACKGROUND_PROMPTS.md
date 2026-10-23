# Промпты для фонов квестбука (ChatGPT Images 2.0, стиль Minecraft)

## Как пользоваться

1. **Каждую картинку — в новом чате.** ChatGPT помнит контекст чата и тянет новые картинки к прошлым,
   поэтому в одном чате серия выходит одинаковой.
2. Копируйте блок промпта целиком: сцена, ракурс, палитра, правила и пропорция уже внутри.
3. Если в ChatGPT есть переключатель соотношения сторон, выставьте то же, что в промпте
   (ChatGPT Images 2.0 умеет от 3:1 до 1:3). Небольшое расхождение не страшно — подгоню сам.
4. Скачайте картинку и назовите её как в заголовке (`bg_global.png`, `bg_chronicle.png`, …).
5. Пришлите картинки в чат или положите в репозиторий в папку `art/backgrounds/`.

Каждая глава отличается ракурсом, временем суток, погодой, палитрой и тем, что занимает середину кадра
(там будут квесты). Общим остаётся только стиль Minecraft и запреты на текст и интерфейс.
Яркость не важна: слишком светлые картинки я затемню сам.

## Если картинка вышла не та

Пишите в тот же чат (можно копировать):

```
Make the middle of the image calmer and emptier, keep the details at the edges.
```

```
Remove all text, letters and any game interface from the image, keep everything else.
```

```
Make it look more different: change the camera angle and the lighting, keep the subject.
```

Если ChatGPT откажется рисовать по слову «Minecraft», замените в промпте `Minecraft-style voxel art`
на `Blocky voxel art`.

## Промпты

### `bg_global.png` — Общий фон книги (под всеми главами)

Соотношение сторон: 16:9 (горизонтальная). Идея: нейтральная тёмная текстура: подложки глав будут видны поверх неё.

```
A straight-on close-up of a wall built from dark deepslate and polished blackstone blocks, with faint cracks and a few dim specks of embedded ore. Soft vignette, almost black and very uniform, like a neutral texture. The whole image is calm, with no objects at all — it lies under the quest book. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 16:9 (wide horizontal image).
```

### `bg_chronicle.png` — Летопись Первой экспедиции

Соотношение сторон: 5:3 (горизонтальная). Идея: интерьер разрушенной башни, лунный свет.

```
Interior of a ruined stone watchtower used as the last camp of a lost expedition, seen at eye level at night. On the left a wooden desk with an open book, an unlit lantern and rope coils; on the right crates and a torn map pinned to the wall; cold moonlight falls through a broken window in the upper right. Palette: dusty amber and moonlit blue. The middle is a large, plain, shadowed stone wall — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 5:3 (wide horizontal image).
```

### `bg_life.png` — Дом, к которому возвращаются

Соотношение сторон: 7:5 (горизонтальная). Идея: утренний туман над огородом.

```
An early misty morning at eye level inside a farm. Rows of wheat, carrots and pumpkins fill the lower corners, a small cottage with chimney smoke stands on the left, chickens and a stone well on the right. Soft sunrise light. Palette: pale green, cream and warm gold. The middle is soft morning mist over an empty meadow — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 7:5 (wide horizontal image).
```

### `bg_village.png` — Люди нашего поселения

Соотношение сторон: 5:4 (горизонтальная). Идея: вид с холма на деревню на закате.

```
A high view from a hilltop at golden hour looking down at a village: houses with orange roofs, a bell tower and market stalls with striped awnings ring the edges, tiny villagers walk the paths. Palette: peach, coral and warm brown. The middle is a calm village pond reflecting the sunset sky — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 5:4 (wide horizontal image).
```

### `bg_exploration.png` — Дорога за горизонт

Соотношение сторон: 1:1 (квадрат). Идея: четыре биома по углам, большое небо.

```
A blocky road starts at the bottom and winds toward a distant horizon. Each corner shows a different land: a glacier in the upper left, a smoking volcano in the upper right, a cherry blossom grove in the lower left, an amethyst canyon in the lower right. Overcast daylight. Palette: teal, slate blue and soft pink. The middle is a huge open sky with soft clouds — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 1:1 (square image).
```

### `bg_archeology.png` — Археология — по следам Холма

Соотношение сторон: 6:5 (горизонтальная). Идея: вид сверху на раскоп в пустыне.

```
A top-down view straight down into a desert excavation at noon. Along the borders: string grid lines, brushes, suspicious sand blocks, decorated clay pots, bone blocks and half-buried sandstone carvings. Harsh but muted sunlight with short shadows. Palette: sand, ochre and dusty terracotta. The middle is flat, smooth, untouched sand — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 6:5 (wide horizontal image).
```

### `bg_compass.png` — Атлас Линд — дальние экспедиции

Соотношение сторон: 1:1 (квадрат). Идея: звёздное небо с балкона обсерватории.

```
From the stone balcony of a blocky observatory at night: a large telescope and a cartography table in the lower left, a railing along the bottom, the silhouettes of distant dungeon towers and a floating sky island low on the horizon. Palette: deep periwinkle, indigo and silver starlight. The middle is a wide starry night sky — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 1:1 (square image).
```

### `bg_defense.png` — Звери и стражи старого мира

Соотношение сторон: 4:5 (вертикальная). Идея: метель, вид снизу, силуэт зверя.

```
A low-angle view from the ground in a dark pine forest during a blizzard. Between the trees on the right towers the silhouette of a giant frost beast; on the left a tribal totem with a sun mask; at the bottom an empty iron armor statue half buried in snow, lit by a single torch. Palette: icy blue-grey with ember orange torchlight. The middle is swirling snow and fog — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 4:5 (tall vertical image).
```

### `bg_ocean.png` — Океан — проводник и монумент

Соотношение сторон: 2:1 (горизонтальная). Идея: под водой, лучи света.

```
A side view under deep water. A prismarine ocean monument rests in the lower right, a broken shipwreck lies in the lower left, a kelp forest sways along the bottom, small schools of fish drift near the edges, light rays come down from the surface. Palette: deep teal, cyan and dark navy. The middle is open, empty deep water — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 2:1 (wide horizontal image).
```

### `bg_netheritage.png` — Нижний мир — огонь и черепа

Соотношение сторон: 8:7 (горизонтальная). Идея: лавовое озеро, пепел.

```
In the Nether, looking across a vast lava lake from a basalt ledge in the foreground. Dark nether fortress bridges cross the far left, a crimson fungus forest grows on the right, ash particles fall through the air, blue soul fire flickers on the ledge. Palette: deep red, rust orange and charcoal. The middle is a dim, smoky haze above the lava lake — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 8:7 (wide horizontal image).
```

### `bg_create.png` — Мастерская — первые машины

Соотношение сторон: 1:1 (квадрат). Идея: интерьер мастерской с шестернями.

```
Inside a timber-framed mill workshop, seen straight on. Giant brass cogwheels turn on the left and right walls, belts and shafts run along the ceiling beams, a large waterwheel is visible through an opening at the bottom. Warm lamplight. Palette: brass orange, oak brown with small cyan accents. The middle is a plain, dark plank wall — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 1:1 (square image).
```

### `bg_industry.png` — Промышленность и артиллерия

Соотношение сторон: 7:6 (горизонтальная). Идея: дождливая ночь, заводской двор.

```
A rainy night in an industrial yard. Tall smokestacks release steam on the left, diesel tanks and pipes line the right, a heavy cannon stands on a stone wall in the lower right, wet ground reflects the lamps. Palette: acid yellow-green, oily black and steel grey. The middle is heavy, smoky rain clouds — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 7:6 (wide horizontal image).
```

### `bg_transport.png` — Дороги нового мира — рельсы и крылья

Соотношение сторон: 11:10 (горизонтальная). Идея: над облаками на рассвете.

```
An aerial view from above the clouds at sunrise. Below, through a gap in the clouds at the bottom, a steam train crosses a stone arch bridge over a valley; a small propeller biplane flies far away in the upper right. Palette: sky blue, soft pink and gold. The middle is a calm sea of clouds — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 11:10 (wide horizontal image).
```

### `bg_economy.png` — Торговый дом

Соотношение сторон: 5:2 (горизонтальная). Идея: ночной базар, очень широкая панорама.

```
A very wide side view of a night bazaar street. A long row of market stalls with striped awnings and hanging lanterns runs along the bottom, barrels and emerald blocks are stacked between them, and a llama caravan arrives on the far right. Palette: emerald green, warm lantern gold and deep night blue. The middle is a dark night sky softly lit by lantern glow — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 5:2 (wide horizontal image).
```

### `bg_grand_projects.png` — Великие проекты — база оживает

Соотношение сторон: 3:2 (горизонтальная). Идея: заводской город на берегу в сумерках.

```
A twilight panorama seen from the water. On the far shore at the bottom stands a large factory town with chimneys, conveyor bridges and lit windows, all reflected in a still lake. Palette: magenta, violet and dark teal. The middle is the mirror-like lake and the twilight sky — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 3:2 (wide horizontal image).
```

### `bg_legends.png` — Легенды глубин — шесть потерянных миров

Соотношение сторон: 11:10 (горизонтальная). Идея: огромная пещера, вид снизу вверх.

```
Inside an enormous underground cavern, looking up from below. Around the edges six different cave worlds open up: red and blue magnetic ruins with floating blocks, glowing toxic green pools, a deep abyssal water trench, a candy-colored cavern, a primordial jungle cave with giant bones, and dark forlorn hollows. Palette: violet with small patches of each biome color. The middle is the deep, dark center of the cavern — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 11:10 (wide horizontal image).
```

### `bg_cataclysm.png` — Восемь очей Зодчих

Соотношение сторон: 7:6 (горизонтальная). Идея: вид сверху на ритуальный круг.

```
A top-down view of an ancient ritual floor made of blackstone and gilded blocks. Eight sealed altars form a wide ring along the edges, each holding a dim glowing eye of a different element: flame, water, storm, gear, skull, sand, ice and void. Thin crimson cracks run toward the center. Palette: black, tarnished gold and crimson. The middle is the dark, empty circular floor — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 7:6 (wide horizontal image).
```

### `bg_finale.png` — Край — конец пути

Соотношение сторон: 1:1 (квадрат). Идея: край острова, взгляд в пустоту.

```
In the End, looking out from the edge of an end stone island into the void. Purpur towers of an end city rise on the left, obsidian pillars stand on the right, a beam of an end gateway glows far away, a distant ender dragon silhouette circles near the top. Palette: violet, black and a touch of teal. The middle is a black, starless void with faint purple particles — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 1:1 (square image).
```

### `bg_guild.png` — Бестиарий Ингрид Берг

Соотношение сторон: 1:1 (квадрат). Идея: рассвет на краю саванны и джунглей.

```
Dawn at a naturalist field station on a wooden deck where savanna meets jungle. Animals around the edges: a bison and an elephant on the left, a gorilla among jungle leaves on the right, a crocodile in the river along the bottom, an eagle and seagulls in the upper corners. Palette: leaf green, savanna gold and dawn peach. The middle is soft dawn sky and savanna haze — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 1:1 (square image).
```

### `bg_relics.png` — Кабинет редкостей

Соотношение сторон: 4:3 (горизонтальная). Идея: кабинет диковин при свечах.

```
Interior of a cabinet of curiosities lit by candles. Tall shelves on the left and right hold strange trinkets, item frames, glass display cases, ice skates, a quiver and a glowing magic mirror. Palette: dark violet, deep blue and candle gold. The middle is a dark, velvet-like back wall — a quest map will be placed there. Minecraft-style voxel art: everything is made of cubic blocks with crisp 16x16 pixel textures. Keep the colors subdued, low-contrast and slightly desaturated so the picture works as a background behind small icons. No text, no letters, no logos, no game interface (no hotbar, crosshair, inventory or health bar), no player character, no border, no watermark. Aspect ratio: 4:3 (wide horizontal image).
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
