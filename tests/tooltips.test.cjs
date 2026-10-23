// Executes the tooltip script against an ItemEvents.tooltip model (KubeJS 2001.6.5), not Minecraft.
const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const code = fs.readFileSync(path.join(__dirname, '../kubejs/client_scripts/nasledie_tooltips.js'), 'utf8');
const registry = JSON.parse(fs.readFileSync(path.join(__dirname, '../references/registry.json'), 'utf8'));

test('tooltips cover real items with short lines', () => {
    let handler;
    const added = [];
    vm.runInContext(code, vm.createContext({
        ItemEvents: {tooltip: h => { handler = h; }},
        Text: {darkGray: s => ({darkGray: s})}
    }));
    handler({add: (item, lines) => added.push({item, lines})});
    const items = new Set(registry.items);
    assert.ok(added.length >= 8);
    for (const {item, lines} of added) {
        assert.ok(items.has(item), item);
        assert.ok(Array.isArray(lines) && lines.length >= 1);
        for (const line of lines) assert.ok(line.darkGray.length <= 45, `${item}: ${line.darkGray}`);
    }
});
