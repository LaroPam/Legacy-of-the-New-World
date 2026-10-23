# Промпты для медальонов квестов (ChatGPT Images 2.0)

У всех квестов один круглый медальон; тип квеста виден по рисунку рамки. Семь типов — семь картинок.

## Как пользоваться

1. **Каждую картинку — в новом чате**, иначе ChatGPT тянет рисунки друг к другу.
2. Копируйте блок промпта целиком: в нём уже есть стиль, геометрия, запреты и пропорция 1:1.
3. Сохраните картинку под именем из заголовка (`frame_step.png`, …) в папку `art/frames/`.
4. Если в середине что-то нарисовалось (предмет, символ, узор), напишите в тот же чат:

```
Keep the ring exactly as it is, but make the whole inside of the circle an empty smooth dark recess with only a faint glow.
```

Если медальон не касается краёв картинки или чуть смещён — не страшно, я обрежу сам.
FTB рисует фон квеста полупрозрачным (примерно 60 %), поэтому выбирайте яркий и насыщенный вариант.

## Что я сделаю с картинками

`python tools/quest_frames.py` вырежет медальон по кругу, затемнит середину (там значок предмета),
добавит тонкий ободок — FTB окрашивает его в цвет состояния квеста: закрыт, доступен, начат, выполнен — и
сложит формы в `kubejs/assets/ftbquests/textures/shapes/<тип>/`. Значки квестов станут чуть меньше
(`icon_scale` 0.75), чтобы даже квадратный блок помещался внутри рамки. Перед подключением покажу превью.

| Файл | Тип | Сейчас в книге |
|---|---|---|
| `frame_step.png` | шаг | круг, 172 квеста |
| `frame_expedition.png` | экспедиция | свиток, 101 |
| `frame_milestone.png` | веха, особое достижение | звезда, 89 |
| `frame_trial.png` | опасное испытание | щит, 51 |
| `frame_tech.png` | техника и стройка | шестерня и квадрат, 62 |
| `frame_boss.png` | босс, кульминация | корона, 43 |
| `frame_home.png` | дом, люди, торговля | сердце и монета, 23 |

## Промпты

### `frame_step.png` — шаг

Самый частый тип: рамка спокойная, не спорит с остальными.

```
A single round medallion frame for a quest icon in a magical fantasy game, seen straight from the front, perfectly circular and perfectly centered, filling the whole square image so its outer edge touches all four sides.
Theme: moonstone and silver. A slim ring of polished silver set with a band of pale blue moonstone, with faint engraved runes that glow a soft blue-white.
The ornament lives only in a ring along the outer edge, about one eighth of the diameter wide. Everything inside the ring is an empty, smooth, dark circular recess, about three quarters of the diameter, with only a faint soft glow — no objects, symbols or patterns in the middle, because a small item icon will be placed there.
Style: polished magical game UI, rich materials, soft magical glow, crisp clean edges. It must stay readable when shrunk to 64 pixels: bold shapes and strong contrast between the bright ring and the dark middle, no tiny noisy details. Materials inspired by Minecraft.
Outside the circle: a pure flat black background.
No text, no letters, no numbers, no logos, no watermark, no character, no item in the middle.
Aspect ratio: 1:1 (square).
```

### `frame_expedition.png` — экспедиция

```
A single round medallion frame for a quest icon in a magical fantasy game, seen straight from the front, perfectly circular and perfectly centered, filling the whole square image so its outer edge touches all four sides.
Theme: an explorer's compass. A ring of aged, warm brass engraved with fine map lines, with four small compass points at the top, right, bottom and left, glowing with a warm amber light like a lantern.
The ornament lives only in a ring along the outer edge, about one eighth of the diameter wide. Everything inside the ring is an empty, smooth, dark circular recess, about three quarters of the diameter, with only a faint soft glow — no objects, symbols or patterns in the middle, because a small item icon will be placed there.
Style: polished magical game UI, rich materials, soft magical glow, crisp clean edges. It must stay readable when shrunk to 64 pixels: bold shapes and strong contrast between the bright ring and the dark middle, no tiny noisy details. Materials inspired by Minecraft.
Outside the circle: a pure flat black background.
No text, no letters, no numbers, no logos, no watermark, no character, no item in the middle.
Aspect ratio: 1:1 (square).
```

### `frame_milestone.png` — веха, особое достижение

```
A single round medallion frame for a quest icon in a magical fantasy game, seen straight from the front, perfectly circular and perfectly centered, filling the whole square image so its outer edge touches all four sides.
Theme: amethyst and starlight. A ring of violet amethyst crystal shards set in bright silver, with eight small star-shaped points evenly around it, sparkling with a violet and white magical glow.
The ornament lives only in a ring along the outer edge, about one eighth of the diameter wide. Everything inside the ring is an empty, smooth, dark circular recess, about three quarters of the diameter, with only a faint soft glow — no objects, symbols or patterns in the middle, because a small item icon will be placed there.
Style: polished magical game UI, rich materials, soft magical glow, crisp clean edges. It must stay readable when shrunk to 64 pixels: bold shapes and strong contrast between the bright ring and the dark middle, no tiny noisy details. Materials inspired by Minecraft.
Outside the circle: a pure flat black background.
No text, no letters, no numbers, no logos, no watermark, no character, no item in the middle.
Aspect ratio: 1:1 (square).
```

### `frame_trial.png` — опасное испытание

```
A single round medallion frame for a quest icon in a magical fantasy game, seen straight from the front, perfectly circular and perfectly centered, filling the whole square image so its outer edge touches all four sides.
Theme: a dangerous trial. A heavy ring of blackened iron with rivets and short sharp spikes, carved with crimson runes that glow like redstone embers.
The ornament lives only in a ring along the outer edge, about one eighth of the diameter wide. Everything inside the ring is an empty, smooth, dark circular recess, about three quarters of the diameter, with only a faint soft glow — no objects, symbols or patterns in the middle, because a small item icon will be placed there.
Style: polished magical game UI, rich materials, soft magical glow, crisp clean edges. It must stay readable when shrunk to 64 pixels: bold shapes and strong contrast between the bright ring and the dark middle, no tiny noisy details. Materials inspired by Minecraft.
Outside the circle: a pure flat black background.
No text, no letters, no numbers, no logos, no watermark, no character, no item in the middle.
Aspect ratio: 1:1 (square).
```

### `frame_tech.png` — техника и стройка

```
A single round medallion frame for a quest icon in a magical fantasy game, seen straight from the front, perfectly circular and perfectly centered, filling the whole square image so its outer edge touches all four sides.
Theme: magical clockwork. A ring of interlocking brass gear teeth and riveted copper plates, with thin lines of glowing cyan energy running along it, like a steampunk machine powered by magic.
The ornament lives only in a ring along the outer edge, about one eighth of the diameter wide. Everything inside the ring is an empty, smooth, dark circular recess, about three quarters of the diameter, with only a faint soft glow — no objects, symbols or patterns in the middle, because a small item icon will be placed there.
Style: polished magical game UI, rich materials, soft magical glow, crisp clean edges. It must stay readable when shrunk to 64 pixels: bold shapes and strong contrast between the bright ring and the dark middle, no tiny noisy details. Materials inspired by Minecraft.
Outside the circle: a pure flat black background.
No text, no letters, no numbers, no logos, no watermark, no character, no item in the middle.
Aspect ratio: 1:1 (square).
```

### `frame_boss.png` — босс, кульминация

```
A single round medallion frame for a quest icon in a magical fantasy game, seen straight from the front, perfectly circular and perfectly centered, filling the whole square image so its outer edge touches all four sides.
Theme: a legendary boss. An ornate ring of royal gold with a crown motif and gold laurel leaves worked into it, set with deep red rubies, wrapped in a fiery orange magical glow. Everything stays inside the circle: no crown points or leaves sticking out.
The ornament lives only in a ring along the outer edge, about one eighth of the diameter wide. Everything inside the ring is an empty, smooth, dark circular recess, about three quarters of the diameter, with only a faint soft glow — no objects, symbols or patterns in the middle, because a small item icon will be placed there.
Style: polished magical game UI, rich materials, soft magical glow, crisp clean edges. It must stay readable when shrunk to 64 pixels: bold shapes and strong contrast between the bright ring and the dark middle, no tiny noisy details. Materials inspired by Minecraft.
Outside the circle: a pure flat black background.
No text, no letters, no numbers, no logos, no watermark, no character, no item in the middle.
Aspect ratio: 1:1 (square).
```

### `frame_home.png` — дом, люди, торговля

```
A single round medallion frame for a quest icon in a magical fantasy game, seen straight from the front, perfectly circular and perfectly centered, filling the whole square image so its outer edge touches all four sides.
Theme: home and friendship. A living ring woven from oak branches with green leaves and small flowers, set with a few small emeralds, giving off a gentle warm green glow.
The ornament lives only in a ring along the outer edge, about one eighth of the diameter wide. Everything inside the ring is an empty, smooth, dark circular recess, about three quarters of the diameter, with only a faint soft glow — no objects, symbols or patterns in the middle, because a small item icon will be placed there.
Style: polished magical game UI, rich materials, soft magical glow, crisp clean edges. It must stay readable when shrunk to 64 pixels: bold shapes and strong contrast between the bright ring and the dark middle, no tiny noisy details. Materials inspired by Minecraft.
Outside the circle: a pure flat black background.
No text, no letters, no numbers, no logos, no watermark, no character, no item in the middle.
Aspect ratio: 1:1 (square).
```
