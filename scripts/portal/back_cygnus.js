function enter(pi) {
    const EmpressContentPolicy = Java.type('everleaf.content.EmpressContentPolicy');

    if (!EmpressContentPolicy.isEnabled()) {
        pi.getPlayer().dropMessage(5, EmpressContentPolicy.disabledMessage());
        return false;
    }

    // Scrubby Garden is outside the reward-bearing boss room. Keep the return
    // deterministic and avoid fabricating progression through the imported maps.
    pi.playPortalSound();
    pi.warp(271040200, 0);
    return true;
}
