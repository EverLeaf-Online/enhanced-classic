var status = -1;

function end(mode, type, selection) {
    if (mode == -1) {
        qm.dispose();
        return;
    }

    status++;
    if (status == 0) {
        qm.sendNext("Cannoneer is not available in EverLeaf's current v83 class roster. This legacy quest remains in the data files, but it cannot advance your character into an unsupported job.");
    } else {
        qm.dispose();
    }
}
