// Executes the production script against explicit API models, not Minecraft.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const code = fs.readFileSync(path.join(__dirname, '../kubejs/server_scripts/nasledie_factory_trials.js'), 'utf8');
const UUID = '12345678-1234-1234-1234-123456789abc';
const SECOND = '12345678-1234-1234-1234-123456789def';

function fixture(mode = 'electric') {
    const diesel = mode === 'diesel';
    const state = {input: {id: 'minecraft:air', count: 0}, output: [], fuel: 'createdieselgenerators:diesel'};
    const blocks = new Map(), loaded = new Set(['0,0,0', '1,0,0']);
    const reads = [], grants = [], errors = [], clicks = {}, handlers = {};
    const key = p => `${p.x},${p.y},${p.z}`;
    function kinetic() {
        return {network: '9223372036854775000', speed: 32, source: null, generated: 32,
            getSpeed() { return this.speed; }, hasSource() { return this.source !== null; },
            getGeneratedSpeed() { return this.generated; }, equals(other) { return this === other; }};
    }
    const machine = kinetic(), engine = kinetic();
    machine.source = {x: 1, y: 0, z: 0}; machine.timer = 0;
    machine.inputInv = {getStackInSlot: () => state.input};
    machine.outputInv = {getSlots: () => 9, getStackInSlot: i => state.output[i] || {id: 'minecraft:air', count: 0}};
    engine.getTank = () => ({getFluid: () => ({isEmpty: () => !state.fuel, getFluid: () => state.fuel})});
    const station = diesel ? 'create:millstone' : 'createaddition:rolling_mill';
    blocks.set('0,0,0', {id: station, x: 0, y: 0, z: 0, pos: {x: 0, y: 0, z: 0}, entity: machine});
    blocks.set('1,0,0', {id: diesel ? 'createdieselgenerators:diesel_engine' : 'createaddition:electric_motor',
        x: 1, y: 0, z: 0, pos: {x: 1, y: 0, z: 0}, entity: engine});
    const level = {dimension: 'minecraft:overworld', hasChunkAt: p => loaded.has(key(p)),
        getBlock(x, y, z) {
            const k = typeof x === 'object' ? key(x) : key({x, y, z}); reads.push(k);
            assert.ok(loaded.has(k), 'must not access an unloaded block');
            return blocks.get(k);
        }};
    const players = {};
    const server = {getPlayer: id => players[id], runCommandSilent: command => { grants.push(command); return 1; }};
    function addPlayer(uuid) {
        return players[uuid] = {uuid, level, server, x: 0, y: 0, z: 0, alive: true, messages: [],
            isAlive() { return this.alive; }, tell(text) { this.messages.push(text); },
            runCommandSilent() { throw new Error('must not require operator permission on player command source'); }};
    }
    const player = addPlayer(UUID);
    const context = vm.createContext({
        Java: {loadClass(name) { assert.equal(name, 'net.minecraftforge.registries.ForgeRegistries'); return {FLUIDS: {getKey: fluid => fluid}}; }},
        BlockEvents: {rightClicked: (id, callback) => { clicks[id] = callback; }},
        ServerEvents: {tick: callback => { handlers.tick = callback; }, unloaded: callback => { handlers.unloaded = callback; }},
        console: {error: message => errors.push(message)}
    });
    vm.runInContext(code, context, {filename: 'nasledie_factory_trials.js'});
    function click(p = player, item = 'minecraft:clock', hand = 'MAIN_HAND') {
        const event = {player: p, block: blocks.get('0,0,0'), hand, item: {id: item}, canceled: false,
            cancel() { this.canceled = true; }};
        clicks[station](event); return event;
    }
    const tick = () => handlers.tick({server});
    function begin() {
        state.input = {id: diesel ? 'minecraft:wheat' : 'create:copper_sheet', count: 1};
        machine.timer = 10; tick(); machine.timer = 5; tick();
    }
    function finish(count = diesel ? 1 : 2, seeds = 0) {
        state.input = {id: 'minecraft:air', count: 0}; machine.timer = 0;
        state.output = [{id: diesel ? 'create:wheat_flour' : 'createaddition:copper_wire', count}];
        if (seeds) state.output.push({id: 'minecraft:wheat_seeds', count: seeds});
        tick();
    }
    return {state, blocks, loaded, reads, grants, errors, machine, engine, level, players,
        player, server, handlers, addPlayer, click, tick, begin, finish};
}

test('electric cycle grants once from server source to the observing player', () => {
    const f = fixture(); assert.ok(f.click().canceled); f.begin(); f.finish(); f.tick();
    assert.deepEqual(f.grants, [`advancement grant ${UUID} only nasledie:alpha43/industry/electric_wire`]);
});
test('an unloaded station is not accessed during observation', () => {
    const f = fixture(); f.click(); f.begin();
    f.loaded.delete('0,0,0'); f.reads.length = 0; f.tick();
    assert.deepEqual(f.reads, []); assert.equal(f.grants.length, 0); assert.deepEqual(f.errors, []);
});
test('observations are bounded to eight players', () => {
    const f = fixture();
    for (let i = 0; i < 9; i++) {
        f.click(f.addPlayer(`12345678-1234-1234-1234-1234567890${i.toString().padStart(2, '0')}`));
    }
    f.begin(); f.finish(); assert.equal(f.grants.length, 8);
});
test('a source path longer than the 32-block bound cannot award credit', () => {
    const f = fixture();
    for (let x = 1; x <= 32; x++) {
        const pos = {x, y: 0, z: 0};
        f.loaded.add(`${x},0,0`);
        f.blocks.set(`${x},0,0`, {id: 'create:shaft', ...pos, pos,
            entity: {...f.engine, source: {x: x + 1, y: 0, z: 0}}});
    }
    const pos = {x: 33, y: 0, z: 0}; f.loaded.add('33,0,0');
    f.blocks.set('33,0,0', {id: 'createaddition:electric_motor', ...pos, pos, entity: f.engine});
    f.click(); f.begin(); f.finish(); assert.equal(f.grants.length, 0);
    assert.ok(!f.reads.includes('33,0,0'));
});
test('diesel milling accepts the real random flour bonus and seed byproduct', () => {
    const f = fixture('diesel'); f.click(); f.begin(); f.finish(3, 1);
    assert.deepEqual(f.grants, [`advancement grant ${UUID} only nasledie:alpha43/industry/diesel_flour`]);
});
test('already stored output cannot be presented as a fresh cycle', () => {
    const f = fixture(); f.state.output = [{id: 'createaddition:copper_wire', count: 2}];
    f.click(); f.state.output = []; f.begin(); f.finish(); assert.equal(f.grants.length, 0);
});
test('holding the product or injecting it without processing gives no credit', () => {
    const f = fixture(); f.click(); f.finish(); assert.equal(f.grants.length, 0);
});
test('a nearby electric motor does not qualify a water-wheel source chain', () => {
    const f = fixture(); f.blocks.get('1,0,0').id = 'create:water_wheel';
    f.click(); f.begin(); f.finish(); assert.equal(f.grants.length, 0);
});
test('inactive, invalid and overloaded drivers cannot pass', () => {
    for (const [field, value] of [['generated', 0], ['generated', NaN], ['speed', 0]]) {
        const f = fixture(); f.engine[field] = value; f.click(); f.begin(); f.finish();
        assert.equal(f.grants.length, 0, `${field}=${value}`);
    }
});
test('reverse rotation is valid when the correct driver is active', () => {
    const f = fixture(); f.machine.speed = f.engine.speed = f.engine.generated = -32;
    f.click(); f.begin(); f.finish(); assert.equal(f.grants.length, 1);
});
test('diesel trial rejects other fuels and an empty tank', () => {
    for (const fuel of ['', 'createdieselgenerators:biodiesel', 'minecraft:lava']) {
        const f = fixture('diesel'); f.state.fuel = fuel; f.click(); f.begin(); f.finish();
        assert.equal(f.grants.length, 0, fuel);
    }
});
test('loss of the right fuel or power during processing cancels the observation', () => {
    const d = fixture('diesel'); d.click(); d.begin(); d.state.fuel = ''; d.finish();
    const e = fixture(); e.click(); e.begin(); e.engine.generated = 0; e.finish();
    assert.equal(d.grants.length + e.grants.length, 0);
});
test('replacing either physical block at the same coordinates cancels credit', () => {
    for (const location of ['0,0,0', '1,0,0']) {
        const f = fixture(); f.click(); f.begin();
        f.blocks.get(location).entity = {...f.blocks.get(location).entity};
        f.finish(); assert.equal(f.grants.length, 0);
    }
});
test('source cycles and changed kinetic networks fail closed', () => {
    const c = fixture(); c.engine.source = {x: 0, y: 0, z: 0}; c.click(); c.begin(); c.finish();
    const n = fixture(); n.click(); n.begin(); n.engine.network = 'other'; n.finish();
    assert.equal(c.grants.length + n.grants.length, 0);
});
test('an unloaded source is not accessed or loaded by the monitor', () => {
    const f = fixture(); f.loaded.delete('1,0,0'); f.click(); f.begin(); f.finish();
    assert.equal(f.grants.length, 0); assert.ok(!f.reads.includes('1,0,0')); assert.equal(f.errors.length, 0);
});
test('removing the input and adding output before a timer boundary is rejected', () => {
    const f = fixture(); f.click(); f.begin(); f.machine.timer = 4;
    f.state.input = {id: 'minecraft:air', count: 0};
    f.state.output = [{id: 'createaddition:copper_wire', count: 2}]; f.tick();
    assert.equal(f.grants.length, 0);
});
test('wrong input, oversized batch and wrong result are rejected', () => {
    for (const input of [{id: 'minecraft:copper_ingot', count: 1}, {id: 'create:copper_sheet', count: 2}]) {
        const f = fixture(); f.state.input = input; f.click(); f.begin(); f.finish(); assert.equal(f.grants.length, 0);
    }
    const f = fixture(); f.click(); f.begin(); f.finish(1); assert.equal(f.grants.length, 0);
});
test('immediate hopper extraction fails without a late false positive', () => {
    const f = fixture(); f.click(); f.begin(); f.machine.timer = 0;
    f.state.input = {id: 'minecraft:air', count: 0}; f.tick(); f.finish(); assert.equal(f.grants.length, 0);
});
test('disconnect, dimension change, distance and death clear unfinished work', () => {
    for (const leave of [f => delete f.players[UUID], f => f.level.dimension = 'minecraft:the_nether',
                         f => f.player.x = 100, f => f.player.alive = false]) {
        const f = fixture(); f.click(); f.begin(); leave(f); f.tick();
        f.players[UUID] = f.player; f.level.dimension = 'minecraft:overworld'; f.player.x = 0; f.player.alive = true;
        f.finish(); assert.equal(f.grants.length, 0);
    }
});
test('timeout and server unload do not preserve incomplete observations', () => {
    const f = fixture(); f.click(); for (let i = 0; i < 1200; i++) f.tick();
    f.begin(); f.finish(); assert.equal(f.grants.length, 0);
    const u = fixture(); u.click(); u.begin(); u.handlers.unloaded(); u.finish(); assert.equal(u.grants.length, 0);
});
test('a second player may feed the same batch while each observer is attributed separately', () => {
    const f = fixture(); f.click(); f.click(f.addPlayer(SECOND)); f.begin(); f.finish();
    assert.equal(f.grants.length, 2); assert.ok(f.grants[0].includes(UUID)); assert.ok(f.grants[1].includes(SECOND));
});
test('other tools and offhand interactions neither start nor cancel normal use', () => {
    const f = fixture(); assert.equal(f.click(f.player, 'create:wrench').canceled, false);
    assert.equal(f.click(f.player, 'minecraft:clock', 'OFF_HAND').canceled, false);
    f.begin(); f.finish(); assert.equal(f.grants.length, 0);
});
test('a broken Java API logs the failure and never awards progress', () => {
    const f = fixture(); f.machine.inputInv = null; f.click(); f.tick();
    assert.equal(f.grants.length, 0); assert.equal(f.errors.length, 1);
});
test('a malformed UUID cannot become part of a server command', () => {
    const f = fixture(); f.player.uuid = '@a'; f.click(); f.begin(); f.finish(); assert.equal(f.grants.length, 0);
});
