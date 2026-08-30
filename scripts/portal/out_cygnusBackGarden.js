function enter(pi) {
    const EmpressContentPolicy = Java.type('everleaf.content.EmpressContentPolicy');

    if (!EmpressContentPolicy.isEnabled()) {
        pi.getPlayer().dropMessage(5, EmpressContentPolicy.disabledMessage());
        return false;
    }

    // Both rear-garden variants are staging/return maps. Return players to
    // Cygnus Garden rather than allowing a scripted portal with no target to
    // strand them inside the imported map family.
    pi.playPortalSound();
    pi.warp(271040000, 0);
    return true;
}
