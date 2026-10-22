// Exact API evidence and limitations: reviews/factory_trial_evidence.json.
// Server-only, bounded observations. Never writes machine inventory or persistent world data.
var NasledieFactoryTrials = (function () {
    var registries = Java.loadClass('net.minecraftforge.registries.ForgeRegistries');
    var recipes = {
        'createaddition:rolling_mill': {
            driver: 'createaddition:electric_motor', input: 'create:copper_sheet',
            product: 'createaddition:copper_wire', outputs: [2], extra: '',
            advancement: 'nasledie:alpha43/industry/electric_wire',
            prompt: 'Подайте один медный лист Create. Стан должен выпустить две проволоки.'
        },
        'create:millstone': {
            driver: 'createdieselgenerators:diesel_engine', input: 'minecraft:wheat',
            product: 'create:wheat_flour', outputs: [1, 3], extra: 'minecraft:wheat_seeds',
            advancement: 'nasledie:alpha43/industry/diesel_flour',
            prompt: 'Подайте одну пшеницу. Жернова должны выпустить муку на дизельном приводе.'
        }
    };
    var watches = {};
    var ticks = 0;
    var uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

    function key(block) { return block.x + ',' + block.y + ',' + block.z; }
    function equalEntity(a, b) { return a != null && b != null && a.equals(b); }
    function fail(message) { return {error: message}; }

    function trace(level, block, recipe) {
        var seen = {};
        var route = [];
        var network = null;
        for (var step = 0; step < 32; step++) {
            var posKey = key(block);
            if (seen[posKey]) return fail('В приводе обнаружен замкнутый путь. Дайте линии перестроиться и повторите измерение.');
            seen[posKey] = true;
            var entity = block.entity;
            if (!entity || typeof entity.getSpeed !== 'function' ||
                    !isFinite(Number(entity.getSpeed())) || Number(entity.getSpeed()) === 0 || entity.network == null) {
                return fail('Станок или его привод не вращается. Проверьте питание, соединения и перегрузку.');
            }
            var currentNetwork = String(entity.network);
            if (network == null) network = currentNetwork;
            if (network !== currentNetwork) return fail('Соединения привода ещё перестраиваются. Повторите измерение.');
            route.push(posKey);
            if (!entity.hasSource()) {
                var generated = Number(entity.getGeneratedSpeed());
                if (String(block.id) !== recipe.driver || !isFinite(generated) || generated === 0) {
                    return fail('Этот станок получает вращение от другого источника. Подключите привод, указанный в задании.');
                }
                if (recipe.driver === 'createdieselgenerators:diesel_engine') {
                    var fluid = entity.getTank().getFluid();
                    if (fluid.isEmpty() || String(registries.FLUIDS.getKey(fluid.getFluid())) !== 'createdieselgenerators:diesel') {
                        return fail('Для этого испытания нужен дизель в баке обычного дизельного двигателя.');
                    }
                }
                return {signature: network + '|' + route.join(';'), entity: entity};
            }
            var source = entity.source;
            // Check before getBlock/entity: an observation must never load a remote chunk.
            if (source == null || !level.hasChunkAt(source)) return fail('Часть привода сейчас не загружена. Для опыта соберите короткую линию рядом.');
            block = level.getBlock(source);
        }
        return fail('Привод слишком длинный для контрольного опыта. Используйте линию до 32 звеньев.');
    }

    function sample(level, block, recipe) {
        if (!level.hasChunkAt(block.pos)) return fail('Станок сейчас не загружен.');
        var entity = block.entity;
        if (String(block.id) !== recipe.station || !entity) return fail('Станок убран или заменён.');
        var origin = trace(level, block, recipe);
        if (origin.error) return origin;
        var input = entity.inputInv.getStackInSlot(0);
        var output = {product: 0, extra: 0, total: 0, unknown: false};
        for (var slot = 0; slot < entity.outputInv.getSlots(); slot++) {
            var stack = entity.outputInv.getStackInSlot(slot);
            var count = Number(stack.count);
            if (count <= 0) continue;
            output.total += count;
            if (String(stack.id) === recipe.product) output.product += count;
            else if (recipe.extra && String(stack.id) === recipe.extra) output.extra += count;
            else output.unknown = true;
        }
        return {machine: entity, origin: origin, timer: Number(entity.timer),
            input: String(input.id), count: Number(input.count), output: output};
    }

    function completed(previous, current, recipe) {
        return previous.timer > 0 && current.timer <= 0 &&
            previous.input === recipe.input && previous.count === 1 && current.count === 0 &&
            previous.output.total === 0 && !current.output.unknown &&
            recipe.outputs.indexOf(current.output.product) !== -1 &&
            current.output.extra >= 0 && current.output.extra <= 1;
    }

    function start(event, station) {
        if (String(event.hand) !== 'MAIN_HAND' || String(event.item.id) !== 'minecraft:clock') return;
        var player = event.player;
        if (!player.server) return;
        var uuid = String(player.uuid);
        if (!uuidPattern.test(uuid)) return;
        delete watches[uuid];
        try {
            var recipe = recipes[station];
            recipe.station = station;
            var current = sample(player.level, event.block, recipe);
            if (current.error) player.tell(current.error);
            else if (Object.keys(watches).length >= 8) player.tell('Все измерители заняты. Повторите немного позже.');
            else if (current.output.total !== 0 || current.count > 1 || (current.count === 1 && current.input !== recipe.input)) {
                player.tell('Освободите выход станка. Для контрольного опыта оставьте на входе одну нужную заготовку или пустой слот.');
            } else {
                watches[uuid] = {recipe: recipe, x: event.block.x, y: event.block.y, z: event.block.z,
                    pos: event.block.pos, dimension: String(player.level.dimension), until: ticks + 1200, previous: current};
                player.tell('Измерение начато на одну минуту. Отключите автоподачу и выгрузку, оставайтесь рядом. ' + recipe.prompt);
            }
        } catch (error) {
            console.error('[Nasledie factory trials] Cannot start: ' + error);
            player.tell('Не удалось начать измерение. Подробности есть в журнале сервера.');
        }
        // Keep the station GUI closed during the clock's measurement interaction.
        event.cancel();
    }

    function tick(server) {
        ticks++;
        Object.keys(watches).forEach(function (uuid) {
            var watch = watches[uuid];
            var player = server.getPlayer(uuid);
            if (!player) { delete watches[uuid]; return; }
            try {
                var dx = Number(player.x) - (watch.x + 0.5);
                var dy = Number(player.y) - (watch.y + 0.5);
                var dz = Number(player.z) - (watch.z + 0.5);
                if (ticks >= watch.until || !player.isAlive() || String(player.level.dimension) !== watch.dimension || dx * dx + dy * dy + dz * dz > 256) {
                    delete watches[uuid];
                    player.tell('Измерение завершено без зачёта. Вернитесь к станку и начните новый контрольный опыт.');
                    return;
                }
                if (!player.level.hasChunkAt(watch.pos)) {
                    delete watches[uuid];
                    player.tell('Станок сейчас не загружен. Начните новый опыт после возвращения.');
                    return;
                }
                var block = player.level.getBlock(watch.x, watch.y, watch.z);
                var current = sample(player.level, block, watch.recipe);
                var previous = watch.previous;
                if (current.error || !equalEntity(current.machine, previous.machine) ||
                        !equalEntity(current.origin.entity, previous.origin.entity) || current.origin.signature !== previous.origin.signature) {
                    delete watches[uuid];
                    player.tell(current.error || 'Во время измерения изменился привод или станок. Начните новый опыт.');
                    return;
                }
                if (completed(previous, current, watch.recipe)) {
                    delete watches[uuid];
                    // Server command source: no operator rights are required from the player.
                    // Target is a validated UUID and advancement is a constant from recipes above.
                    server.runCommandSilent('advancement grant ' + uuid + ' only ' + watch.recipe.advancement);
                    player.tell('Готово: станок обработал заготовку от нужного привода. Производственный цикл подтверждён.');
                    return;
                }
                if (current.output.total !== 0 || current.count > 1 ||
                        (current.count === 1 && current.input !== watch.recipe.input) ||
                        (previous.count === 1 && current.count === 0)) {
                    delete watches[uuid];
                    player.tell('Контрольная партия изменилась или продукт забрали слишком рано. Освободите выход, отключите автоматику и повторите опыт с одной заготовкой.');
                    return;
                }
                watch.previous = current;
            } catch (error) {
                delete watches[uuid];
                console.error('[Nasledie factory trials] Observation stopped: ' + error);
                player.tell('Измерение прервано без зачёта. Подробности есть в журнале сервера.');
            }
        });
    }

    Object.keys(recipes).forEach(function (station) {
        BlockEvents.rightClicked(station, function (event) { start(event, station); });
    });
    ServerEvents.tick(function (event) { tick(event.server); });
    ServerEvents.unloaded(function () { watches = {}; });
    return {completed: completed};
})();
