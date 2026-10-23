// Executes the artillery script against explicit API models, not Minecraft.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const code = fs.readFileSync(path.join(__dirname, '../kubejs/server_scripts/nasledie_artillery.js'), 'utf8');
const UUID = '12345678-1234-1234-1234-123456789abc';
const FAR = '12345678-1234-1234-1234-123456789def';

function fixture() {
    let handler;
    const commands = [], errors = [];
    const level = {name: 'overworld'}, nether = {name: 'nether'};
    const players = [
        {uuid: UUID, level, x: 10, y: 64, z: 0, isAlive: () => true},
        {uuid: FAR, level, x: 1000, y: 64, z: 0, isAlive: () => true}];
    const server = {getPlayers: () => players, runCommandSilent: c => { commands.push(c); return 1; }};
    vm.runInContext(code, vm.createContext({
        EntityEvents: {death: h => { handler = h; }},
        console: {error: m => errors.push(m)}
    }));
    const kill = (type, msgId, where = level) => handler({
        source: {getMsgId: () => msgId},
        entity: {type, server, level: where, x: 0, y: 64, z: 0, player: false}});
    return {kill, commands, errors, players};
}

test('cannon kill credits nearby players only', () => {
    const f = fixture();
    f.kill('minecraft:zombie', 'createbigcannons.cannon_projectile');
    assert.deepEqual(f.commands, [`advancement grant ${UUID} only nasledie:events/artillery/kill`]);
});

test('cannon kill of a boss grants the boss goal too', () => {
    const f = fixture();
    f.kill('cataclysm:ignis', 'createbigcannons.shrapnel');
    assert.deepEqual(f.commands, [
        `advancement grant ${UUID} only nasledie:events/artillery/kill`,
        `advancement grant ${UUID} only nasledie:events/artillery/boss`]);
});

test('other damage and other dimensions are ignored', () => {
    const f = fixture();
    f.kill('minecraft:zombie', 'arrow');
    f.kill('minecraft:zombie', 'createbigcannons.flak', {name: 'nether'});
    assert.deepEqual(f.commands, []);
});

test('errors are logged, not thrown', () => {
    const f = fixture();
    f.players.push(null);
    f.kill('minecraft:zombie', 'createbigcannons.grapeshot');
    assert.equal(f.errors.length, 1);
});
