// Story lines in item tooltips (client side). Eye targets come from L_Ender's Cataclysm 3.31 tags
// data/cataclysm/tags/worldgen/structure/eye_of_*_located.json; the void eye uses eye_of_ruined_located.
var NasledieTooltips = (function () {
    var lines = {
        'cataclysm:flame_eye': ['Око Зодчих. Ведёт к Пылающей арене,', 'где рыцарь до сих пор помнит присягу.'],
        'cataclysm:abyss_eye': ['Око Зодчих. Ведёт к затонувшему городу,', 'где заперта чужая боль.'],
        'cataclysm:storm_eye': ['Око Зодчих. Ведёт к акрополю в небе.', 'У его подножия Линд писала в последний раз.'],
        'cataclysm:mech_eye': ['Око Зодчих. Ведёт к древней фабрике.', 'Странд дошёл до неё первым.'],
        'cataclysm:monstrous_eye': ['Око Зодчих. Ведёт к кузне душ,', 'где кузнец стал собственной наковальней.'],
        'cataclysm:desert_eye': ['Око Зодчих. Ведёт к проклятой пирамиде.', 'Холм оттуда не вернулся.'],
        'cataclysm:cursed_eye': ['Око Зодчих. Ведёт к ледяной тюрьме,', 'где король сторожит свою стражу.'],
        'cataclysm:void_eye': ['Око Зодчих. Ведёт к разрушенной цитадели —', 'к последнему доспеху.'],
        'cataclysm:void_core': ['Сердце последнего доспеха. Пустое.'],
        'minecraft:nether_star': ['Три души, сплавленные в одну.'],
        'mowziesmobs:sol_visage': ['Холм отдал за такую маску свой компас.'],
        'alexscaves:tremorzilla_egg': ['Сосуд, который выберет сам.'],
        'alexsmobs:mysterious_worm': ['Зодчие закрыли пустоту островами.', 'Не бросайте это вниз. Или бросайте.']
    };

    function register(event) {
        Object.keys(lines).forEach(function (item) {
            event.add(item, lines[item].map(function (line) { return Text.darkGray(line); }));
        });
    }

    return {lines: lines, register: register};
})();

ItemEvents.tooltip(function (event) {
    NasledieTooltips.register(event);
});
