// Executes the expedition notes script against API models (KubeJS 2001.6.5 ChestLootEventJS), not Minecraft.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const code = fs.readFileSync(path.join(__dirname, '../kubejs/server_scripts/nasledie_notes.js'), 'utf8');
const registry = JSON.parse(fs.readFileSync(path.join(__dirname, '../references/registry.json'), 'utf8'));

function load() {
    let handler;
    const errors = [];
    const context = vm.createContext({
        ServerEvents: {chestLootTables: h => { handler = h; }},
        console: {error: m => errors.push(m)}
    });
    vm.runInContext(code, context);
    return {handler, errors, api: vm.runInContext('NasledieNotes', context)};
}

function fakeEvent() {
    const calls = [];
    return {calls, modify(id, fn) {
        const pools = [];
        fn({addPool(f) {
            const pool = {rolls: null, entries: []};
            f({setUniformRolls(a, b) { pool.rolls = [a, b]; },
               addEntry(json) { const e = {json, weight: null}; pool.entries.push(e); return {weight(w) { e.weight = w; }}; },
               addEmpty(w) { pool.entries.push({empty: w}); }});
            pools.push(pool);
        }});
        calls.push({id, pools});
    }};
}

// Reads the SNBT the script builds: {title:"..",author:"..",pages:["..",..]} with \\ and \" escapes.
function readTag(tag) {
    const strings = [];
    const re = /"((?:[^"\\]|\\.)*)"/g;
    let m;
    while ((m = re.exec(tag))) strings.push(m[1].replace(/\\(.)/g, '$1'));
    const [title, author, ...pages] = strings;
    return {title, author, pages: pages.map(p => JSON.parse(p).text)};
}

test('every note targets a real chest loot table and a valid book', () => {
    const {api} = load();
    const tables = new Set(registry.loot_tables);
    assert.ok(api.notes.length >= 8);
    for (const note of api.notes) {
        assert.ok(tables.has(note.table), note.table);
        assert.ok(note.title.length >= 1 && note.title.length <= 32, note.title);
        assert.ok(note.author.length >= 1);
        assert.ok(note.pages.length >= 1);
        for (const page of note.pages) assert.ok(page.length <= 256, `${note.title}: page too long`);
        assert.ok(note.chance >= 2);
    }
});

test('book tag round-trips titles, authors and pages', () => {
    const {api} = load();
    for (const note of api.notes) {
        assert.deepEqual(readTag(api.bookTag(note)), {title: note.title, author: note.author, pages: [...note.pages]});
    }
    const tricky = {title: 'Кавычки "и" \\', author: 'A', pages: ['строка\nи "цитата" \\ слэш']};
    assert.deepEqual(readTag(api.bookTag(tricky)), tricky);
});

test('register adds one weighted pool per table, without the chests/ prefix', () => {
    const {handler, errors} = load();
    const event = fakeEvent();
    handler(event);
    assert.deepEqual(errors, []);
    const {api} = load();
    assert.equal(event.calls.length, api.notes.length);
    event.calls.forEach((call, i) => {
        const note = api.notes[i];
        assert.equal(call.id, note.table.replace(':chests/', ':'));
        assert.equal(call.pools.length, 1);
        const [pool] = call.pools;
        assert.deepEqual(pool.rolls, [1, 1]);
        assert.equal(pool.entries[0].weight, 1);
        assert.equal(pool.entries[0].json.name, 'minecraft:written_book');
        assert.equal(pool.entries[0].json.functions[0].function, 'minecraft:set_nbt');
        assert.deepEqual(pool.entries[1], {empty: note.chance - 1});
    });
});

test('non-chest tables are refused and logged, not thrown', () => {
    const {api} = load();
    assert.throws(() => api.eventId('betterarcheology:archeology/chest_mott'));
    const {handler, errors} = load();
    const event = {modify() { throw new Error('boom'); }};
    handler(event);
    assert.equal(errors.length > 0, true);
});
