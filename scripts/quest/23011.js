var status = -1;

function end(mode, type, selection) {
    if (mode == -1) {
        qm.dispose();
        return;
    }

    status++;
    if (status == 0) {
        qm.sendNext("Battle Mage is not part of EverLeaf's current v83 class roster. This inherited Resistance quest is kept as legacy data, but it cannot advance your character into an unsupported job.");
    } else {
        qm.dispose();
    }
}
