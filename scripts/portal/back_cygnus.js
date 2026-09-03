function enter(pi) {
    var player = pi.getPlayer();
    var eim = player.getEventInstance();
    if (eim != null) eim.unregisterPlayer(player);
    pi.warp(271040000, 0);
    return true;
}
