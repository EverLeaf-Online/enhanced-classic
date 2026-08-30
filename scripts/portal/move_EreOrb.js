function enter(pi) {
    // Empress' Road - To Orbis. Map.wz uses a scripted portal sentinel here;
    // the destination is Orbis Station.
    pi.playPortalSound();
    pi.warp(200000161, 0);
    return true;
}
