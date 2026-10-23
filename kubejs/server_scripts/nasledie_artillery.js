// Credits artillery kills from Create Big Cannons 5.11.4. Its projectiles carry no player owner, so a kill
// is detected by the damage type message id (data/createbigcannons/damage_type/*.json: "createbigcannons.*")
// and credited to players near the victim. Grants nasledie:events/artillery/... (minecraft:impossible).
var NasledieArtillery = (function () {
    var RADIUS = 128;
    var uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    var bosses = {
        'minecraft:wither': true, 'minecraft:ender_dragon': true, 'minecraft:warden': true, 'minecraft:elder_guardian': true,
        'cataclysm:ender_guardian': true, 'cataclysm:netherite_monstrosity': true, 'cataclysm:ignis': true,
        'cataclysm:the_harbinger': true, 'cataclysm:the_leviathan': true, 'cataclysm:ancient_remnant': true,
        'cataclysm:maledictus': true, 'cataclysm:scylla': true,
        'mowziesmobs:ferrous_wroughtnaut': true, 'mowziesmobs:frostmaw': true, 'mowziesmobs:umvuthi': true,
        'alexscaves:hullbreaker': true, 'alexscaves:luxtructosaurus': true, 'alexscaves:forsaken': true,
        'alexsmobs:void_worm': true
    };

    function isArtillery(source) {
        var id = source ? String(source.getMsgId()) : '';
        return id.indexOf('createbigcannons.') === 0;
    }

    function witnesses(server, victim) {
        var result = [];
        server.getPlayers().forEach(function (player) {
            if (player.level !== victim.level || !player.isAlive()) return;
            var dx = Number(player.x) - Number(victim.x);
            var dy = Number(player.y) - Number(victim.y);
            var dz = Number(player.z) - Number(victim.z);
            if (dx * dx + dy * dy + dz * dz <= RADIUS * RADIUS) result.push(player);
        });
        return result;
    }

    function grant(server, player, path) {
        var uuid = String(player.uuid);
        if (uuidPattern.test(uuid)) server.runCommandSilent('advancement grant ' + uuid + ' only nasledie:events/artillery/' + path);
    }

    function onDeath(event) {
        if (!isArtillery(event.source)) return;
        var victim = event.entity;
        var server = victim.server;
        if (!server || victim.player) return;
        var boss = bosses[String(victim.type)] === true;
        witnesses(server, victim).forEach(function (player) {
            grant(server, player, 'kill');
            if (boss) grant(server, player, 'boss');
        });
    }

    EntityEvents.death(function (event) {
        try {
            onDeath(event);
        } catch (error) {
            console.error('[Nasledie artillery] ' + error);
        }
    });
    return {isArtillery: isArtillery, bosses: bosses};
})();
