// Grants nasledie:events/... advancements for mod events that have no advancement trigger.
// Recruits 1.15.2 posts RecruitEvent$Hired / $Promoted / $LevelUp on the Forge bus (server side);
// Workers 2.0.3 entities extend AbstractRecruitEntity, so hiring a worker posts the same event.
// Every target advancement uses minecraft:impossible; a missing one is ignored by the silent command.
var NasledieEvents = (function () {
    var registries = Java.loadClass('net.minecraftforge.registries.ForgeRegistries');
    var uuidPattern = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
    var levels = [3, 5];

    function grant(player, path) {
        if (!player) return;
        var server = player.getServer();
        var uuid = String(player.getStringUUID());
        if (!server || !uuidPattern.test(uuid) || !/^[a-z0-9_\/]+$/.test(path)) return;
        server.runCommandSilent('advancement grant ' + uuid + ' only nasledie:events/' + path);
    }

    function typeOf(entity) {
        var key = registries.ENTITY_TYPES.getKey(entity.getType());
        return key ? String(key) : '';
    }

    function hired(event) {
        var type = typeOf(event.getRecruit());
        var namespace = type.split(':')[0];
        if (namespace !== 'recruits' && namespace !== 'workers') return;
        grant(event.getPlayer(), 'hired/' + namespace);
        grant(event.getPlayer(), 'hired/' + type.replace(':', '/'));
    }

    function promoted(event) {
        grant(event.getPromotingPlayer(), 'recruits/promoted');
    }

    function levelUp(event) {
        var recruit = event.getRecruit();
        var level = Number(event.getNewLevel());
        if (levels.indexOf(level) === -1) return;
        grant(recruit.getOwner(), 'recruits/level_' + level);
    }

    function safely(name, handler) {
        return function (event) {
            try {
                handler(event);
            } catch (error) {
                console.error('[Nasledie events] ' + name + ': ' + error);
            }
        };
    }

    ForgeEvents.onEvent('com.talhanation.recruits.RecruitEvent$Hired', safely('hired', hired));
    ForgeEvents.onEvent('com.talhanation.recruits.RecruitEvent$Promoted', safely('promoted', promoted));
    ForgeEvents.onEvent('com.talhanation.recruits.RecruitEvent$LevelUp', safely('levelUp', levelUp));
    return {grant: grant};
})();
