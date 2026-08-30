const PersonalTravelService = Java.type('server.travel.PersonalTravelService');

// Rien -> Lith Harbor personal ship maps (200090070-200090079).
function enter(pi) {
    if (!PersonalTravelService.completeIfReady(pi.getPlayer())) {
        return false;
    }

    pi.playPortalSound();
    pi.warp(104000000, 0);
    return true;
}
