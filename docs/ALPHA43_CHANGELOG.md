# Журнал изменений Alpha 43

База — `main` после PR #3 (`bf2a0d9`, Alpha 42: 18 глав, 485 квестов). Ветка
`claude/eloquent-goodall-qera4e`. Minecraft не запускался: всё ниже проверено статически
(валидатор, тесты, разбор JAR модов), а не в игре.

## Что сделано

Квестбук переписан как одна история «Наследие нового мира» в четырёх актах и финале
(сюжет — `docs/STORY.md`, план — `docs/ALPHA43_PLAN.md`).

| # | Глава | Alpha 42 | Alpha 43 | Ссылок | Суть изменений |
|---|---|---|---|---|---|
| 0 | Летопись Первой экспедиции | 4 (Пролог) | 29 | — | Сюжетный хребет: 25 записей дневника, все боссы, финал |
| 1 | Дом, к которому возвращаются | 18 | 22 | — | Быт, огород, кухня, рюкзаки |
| 2 | Люди нашего поселения | 10 | 36 | — | MCA, Recruits/Workers, защита деревни, чужие деревни CTOV и Towns and Towers |
| 3 | Дорога за горизонт | 20 | 31 | — | Биомы Terralith, обелиски, сундуки, подземелья YUNG |
| 4 | Археология — по следам Холма | 23 | 24 | 1 | Действия внутри раскопов вместо посещений |
| 5 | Атлас Линд — дальние экспедиции | 38 | 35 | 1 | Сокровищницы данжей вместо посещений |
| 6 | Звери и стражи старого мира | 25 | 19 | 5 | Охота на боссов Mowzie's |
| 7 | Океан — проводник и монумент | 21 | 18 | 1 | Корабли, руины, монумент |
| 8 | Нижний мир — огонь и черепа | 20 | 21 | 2 | Крепости, бастион, визер |
| 9 | Мастерская — первые машины | 41 | 36 | — | Вехи Create вместо пересказа достижений |
| 10 | Промышленность и артиллерия | 27 | 34 | 2 | Энергия, дизель, Big Cannons, победы артиллерией |
| 11 | Дороги нового мира | 18 | 23 | — | Поезда, самолёты, путевые камни |
| 12 | Торговый дом | 9 | 9 | — | Торговля, свой торговец, лавка Create |
| 13 | Великие проекты | 26 | 25 | — | Производственные испытания |
| 14 | Легенды глубин | 78 | 54 | 4 | Alex's Caves: шесть лучей, подземные стражи |
| 15 | Восемь очей Зодчих | 28 | 33 | 10 | Восемь логов Катаклизма лучами |
| 16 | Край — конец пути | — | 15 | 4 | **Новая**: Край, Червь пустоты, эпилог |
| 17 | Бестиарий Ингрид Берг | 58 | 35 | 1 | Alex's Mobs: приручения и редкие встречи |
| 18 | Кабинет редкостей | 21 | 11 | — | Восемь коллекций Relics по краям мира |

Итого: 19 глав, 510 квестов, 566 задач, 1107 наград, 26 книг-записей.

**История в самих модах** (`kubejs/`): сюжетные имена боссов Катаклизма и Mowzie's
(русский язык), подсказки к восьми очам Зодчих и сюжетным предметам, десять страниц
экспедиции в сундуках мест, где она побывала. Подробно — `docs/STORY.md`, раздел «История в модах».

## Найденные и исправленные ошибки

| Где | Было | Стало | Как проверено | Риск |
|---|---|---|---|---|
| 5 задач FTB `kill` (океан, Нижний мир, летопись) | Без `value`: `KillTask.readData` читает `getLong("value")`, отсутствующий ключ = цель 0 убийств | `value: 1`; валидатор отвергает `kill`/`stat` без положительного `value` | Байткод FTB Quests 2001.4.22, тест `tests/test_validate.py` | Поведение задачи с целью 0 в игре не наблюдалось |
| «Восемь побед Катаклизма» | Достижение `cataclysm:kill_all_bosses`: все 8 добивающих ударов должен нанести один игрок | Восемь FTB-задач `kill`, прогресс общий на команду | JSON достижения в JAR Cataclysm 3.31 | Победы до установки Alpha 43 не засчитаются |
| Книга «Последняя запись Торвальда Эклунда» | Название 34 символа: клиент показывает «Неверные данные книги» | «Последняя запись Эклунда»; сборщик и валидатор ограничивают название 32 символами | Байткод клиента 1.20.1 (`WrittenBookItem.makeSureTagIsValid`) | — |
| Награда за дракона | Элитры — сразу засчитали бы квест «Крылья с корабля» | Голова дракона и тотем хоруса | Валидатор `reward_completes_task` | — |
| Награды Alpha 42 | Подарки закрывали следующие квесты, тройное оружие, дорогие устройства за мелкие шаги | Пересмотрены по главам (`docs/REWARD_POLICY.md`) | Валидатор, `references/registry.json` | Баланс в игре не измерялся |
| Повторное использование ID | Два квеста сменили смысл при старом ID | Новые ID («Все сокровищницы YUNG», «Огненный стержень») | `tools/book_diff.py` | — |
| Формы crown, star, scroll, shield, coin, laurel, ribbon (из Alpha 42) | `shape.png` — серая маска без альфа-канала; Minecraft читает текстуры как RGBA, и маска становится непрозрачным тёмным квадратом под значком | Белая маска с прозрачностью, как у форм FTB; валидатор отвергает маску без альфы | Байткод клиента 1.20.1 (`NativeImage.read` → формат RGBA), превью `--screen` | Вид в игре не наблюдался |
| Тема: `container_slot`, `text_box` (из Alpha 42) | `… + color=#24374B`: FTB Library читает `color=#24374B` как путь к ресурсу, а `=` и `#` в пути — исключение | `… + #24374B; padding=1`; валидатор проверяет значки темы | Байткод FTB Library 2001.2.13 (`Icon.getIcon0`) | — |
| Все ID книги (из Alpha 42 и новые) | 1111 ID с первой цифрой 8–F. FTB Quests читает ID знаковым `Long.parseLong(hex, 16)`: такие объекты при каждой загрузке получали случайный ID (прогресс и зависимости терялись), а ссылка на квест с таким ID роняла сервер — **мир не загружался** | ID с той же записью без старшего бита (`A0BE…` → `20BE…`), задачи и награды перенумерованных квестов — новые ID; генератор выдаёт только допустимые ID, валидатор (`id_unreadable`) и сборщик темы проверяют диапазон | Лог игры 2026-10-23 (`QuestLink.readData`), байткод FTB Quests 2001.4.22 (`BaseQuestFile.readID`, `newID` = `Math.abs`); новая книга совпадает со старой с точностью до ID | Сохранения с Alpha 43 не грузились, терять нечего; в мирах Alpha 42 эти ID и так менялись при каждой загрузке |
| «Фуражка дежурного по станции» | Достижение проверяло `railways:conductor_cap` — в Steam Rails 1.7.3 есть только модель, а предметы — 16 цветных фуражек; достижение не загружалось | Тег `railways:conductor_caps`, значок — красная фуражка | Теги и классы JAR Steam Rails 1.7.3, лог игры | — |
| Награды «Латунь для самостоятельной фабрики» и «Дробилка начинает вращаться» | `createaddition:multimeter` и `createaddition:heater` — только модели, в Create Crafts & Additions 1.3.3 таких предметов нет | 4 электронные лампы; 16 рудного цинка | Классы и данные JAR; индекс теперь отмечает «предметы без названия» (`item_unconfirmed`) | — |

## Влияние на существующие сохранения

Автор разрешил не беречь прогресс старого мира (2026-10-22). Что ожидать по правилам FTB Quests
(в игре не проверялось):
- прогресс хранится по ID; квесты с удалёнными ID просто исчезают из книги;
- квест с сохранённым ID, уже выполненный, остаётся выполненным, даже если его проверка теперь строже;
  невыполненный потребует нового действия (например, сокровищницу вместо посещения структуры);
- новые задачи `kill` и достижения засчитывают только события после установки;
- для честного игрового теста надёжнее новый мир.

## Дополнение: чужие деревни (2026-10-23)

По решению автора задействованы моды, которых книга почти не касалась. В «Людях нашего поселения» —
12 необязательных квестов: веер CTOV от «Города за холмами» (деревня в кронах, праздничная деревня,
ночь в укреплённой деревне, сундук грибного дома), веер Towns and Towers от новой «Деревни другого
уклада» (свайный дом, деревня под сакурой, пуэбло и типи, лагерь торговцев, северяне, горный трактир)
и «Арсенал разбойников» после «Защитников деревни». Проверки — действия внутри постройки: торговля
(`trade_in`), сон (`slept_in`), открытие сундука своей таблицы добычи. Какие постройки вообще появляются
с установленными биомами — проверено по тегам JAR: иберийская, нильская, рустикальная и пиглинская
деревни T&T требуют биомов других модов и в книгу не взяты; подземные деревни CTOV отключены самим модом.

## Дополнение: фоны глав (2026-10-23)

У каждой главы свой полноэкранный фон — картинки автора (`art/backgrounds/`), подготовленные
`tools/backgrounds.py`: исходное разрешение, светлые картинки равномерно затемнены (см. «оформление квестов»).
Фон задаётся в теме селектором главы (`background`), `bg_global.png` — запасной для остальных экранов.
Раньше фон был прозрачным, поэтому контекстное меню и окно квеста тоже были прозрачными; теперь у них
сплошная тёмная подложка (`context_menu`, `quest_view_background`). Квесты, награды и ID не менялись.
Как это выглядит в настоящем интерфейсе FTB, проверяется в игровом тесте.

## Дополнение: оформление квестов (2026-10-23)

По отзыву после первого запуска:
- **Связи** — плавные кривые без углов вместо прямых линий FTB со стрелками-«ёлочками». FTB умеет только прямые,
  поэтому кривые — картинки главы под квестами (`tools/curves.py`, 366 картинок): база в цвете «не пройдено»
  и для каждого квеста-условия — его исходящие связи в цвете «пройдено», они появляются после выполнения.
  Путь, который поворачивает, огибает узел дугой; боковое ответвление отходит плавно, как железнодорожная стрелка.
  Прямые линии FTB скрыты (`default_hide_dependency_lines`, прозрачные цвета линий в теме).
- **Медальоны** — целиком, без обрезки украшений; середина светится цветом рамки (фиолетовым у вех, красным
  у испытаний…); значок предмета меньше (`icon_scale` 0.6) и всегда внутри.
- **Фоны глав** — исходные картинки автора в своём разрешении (1672×941), только равномерно затемнённые:
  гамма, «день в ночь», размытие и виньетка испортили картинки и убраны.
- **Значки квестов** — круглые медальоны одного вида вместо девяти разных форм (стандартные FTB и формы Alpha 42
  выглядели вразнобой). Рамки нарисовал автор (`art/frames/`), типы:

  | Было | Стало |
  |---|---|
  | `circle` | `step` — шаг |
  | `scroll` | `expedition` — экспедиция |
  | `star` | `milestone` — веха |
  | `shield` | `trial` — испытание |
  | `gear`, `square` | `tech` — техника и стройка |
  | `crown` | `boss` — босс |
  | `heart`, `coin` | `home` — дом, люди, торговля |

  Каждому квесту — `icon_scale` (сейчас 0.6), чтобы значок помещался в рамку. Текстуры форм Alpha 42
  (`crown`, `laurel`, `ribbon`, `scroll`, `shield`, `coin`, `star`) больше не используются и удалены.
  Квесты, задачи, награды и ID не менялись — меняются только поля `shape`, `default_quest_shape` и `icon_scale`.

## Дополнение: перенумерация ID (2026-10-23)

Первый запуск Alpha 43 упал при загрузке мира: FTB Quests 2001.4.22 не читает ID больше `7FFFFFFFFFFFFFFF`
(подробно — строка «Все ID книги» в таблице ошибок). Перенумерованы 1512 ID из 2238: 1111 «невозможных»
(213 из них пришли из Alpha 42 и в игре никогда не держались) и 401 ID задач и наград внутри этих квестов.
Ни один новый ID не совпадает с ID Alpha 42 или прежней Alpha 43; ID Alpha 42 ниже `8000000000000000` не тронуты.
Таблица «старый → новый» — `reviews/id_remap_alpha43.json`. Квесты, задачи, награды, тексты и координаты
не менялись — проверено сравнением книги до и после с точностью до ID. Для игрового теста нужен новый мир
и полностью удалённая папка `config/ftbquests/quests/`: после неудачной загрузки FTB мог записать туда
недогруженную книгу.

## Приложение: ID относительно Alpha 42

Сформировано командой `python tools/book_diff.py <распакованный bf2a0d9>` до перенумерации ID 2026-10-23:
ID с первой цифрой 8–F ниже указаны старыми, новые — в `reviews/id_remap_alpha43.json`.

База: 485 квестов, сейчас: 510. Сохранено ID: 391, удалено: 94, новых: 119, перенесено между главами: 39, сохранили ID при новой проверке: 41.

Новые квесты по главам: village 27, exploration 17, cataclysm 14, chronicle 10, finale 9, netheritage 9, relics 9, compass 5, life 4, transport 4, archeology 3, defense 3, economy 3, industry 2

### Удалённые квесты

| ID | Глава | Название | Проверка |
|---|---|---|---|
| `88ABBD5262DB0432` | archeology | Обелиск среди песков | structure betterarcheology:desert_obelisk |
| `36816E6DCCAC9776` | compass | Найти лагерь торговцев | structure dungeons_arise:merchant_campsite |
| `125225CC968ECEB1` | compass | Найти лесную смотровую башню | structure nova_structures:firewatch_tower_forest |
| `8C486E24C425E49B` | compass | Найти подземную хижину | structure terralith:underground_cabin |
| `C98BCEC5872D8647` | compass | Найти пустынную заставу | structure terralith:desert_outpost |
| `E74BE19F5E31D304` | compass | Найти укреплённую деревню | structure terralith:fortified_village |
| `12202D6F529C409B` | compass | Найти шпиль Terralith | structure terralith:spire |
| `52B457F0F3B0109A` | compass | Освоить поиск компасом | advancement explorerscompass:repair_explorers_compass |
| `EB2746965E47F745` | compass | Подготовить обычный компас | advancement explorerscompass:explorers_compass |
| `1C477D2FE85FE89C` | create | Вода в мастерской | advancement create:water_supply |
| `078DEE5AC16D0721` | create | Картон с гербом | advancement create:cardboard_armor_trim |
| `E151ABC26C849155` | create | Обслуживание больших запасов | advancement create:hose_pulley |
| `8EC3094B2671ABF2` | create | Увидеть поток | advancement create:glass_pipe |
| `D49CAFA761D24CA4` | economy | Первая прибыль | advancement nasledie:economy/earned_emerald |
| `E03032475F008D4D` | economy | Редстоун через рынок | advancement nasledie:economy/bought_redstone |
| `D15B25FAA41E05AE` | economy | Стекло для стройки | advancement nasledie:economy/bought_glass |
| `B31BCA46216D2DC6` | economy | Хлеб к дороге | advancement nasledie:economy/bought_bread |
| `142D439350347E70` | exploration | Белые утёсы | biome terralith:white_cliffs |
| `D8325F832D406D1F` | exploration | Ледяное убежище | structure minecraft:igloo |
| `57FD47EFC4E11601` | exploration | Осенняя башня мага | structure terralith:mage_tower_autumn |
| `4654570D569F8AFB` | exploration | Пепельная саванна | biome terralith:ashen_savanna |
| `B7BA27A969107D22` | exploration | Старая шахта | structure bettermineshafts:mineshaft_oak |
| `4A366B92A0D4BDCD` | exploration | Хижина среди болот | structure minecraft:swamp_hut |
| `F740FB239378B229` | exploration | Цветущая долина | biome terralith:blooming_valley |
| `EA048E705BEC8414` | exploration | Шахта грибников | structure bettermineshafts:mineshaft_mushroom |
| `F09FD8875C97CD92` | exploration | Шахта красных пустошей | structure bettermineshafts:mineshaft_mesa |
| `28CBD873B6A9B3EA` | exploration | Шахта среди капельников | structure bettermineshafts:mineshaft_dripstone |
| `FBBF01EF727D4ABF` | guild | Благословение солнечной птицы | advancement alexsmobs:alexsmobs/sunbird_blessing |
| `3684E8517DD612A0` | guild | Вода для сухопутной прогулки | advancement alexsmobs:alexsmobs/mantis_shrimp_bucket |
| `F5D02EE894BC9AE7` | guild | Грибная болезнь москита | advancement alexsmobs:alexsmobs/crimson_mosquito_sick |
| `1BC5E19E384E37E0` | guild | Знакомство с каменным катком | advancement alexsmobs:alexsmobs/rocky_roller |
| `0FF56BD66615E8C4` | guild | Кормушка цветочного сада | advancement alexsmobs:alexsmobs/hummingbird_feeder |
| `51C3266BACCA8D53` | guild | Крокодил на близком расстоянии | advancement alexsmobs:alexsmobs/crocodile |
| `E0ECA7B8B4204545` | guild | Муравьи отвечают на визит | advancement alexsmobs:alexsmobs/stomp_leafcutter_anthill |
| `ABADB8973594E0A0` | guild | Наблюдатель у края мира | advancement alexsmobs:alexsmobs/farseer |
| `23B7EC4E576DFA6A` | guild | Наследники ледяной стаи | advancement alexsmobs:alexsmobs/breed_froststalker |
| `E0B32143847E9AF0` | guild | Последнее подземелье — среди лавы | advancement betterdungeons:small_nether_dungeon |
| `7FBCE407DFCAF42C` | guild | Слушать скрытые полости | advancement alexsmobs:alexsmobs/echolocator |
| `71006DAD7D01307F` | guild | Цветы для большого спутника | advancement alexsmobs:alexsmobs/acacia_blossom |
| `6CC28B3392054882` | guild | Эму уклоняется от выстрела | advancement alexsmobs:alexsmobs/emu_dodge |
| `E0FC9F1146B778E2` | legends | До взрыва жвачки | advancement alexscaves:alexscaves/defeat_gumbeeper |
| `7947BD2068E57CC5` | legends | Дорога из леденцов | advancement alexscaves:alexscaves/walk_on_rock_candy |
| `66EADAB24A1552E0` | legends | Зелье для мармеладного медведя | advancement alexscaves:alexscaves/feed_gummy_bear |
| `383DD6353CA94C12` | legends | Кнопка за сотней блоков | advancement alexscaves:alexscaves/remote_detonation |
| `2FD4730BC0FE9EAE` | legends | Мозг и сила токсичных глубин | advancement alexscaves:alexscaves/defeat_brainiac |
| `C133D2D8DF77C482` | legends | Мятный берсерк | advancement alexscaves:alexscaves/defeat_caniac |
| `70F6DFB37F774EB1` | legends | Наблюдать за тысячу блоков | advancement alexscaves:alexscaves/beholder_far_away |
| `99E7481EE409646E` | legends | Оставить рисунок на камне | advancement alexscaves:alexscaves/cave_painting |
| `B156B9A8303E6235` | legends | Охота первобытного мира | advancement alexscaves:alexscaves/defeat_big_dinosaur |
| `3EBA900FE44E6268` | legends | Подношение на глубинном алтаре | advancement alexscaves:alexscaves/pearl_on_abyssal_altar |
| `0AC844524C34131D` | legends | Потомство гроттоцератопсов | advancement alexscaves:alexscaves/breed_grottoceratops |
| `60FEF5A262F30317` | legends | Пять пассажиров доисторического поезда | advancement alexscaves:alexscaves/dinosaurs_minecart |
| `5F3AED9BBF4F1BB6` | legends | Река пурпурной газировки | advancement alexscaves:alexscaves/enter_purple_soda |
| `6E775F1F2C2EDC48` | legends | Рисунок неведомого великана | advancement alexscaves:alexscaves/mystery_cave_painting |
| `8A4368A1D28651AC` | legends | Свет для глаз глубины | advancement alexscaves:alexscaves/deepsight |
| `8DB19C7D42300F1B` | legends | Сладостей оказалось слишком много | advancement alexscaves:alexscaves/sugar_rush |
| `A7C984849A56D149` | legends | След туннельного грызуна | advancement alexscaves:alexscaves/defeat_corrodent |
| `22EF4B3D99CB8E8B` | legends | Суп для доисторического лесоруба | advancement alexscaves:alexscaves/feed_relicheirus |
| `03AF226767BF1BAC` | legends | Три блюда долгого хранения | advancement alexscaves:alexscaves/eat_radiation_foods |
| `A0718A921F867880` | legends | Угощение для гаммарака | advancement alexscaves:alexscaves/feed_gammaroach |
| `05BBD788896174D5` | legends | Участок Незера под обычным небом | advancement alexscaves:alexscaves/convert_nether_biome |
| `C3D9E46E5C4B9DA5` | life | Из отходов в почву | advancement farmersdelight:main/place_organic_compost |
| `6E42774EBA2B38FB` | life | Порядок на складе | advancement nasledie:alpha35/engineering/6e42774eba2b38fb |
| `FE2674FC9E1DD748` | life | Солома из урожая | advancement farmersdelight:main/harvest_straw |
| `E9E05E2FD9CC70E0` | netheritage | Найти багровую башню | structure nova_structures:nether_skeleton_tower_crimson |
| `3F66C4154E21D0F4` | netheritage | Найти базальтовую башню | structure nova_structures:nether_skeleton_tower_basalt |
| `AA22526FD2483C34` | netheritage | Найти башню душ | structure nova_structures:nether_skeleton_tower_soul |
| `510C765AAA37753C` | netheritage | Найти незерские пустоши | biome minecraft:nether_wastes |
| `32389AE05BB9940C` | netheritage | Найти незерское подземелье | structure betterdungeons:small_nether_dungeon |
| `C1CEC3D998651E9C` | netheritage | Отметить найденный замок | advancement nova_structures:nether/find_keep |
| `7714F8F0EED40559` | netheritage | Пересечь базальтовые дельты | biome minecraft:basalt_deltas |
| `F627CCC35580E95F` | netheritage | Победить ифрита | kill minecraft:blaze |
| `A19C3A7B7AF63B80` | ocean | Найти холодные океанские руины | structure minecraft:ocean_ruin_cold |
| `F805A24AC6136435` | ocean | Победить утопленника | kill minecraft:drowned |
| `37A42269B00D8373` | relics | Зеркало возвращения | item relics:magic_mirror |
| `C59D7785BCFC682D` | relics | Знак пройденного пути | item relics:spatial_sign |
| `B4210CAE7916EC4B` | relics | Кольцо для чужого бастиона | item relics:bastion_ring |
| `FC18B444C7E1629F` | relics | Коньки для ледяного пути | item relics:ice_skates |
| `7A6DE62914ABF934` | relics | Лошадь отправляется с вами | item relics:horse_flute |
| `0068C3492D5FEF60` | relics | Находка для долгого заплыва | item relics:amphibian_boot |
| `BF8C1895E9D7830E` | relics | Начало коллекции странностей | advancement artifacts:amateur_archaeologist |
| `6CD091542ED7E77D` | relics | Обувь морского странника | item relics:aqua_walker |
| `6E2FE392089D97DF` | relics | Ожерелье медузы | item relics:jellyfish_necklace |
| `2CB6F19A77F3D3C0` | relics | Опыт, который можно хранить | item relics:relic_experience_bottle |
| `B80C987F9AB03683` | relics | Ответ лесной находки | item relics:spore_sack |
| `E3EA2CF97420E989` | relics | Пояс дальнего дозора | item relics:hunter_belt |
| `2783FBF67E012E66` | relics | Пояс из затонувшей истории | item relics:drowned_belt |
| `43496821860704D3` | relics | Пояс коллекционера | item relics:leather_belt |
| `C3620DEF30C9A9E2` | relics | Ролики для длинной дороги | item relics:roller_skates |
| `95E67FB14F3417B2` | relics | Священный медальон | item relics:holy_locket |
| `02183638E5416B5E` | relics | Стрелы в одном месте | item relics:arrow_quiver |
| `AF5426942D7C2622` | relics | Ускоритель дальнего полёта | item relics:elytra_booster |
| `CC5ABE356CD75C8E` | relics | Шаг над раскалённым озером | item relics:magma_walker |
| `C1275FDF3B2F99C1` | village | Оборудовать пункт набора | advancement nasledie:alpha34/actions/9f9843eca3fe9e3d |

### ID сохранён, проверка уточнена

| ID | Глава | Название | Было | Стало |
|---|---|---|---|---|
| `01C584DB0BC6D1D4` | archeology | Артефакт ждёт исследователя | item betterarcheology:unidentified_artifact | advancement betterarcheology:unidentified_artifact |
| `19745F0470E73C17` | archeology | Зал древних светильников | structure betterarcheology:light_temple | advancement nasledie:q/archeology/light_temple |
| `A387D38D6E080261` | archeology | Катакомбы забытых жителей | structure betterarcheology:catacombs | advancement nasledie:q/archeology/catacombs |
| `718927C2E9263AAC` | archeology | Курган на зелёном холме | structure betterarcheology:tumulus_grassy | advancement nasledie:q/archeology/tumulus |
| `2BA185CBF139E3AF` | archeology | Осколок с неизвестной историей | item betterarcheology:artifact_shards | advancement betterarcheology:artifact_shards |
| `88352D47820D40B4` | archeology | Последний зал — под водой | structure betterarcheology:underwater_0 | advancement nasledie:q/archeology/underwater |
| `938F14F75C60045E` | archeology | Руины красной земли | structure betterarcheology:mesa_ruins | advancement nasledie:q/archeology/mesa_ruins |
| `FBF1AAEFC633EC9F` | archeology | Руины под песком | structure betterarcheology:buried_ruins_sand | advancement nasledie:q/archeology/buried_ruins |
| `316AFB9A561BE01E` | archeology | Храм под джунглями | structure betterarcheology:temple_jungle | advancement nasledie:q/archeology/jungle_temple |
| `B2584C9F3E1DF7E2` | cataclysm | Аметистовое гнездо | structure cataclysm:amethyst_nest | advancement nasledie:q/cataclysm/amethyst_nest |
| `DE6173A11D04779E` | cataclysm | Восемь побед Катаклизма | advancement cataclysm:kill_all_bosses | kill cataclysm:ignis; kill cataclysm:the_leviathan; kill cataclysm:the_harbinger; kill cataclysm:ender_guardian; kill cataclysm:maledictus; kill cataclysm:ancient_remnant; kill cataclysm:netherite_monstrosity; kill cataclysm:scylla |
| `1CB249497EF14D92` | cataclysm | Храм за пределами пирамиды | structure cataclysm:abandoned_temple | advancement nasledie:q/cataclysm/abandoned_temple |
| `79C6E9FC12713C40` | chronicle | Лагерь у старого раскопа | structure betterarcheology:archeologist_camp_grassy | structure #nasledie:archeologist_camps |
| `95734C53761E6456` | compass | Башни бандитов | structure dungeons_arise:bandit_towers | advancement nasledie:q/compass/bandit_towers |
| `3BFF245E8A4EEBE2` | compass | Большая шахтная система | structure dungeons_arise:mining_system | advancement nasledie:q/compass/mining_system |
| `5DB6F54ADA7C276F` | compass | Грибные шахты | structure dungeons_arise:mushroom_mines | advancement nasledie:q/compass/mushroom_mines |
| `B1509620769451B8` | compass | Дворец Шираз | structure dungeons_arise:shiraz_palace | advancement nasledie:q/compass/shiraz_palace |
| `C0194CADC20BB042` | compass | Дом над джунглями | structure dungeons_arise:jungle_tree_house | advancement nasledie:q/compass/tree_house |
| `1B7D417FC2AD346C` | compass | Заражённый храм | structure dungeons_arise:infested_temple | advancement dungeons_arise:find_infested_temple |
| `CEBF8266AC205E60` | compass | Колизей | structure dungeons_arise:coliseum | advancement dungeons_arise:find_coliseum |
| `973E6DFEEE903031` | compass | Крепость Кайры | structure dungeons_arise:keep_kayra | advancement nasledie:q/compass/keep_kayra |
| `BD1F1FA8837A8FC5` | compass | Монастырь с картами | structure dungeons_arise:monastery | advancement dungeons_arise:find_monasteries |
| `A13990B38C18BF50` | compass | Небесный всадник | structure dungeons_arise:heavenly_rider | advancement nasledie:q/compass/heavenly_rider |
| `9F4C744CFD45A276` | compass | Небесный завоеватель | advancement dungeons_arise:find_heavenly_conqueror | advancement nasledie:q/compass/heavenly_conqueror |
| `EF5D057D0A543404` | compass | Небесный претендент | advancement dungeons_arise:find_heavenly_challenger | advancement nasledie:q/compass/heavenly_challenger |
| `59752216F591E945` | compass | Снежный форт | structure nova_structures:stray_fort | advancement nasledie:q/compass/stray_fort |
| `225B6CD9BBAC0F47` | compass | Таверна у дороги | structure nova_structures:tavern_jungle | advancement nova_structures:adventure/find_tavern |
| `07C8419F1FE8738D` | compass | Чумной приют | structure dungeons_arise:plague_asylum | advancement nasledie:q/compass/plague_asylum |
| `F17A293356CD1404` | exploration | Заброшенная шахта | structure bettermineshafts:mineshaft_acacia | structure #nasledie:mineshafts |
| `E6DC4A843BE1C287` | exploration | Острова в небе | biome terralith:skylands_autumn | biome #nasledie:skylands |
| `418BF87D0F99A324` | finale | Поводок для спектра | advancement alexsmobs:alexsmobs/spectre | advancement nasledie:q/finale/spectre |
| `7E2ECDC313839529` | guild | Полевой дневник | advancement alexsmobs:alexsmobs/root | advancement nasledie:q/guild/field_journal |
| `831CD896CBC3B75D` | netheritage | Порт среди лавы | structure nova_structures:nether_port | advancement nasledie:q/netheritage/nether_port |
| `42CDC43E1DFBDB97` | ocean | Береговой маяк | structure dungeons_arise:lighthouse | advancement nasledie:q/ocean/lighthouse |
| `27C6A5C2087489CC` | ocean | Галера иллагеров | structure dungeons_arise:illager_galley | advancement nasledie:q/ocean/galley |
| `D5B701274F41916E` | ocean | Затонувший корабль | structure minecraft:shipwreck | advancement nasledie:q/ocean/shipwreck |
| `F70436662909AF80` | ocean | Клад по карте | item minecraft:heart_of_the_sea | advancement nasledie:q/ocean/buried_treasure |
| `75934B268BAE9806` | ocean | Корабль нежити | structure dungeons_arise:undead_pirate_ship | advancement nasledie:q/ocean/pirate_ship |
| `99935D46EBDDE471` | ocean | Корсарский корабль | structure dungeons_arise:illager_corsair | advancement nasledie:q/ocean/corsair |
| `E89F59FCDCE5619F` | ocean | Руины проводника | structure nova_structures:conduit_ruin | advancement nasledie:q/ocean/conduit_ruin |
| `6FD514AB841DF820` | ocean | Сундук подводных руин | structure minecraft:ocean_ruin_warm | advancement nasledie:q/ocean/ruin_chest |

### Перенесены в другую главу

| ID | Было | Стало | Название |
|---|---|---|---|
| `79C6E9FC12713C40` | archeology | chronicle | Лагерь у старого раскопа |
| `391F9987F1F32442` | cataclysm | chronicle | Фабрика Странда |
| `8792C39846E0D49E` | cataclysm | chronicle | Машина, которая помнит |
| `52813202FFECF301` | cataclysm | chronicle | Кузнец, ставший молотом |
| `92B1754C45756107` | cataclysm | chronicle | Рыцарь, принявший огонь |
| `64338CFBA5C5B699` | cataclysm | chronicle | Ключ всегда идёт первым |
| `A13ADF5DA222DA68` | cataclysm | chronicle | Король во льду |
| `A0BE4189EEE72883` | cataclysm | chronicle | Боль, ушедшая в глубину |
| `E3651E9F6E43FAEB` | cataclysm | chronicle | Последняя запись Линд |
| `4E228116310381E8` | cataclysm | chronicle | Последний доспех |
| `098405E74DFFDA00` | create | transport | Рельсовое происшествие |
| `4843AED5CE824450` | defense | chronicle | Пустой доспех |
| `A378D8F13118FF97` | defense | chronicle | Птица из солнца |
| `DF85EFBB8E452760` | defense | chronicle | Слово отшельника |
| `92AF3238F7B8776E` | defense | chronicle | Зверь зимы |
| `0EF67FFF73E6D383` | defense | industry | Песок будущих орудий |
| `35AB582E2E08DF86` | defense | industry | Наращиватель стволов |
| `35D125C19D556E7A` | defense | industry | Сверлильный станок |
| `17FE2073432FC7E0` | defense | industry | Основание орудия |
| `8EC3B7E438EA800A` | defense | industry | Механизм заряжания |
| `6F6CBC1AF7ABE154` | grand_projects | economy | Мы открыты! |
| `898102A102A9739A` | guild | exploration | Первое подземелье |
| `5086797B05BC7619` | guild | exploration | Паучья пещера |
| `5386AE04902DA4BF` | guild | exploration | Катакомбы беспокойных мертвецов |
| `93EA4AC90BB6F5E7` | guild | exploration | Крепость нежити |
| `418BF87D0F99A324` | guild | finale | Поводок для спектра |
| `50F2011C089DD095` | guild | finale | Эндер-грипп |
| `3C2AA39C0E1FDEF8` | guild | finale | Рыба? Жук? Космав! |
| `C5769170EBDD1A02` | guild | finale | Приманка для пустоты |
| `7C9F211F3C3FEE27` | guild | finale | Надо было по голове |
| `2DAF49A8C5352825` | guild | finale | Червь пустоты |
| `2A2A1ECDD23269E9` | legends | chronicle | Что пришло из темноты |
| `3E03C21C1C3001DF` | legends | chronicle | Мир до Зодчих |
| `FED39CE9F2148371` | legends | chronicle | Сосуд, который выбрал сам |
| `7561C2A49CE25872` | ocean | chronicle | Дозорный монумента |
| `CA2CFD219A124357` | prolog | chronicle | Чужой берег |
| `C322668146484A1C` | prolog | life | Нож повара |
| `42E5495CA00F5CC6` | prolog | life | Семена другого мира |
| `69525CBD49DF5FDB` | prolog | life | Рюкзак за плечами |
