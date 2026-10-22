// Executes the startup event script against explicit API models, not Minecraft.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const code = fs.readFileSync(path.join(__dirname, '../kubejs/startup_scripts/nasledie_events.js'), 'utf8');
const UUID = '12345678-1234-1234-1234-123456789abc';

function fixture() {
    const handlers = {}, commands = [], errors = [];
    const server = {runCommandSilent: command => { commands.push(command); return 1; }};
    const player = {getServer: () => server, getStringUUID: () => UUID};
    const context = vm.createContext({
        Java: {loadClass(name) {
            assert.equal(name, 'net.minecraftforge.registries.ForgeRegistries');
            return {ENTITY_TYPES: {getKey: type => type}};
        }},
        ForgeEvents: {onEvent(name, handler) { handlers[name.split('$')[1]] = handler; }},
        console: {error: message => errors.push(message)}
    });
    vm.runInContext(code, context, {filename: 'nasledie_events.js'});
    const entity = type => ({getType: () => type, getOwner: () => player});
    return {handlers, commands, errors, player, entity};
}

test('hiring a recruit grants the namespace and the exact type', () => {
    const f = fixture();
    f.handlers.Hired({getRecruit: () => f.entity('recruits:bowman'), getPlayer: () => f.player});
    assert.deepEqual(f.commands, [
        `advancement grant ${UUID} only nasledie:events/hired/recruits`,
        `advancement grant ${UUID} only nasledie:events/hired/recruits/bowman`]);
});

test('hiring a worker is reported separately from recruits', () => {
    const f = fixture();
    f.handlers.Hired({getRecruit: () => f.entity('workers:farmer'), getPlayer: () => f.player});
    assert.equal(f.commands[0], `advancement grant ${UUID} only nasledie:events/hired/workers`);
});

test('foreign entity types are ignored', () => {
    const f = fixture();
    f.handlers.Hired({getRecruit: () => f.entity('othermod:knight'), getPlayer: () => f.player});
    assert.deepEqual(f.commands, []);
});

test('only milestone levels are granted, to the owner', () => {
    const f = fixture();
    f.handlers.LevelUp({getRecruit: () => f.entity('recruits:recruit'), getNewLevel: () => 4});
    f.handlers.LevelUp({getRecruit: () => f.entity('recruits:recruit'), getNewLevel: () => 5});
    assert.deepEqual(f.commands, [`advancement grant ${UUID} only nasledie:events/recruits/level_5`]);
});

test('promotion and offline owners', () => {
    const f = fixture();
    f.handlers.Promoted({getPromotingPlayer: () => f.player});
    f.handlers.LevelUp({getRecruit: () => ({getType: () => 'recruits:recruit', getOwner: () => null}), getNewLevel: () => 3});
    assert.deepEqual(f.commands, [`advancement grant ${UUID} only nasledie:events/recruits/promoted`]);
});

test('errors are logged, never thrown into the game', () => {
    const f = fixture();
    f.handlers.Hired({getRecruit: () => { throw new Error('boom'); }, getPlayer: () => f.player});
    assert.equal(f.errors.length, 1);
});
