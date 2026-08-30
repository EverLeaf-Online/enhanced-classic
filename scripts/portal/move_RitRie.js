const PersonalTravelService = Java.type('server.travel.PersonalTravelService');

// Lith Harbor -> Rien personal ship maps (200090060-200090069).
function enter(pi) {
    if (!PersonalTravelService.completeIfReady(pi.getPlayer())) {
        return false;
    }

    pi.playPortalSound();
    pi.warp(140020300, 0);
    return true;
}
