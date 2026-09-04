/* Informant - Gate to the Future / Knight Stronghold prerequisite */

const EmpressContentPolicy = Java.type('everleaf.content.EmpressContentPolicy');
const EmpressStrongholdProgressService = Java.type('everleaf.content.EmpressStrongholdProgressService');

function start() {
    var player = cm.getPlayer();

    if (!EmpressContentPolicy.isEnabled()) {
        cm.sendOk(EmpressContentPolicy.disabledMessage());
        cm.dispose();
        return;
    }

    if (player.getLevel() < 180) {
        cm.sendOk("The future beyond this gate is too dangerous right now. Return when you reach #bLevel 180#k.");
        cm.dispose();
        return;
    }

    if (!EmpressStrongholdProgressService.isStarted(player.getId())) {
        if (!EmpressStrongholdProgressService.start(player.getId())) {
            cm.sendOk("I couldn't register your Knight Stronghold investigation. Please try again in a moment.");
            cm.dispose();
            return;
        }
        cm.sendOk("The Cygnus Knights have fortified the Stronghold. Scout the fortress and defeat #rone of each Advanced Knight A through E#k. Once all five have fallen, the path to Empress Cygnus will be open to you.\r\n\r\nYour progress is character-specific; the Empress clear lockout itself is account-wide each week.");
        cm.dispose();
        return;
    }

    if (EmpressStrongholdProgressService.isComplete(player.getId())) {
        cm.sendOk("You've broken through every Advanced Knight division. The Stronghold prerequisite is complete. Proceed to #bCygnus Garden#k and form an Empress expedition.");
    } else {
        cm.sendOk("Your Knight Stronghold investigation is still underway.\r\n\r\n#b" + EmpressStrongholdProgressService.statusText(player.getId()) + "#k");
    }
    cm.dispose();
}
