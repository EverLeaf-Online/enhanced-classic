/* Adobis — EverLeaf Zakum campaign, Rooted Zakum, and Rooted Forge. */

var status;
var em;
var selectedType;
var forgeRecipe;
var forgeItems;
var forgeTarget;

function start() {
    status = -1;
    action(1, 0, 0);
}

function action(mode, type, selection) {
    if (mode == -1 || mode == 0) {
        cm.dispose();
        return;
    }
    status += mode == 1 ? 1 : -1;

    if (cm.haveItem(4001109, 1)) {
        cm.warp(921100000, "out00");
        cm.dispose();
        return;
    }

    if (!(cm.isQuestStarted(100200) || cm.isQuestCompleted(100200))) {
        if (cm.getPlayer().getLevel() >= 50) {
            cm.sendOk("You are high enough level to begin the Zakum pre-quests, but you still need approval from the #bChief's Residence Council#k in El Nath before Adobis can send you into the trials.");
        } else {
            cm.sendOk("The Zakum campaign begins at #blevel 50#k. Your current level is #r" + cm.getPlayer().getLevel() + "#k.");
        }
        cm.dispose();
        return;
    }

    em = cm.getEventManager("ZakumPQ");
    if (em == null) {
        cm.sendOk("The Zakum trial service could not be loaded. Please report this in EverLeaf's bug-report channel and include that you were speaking to Adobis at the Door to Zakum.");
        cm.dispose();
        return;
    }

    if (status == 0) {
        var menu = "#e#b<Party Quest: Zakum Campaign>\r\n#k#n" + em.getProperty("party") + "\r\n\r\nChoose the Zakum trial you want to attempt:#b\r\n#L0#Stage 1: Enter the Unknown Dead Mine#l\r\n#L1#Stage 2: Face the Breath of Lava#l\r\n#L2#Stage 3: Forge the Eyes of Fire#l";
        if (cm.getPlayer().getLevel() >= 200) {
            menu += "\r\n\r\n#e#d<EverLeaf Endgame>#n#b\r\n#L3#Challenge Rooted Zakum (Lv. 200+, 3-6 players)#l\r\n#L4#Use the Rooted Forge#l";
        }
        cm.sendSimple(menu);
        return;
    }

    if (status == 1) {
        if (selection == 0) {
            if (cm.getParty() == null) {
                cm.sendOk("You need to be in a party to enter Stage 1 of the Zakum trials.");
            } else if (!cm.isLeader()) {
                cm.sendOk("Your party leader must speak to me to start Stage 1 of the Zakum trials.");
            } else {
                var eli = em.getEligibleParty(cm.getParty());
                if (eli.size() > 0) {
                    if (!em.startInstance(cm.getParty(), cm.getPlayer().getMap(), 1)) {
                        cm.sendOk("Another party is already running Stage 1 of the Zakum trials in this channel. Please try another channel or wait for them to finish.");
                    }
                } else {
                    cm.sendOk("Your party cannot enter Stage 1 yet. Make sure every required party member is eligible and standing here at the Door to Zakum before the leader tries again.");
                }
            }
            cm.dispose();
        } else if (selection == 1) {
            if (cm.haveItem(4031061) && !cm.haveItem(4031062)) {
                cm.sendYesNo("You have completed Stage 1. Would you like to attempt #bStage 2: Breath of Lava#k? If you fail, you may die.");
            } else {
                cm.sendNext(cm.haveItem(4031062)
                    ? "You already completed Stage 2 and have the #bBreath of Lava#k. You do not need to repeat it."
                    : "Complete Stage 1 first and bring its proof before attempting the Breath of Lava.");
                cm.dispose();
            }
        } else if (selection == 2) {
            if (cm.haveItem(4031061) && cm.haveItem(4031062)) {
                if (!cm.haveItem(4000082, 30)) {
                    cm.sendOk("You have completed Stages 1 and 2. To finish Stage 3, bring #b30 #t4000082##k so I can forge #b5 #t4001017##k.");
                } else {
                    cm.completeQuest(100201);
                    cm.gainItem(4031061, -1);
                    cm.gainItem(4031062, -1);
                    cm.gainItem(4000082, -30);
                    cm.gainItem(4001017, 5);
                    cm.sendNext("You have completed all three Zakum trials. You are now approved to challenge Zakum and have received #b5 #t4001017##k.");
                }
            } else {
                cm.sendOk("You have not completed all required earlier trials yet. Finish Stages 1 and 2 before attempting to forge the Eyes of Fire.");
            }
            cm.dispose();
        } else if (selection == 3) {
            var rooted = cm.getEventManager("RootedZakumBattle");
            if (rooted == null) {
                cm.sendOk("Rooted Zakum is temporarily unavailable. Please report this if the problem persists.");
                cm.dispose();
                return;
            }
            if (cm.getParty() == null) {
                cm.sendOk("Rooted Zakum requires a party of 3 to 6 players.");
            } else if (!cm.isLeader()) {
                cm.sendOk("Your party leader must start the Rooted Zakum encounter.");
            } else {
                var rootedEligible = rooted.getEligibleParty(cm.getParty());
                if (rootedEligible.size() > 0) {
                    if (!rooted.startInstance(cm.getParty(), cm.getPlayer().getMap(), 200)) {
                        cm.sendOk("All Rooted Zakum instances are currently occupied. Please try again shortly.");
                    }
                } else {
                    cm.sendOk("Your party must contain 3 to 6 level 200-250 players, and every member must be here at the Door to Zakum.");
                }
            }
            cm.dispose();
        } else if (selection == 4) {
            selectedType = 4;
            cm.sendSimple(
                "#e#d<Rooted Forge>#n#k\r\n" +
                "Forge upgrades are #bguaranteed#k: no failure, downgrade, destruction, or random stat rolls. The upgraded equipment becomes untradeable.\r\n\r\n" +
                "#b#L0#Rooted Weapon Refinement — 60 Verdant Marks, 6 Ember Cores, 3 Ancient Bark#l\r\n" +
                "#L1#Rooted Armor Refinement — 45 Verdant Marks, 4 Ember Cores, 4 Ancient Bark#l"
            );
        }
        return;
    }

    if (status == 2) {
        if (selectedType != 4) {
            cm.warp(280020000, 0);
            cm.dispose();
            return;
        }

        var RootedForgeRecipe = Java.type('everleaf.progression.RootedForgeRecipe');
        var RootedForgeOutcomeCatalog = Java.type('everleaf.progression.RootedForgeOutcomeCatalog');
        var RootedForgeTargetPolicy = Java.type('everleaf.progression.RootedForgeTargetPolicy');
        var InventoryType = Java.type('client.inventory.InventoryType');
        forgeRecipe = selection == 0 ? RootedForgeRecipe.ROOTED_WEAPON_REFINEMENT : RootedForgeRecipe.ROOTED_ARMOR_REFINEMENT;
        var outcome = RootedForgeOutcomeCatalog.byRecipe(forgeRecipe);
        var inventory = cm.getPlayer().getInventory(InventoryType.EQUIP).list().toArray();
        forgeItems = [];
        var itemMenu = "#eSelect an eligible item from your Equip inventory:#n\r\n";
        for (var i = 0; i < inventory.length; i++) {
            var item = inventory[i];
            if (item.getItemType() == 1 && RootedForgeTargetPolicy.validate(item, outcome).allowed()) {
                forgeItems.push(item);
                itemMenu += "\r\n#b#L" + (forgeItems.length - 1) + "##i" + item.getItemId() + "# #t" + item.getItemId() + "# (slot " + item.getPosition() + ")#l";
            }
        }
        if (forgeItems.length == 0) {
            cm.sendOk("You have no eligible equipment for that recipe. Unequip the item first, place it in your Equip inventory, and make sure it has not already received this forge stage.");
            cm.dispose();
            return;
        }
        cm.sendSimple(itemMenu);
        return;
    }

    if (status == 3 && selectedType == 4) {
        if (selection < 0 || selection >= forgeItems.length) {
            cm.sendOk("That forge target is no longer available.");
            cm.dispose();
            return;
        }
        forgeTarget = forgeItems[selection];
        var RootedForgeOutcomeCatalog = Java.type('everleaf.progression.RootedForgeOutcomeCatalog');
        var RootedMaterial = Java.type('everleaf.progression.RootedMaterial');
        var Runtime = Java.type('everleaf.progression.EverleafProgressionRuntime');
        var outcome = RootedForgeOutcomeCatalog.byRecipe(forgeRecipe);
        var delta = outcome.statDelta();
        var accountId = cm.getPlayer().getAccountID();
        var marks = Runtime.verdantMarkService().account(accountId).balance();
        var materials = Runtime.rootedMaterialRepository().balances(accountId);
        var costs = forgeRecipe.materialCosts();
        var preview = "#e#d" + forgeRecipe.displayName() + "#n#k\r\n";
        preview += "Target: #b#i" + forgeTarget.getItemId() + "# #t" + forgeTarget.getItemId() + "##k\r\n\r\n";
        preview += "Cost: " + forgeRecipe.verdantMarkCost() + " Verdant Marks (you have " + marks + ")";
        preview += "\r\nEmber Cores: " + costs.get(RootedMaterial.EMBER_CORE) + " (you have " + materials.get(RootedMaterial.EMBER_CORE) + ")";
        preview += "\r\nAncient Bark: " + costs.get(RootedMaterial.ANCIENT_BARK) + " (you have " + materials.get(RootedMaterial.ANCIENT_BARK) + ")";
        preview += "\r\n\r\nFixed upgrade: +" + delta.str() + " all stats";
        if (delta.weaponAttack() > 0) preview += ", +" + delta.weaponAttack() + " weapon/magic attack";
        if (delta.weaponDefense() > 0) preview += ", +" + delta.weaponDefense() + " weapon/magic defense";
        preview += ", +" + delta.hp() + " HP, +" + delta.mp() + " MP, +" + delta.accuracy() + " accuracy/avoidability.";
        preview += "\r\n\r\n#rThis equipment will become untradeable.#k Continue?";
        cm.sendYesNo(preview);
        return;
    }

    if (status == 4 && selectedType == 4) {
        var Runtime = Java.type('everleaf.progression.EverleafProgressionRuntime');
        var RootedForgeTarget = Java.type('everleaf.progression.RootedForgeTarget');
        var InventoryType = Java.type('client.inventory.InventoryType');
        var UUID = Java.type('java.util.UUID');
        var player = cm.getPlayer();
        var target = new RootedForgeTarget(forgeTarget.getItemId(), InventoryType.EQUIP, forgeTarget.getPosition());
        var purchase = Runtime.rootedForgeService().purchase(
            player.getAccountID(), player.getId(), player.getLevel(), forgeRecipe, target, UUID.randomUUID().toString()
        );
        if (!purchase.applied()) {
            cm.sendOk("The forge could not complete the purchase: #r" + purchase.reason() + "#k. No resources were spent.");
            cm.dispose();
            return;
        }
        var fulfilled = Runtime.rootedForgeFulfillmentService().fulfill(player, purchase.order().id());
        if (fulfilled.fulfilled()) {
            cm.sendOk("#e#dRooted Forge complete!#n#k Your equipment received its guaranteed Stage 1 refinement.");
        } else {
            cm.sendOk("Your payment is safely recorded, but delivery is pending: #r" + fulfilled.reason() + "#k. Ask a GM to retry forge order #b" + purchase.order().id() + "#k; you will not be charged again.");
        }
        cm.dispose();
    }
}
