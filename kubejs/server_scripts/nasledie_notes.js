// Loose pages of the First Expedition, added to chests where its members went (lore only: no quest checks them).
// Loot table IDs come from the mod JARs (structure NBT and data/*/loot_tables). Lootr rolls each player's copy
// separately, so Maxim and Yura can each find their own page. A written book title must stay within 32 characters
// (WrittenBookItem.makeSureTagIsValid), otherwise the client shows "Invalid book tag".
var NasledieNotes = (function () {
    var notes = [
        {table: 'mowziesmobs:chests/monastery_chest', chance: 3, title: 'Тропа к отшельнику', author: 'Сигрид Линд',
            pages: ['Старик наверху не пускает тех, кто строит или летит. Только ногами.\n\nЭклунд злился полдня — и полез.',
                'Наверху Эклунд долго говорил с ним один. Спустился молча и до вечера ничего не записывал.']},
        {table: 'mowziesmobs:chests/umvuthana_grove_chest', chance: 3, title: 'Маска за компас', author: 'Эйнар Холм',
            pages: ['Отдал компас за маску. Без маски в рощу не пустят, а в маске не выпустят, если узнают.\n\nЭклунд сказал — пустяки. Ему легко говорить, маску ношу я.']},
        {table: 'betterstrongholds:chests/grand_library', chance: 2, title: 'Выписки из библиотеки', author: 'Торвальд Эклунд',
            pages: ['Письмена у портала моложе остальных. Кто-то из Зодчих вернулся сюда уже после обряда.',
                'Значит, из сосуда можно выйти.\n\nА если можно выйти — можно и войти.']},
        {table: 'minecraft:chests/ancient_city', chance: 4, title: 'Обломок таблички', author: 'Неизвестный Зодчий',
            pages: ['…и каждый, кто отдаёт голос, слышит после только стражу.\n\nМы согласны.\nМы согласны.\nМы…']},
        {table: 'cataclysm:chests/desert_treasure', chance: 3, title: 'Под храмом — ещё храм', author: 'Эйнар Холм',
            pages: ['Пустынники строили поверх старого. Под их храмами — кладка Зодчих, а под ней ещё одна.\n\nСколько раз этот мир уже чинили?']},
        {table: 'cataclysm:chests/frosted_prison_treasure', chance: 3, title: 'Пар у входа', author: 'Ингрид Берг',
            pages: ['Драугры не дышат, а у входа идёт пар. Здесь кто-то ещё живой.\n\nИли помнит, как это — быть живым.']},
        {table: 'cataclysm:chests/acropolis_treasure', chance: 3, title: 'Восемь швов', author: 'Сигрид Линд',
            pages: ['Отсюда видны все швы сразу. Я отметила их на карте — восемь, как он и говорил.',
                'Он знал заранее.\n\nОткуда?']},
        {table: 'cataclysm:chests/abandoned_treasure', chance: 3, title: 'Записка Странда', author: 'Улоф Странд',
            pages: ['Если найдёте мой ящик с инструментом — берите, мне он не понадобится.\n\nШучу. Наверное.']},
        {table: 'alexscaves:chests/forlorn_ruins', chance: 3, title: 'Обрывок, рука Берг', author: 'Ингрид Берг',
            pages: ['Они видят в темноте не глазами. Я закрыла глаза — и тоже увидела.\n\nНе ищите меня.']},
        {table: 'alexscaves:chests/abyssal_ruins', chance: 3, title: 'Песня, выбитая в камне', author: 'Народ глубин',
            pages: ['Мы держали воду для тех, кто наверху.\nНаверху забыли.\nВода помнит.']}
    ];

    function quote(text) {
        return '"' + String(text).replace(/\\/g, '\\\\').replace(/"/g, '\\"') + '"';
    }

    // SNBT for minecraft:set_nbt; pages are JSON text components, as in a signed book.
    function bookTag(note) {
        var pages = note.pages.map(function (page) { return quote(JSON.stringify({text: page})); });
        return '{title:' + quote(note.title) + ',author:' + quote(note.author) + ',pages:[' + pages.join(',') + ']}';
    }

    function entry(note) {
        return {type: 'minecraft:item', name: 'minecraft:written_book',
            functions: [{function: 'minecraft:set_nbt', tag: bookTag(note)}]};
    }

    // ServerEvents.chestLootTables adds "chests/" to the path itself (LootEventJS.modify/addJson),
    // so 'mowziesmobs:chests/monastery_chest' is passed as 'mowziesmobs:monastery_chest'.
    function eventId(table) {
        var parts = table.split(':');
        if (parts.length !== 2 || parts[1].indexOf('chests/') !== 0) throw new Error('not a chest loot table: ' + table);
        return parts[0] + ':' + parts[1].substring('chests/'.length);
    }

    // One extra roll per chest: the page with weight 1 against `chance - 1` empty results (1 in `chance`).
    function register(event) {
        notes.forEach(function (note) {
            try {
                event.modify(eventId(note.table), function (table) {
                    table.addPool(function (pool) {
                        pool.setUniformRolls(1, 1);
                        pool.addEntry(entry(note)).weight(1);
                        pool.addEmpty(note.chance - 1);
                    });
                });
            } catch (e) {
                console.error('nasledie notes: ' + note.table + ': ' + e);
            }
        });
    }

    return {notes: notes, bookTag: bookTag, eventId: eventId, register: register};
})();

ServerEvents.chestLootTables(function (event) {
    NasledieNotes.register(event);
});
