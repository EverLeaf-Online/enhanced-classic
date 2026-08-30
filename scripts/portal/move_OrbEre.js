function enter(pi) {
    // Empress' Road - To Ereve. Map.wz uses a scripted portal sentinel here;
    // the destination is Ereve's Sky Ferry.
    pi.playPortalSound();
    pi.warp(130000210, 0);
    return true;
}
