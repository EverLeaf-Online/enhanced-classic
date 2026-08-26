/*
	This file is part of the OdinMS Maple Story Server
    Copyright (C) 2008 Patrick Huy <patrick.huy@frz.cc>
		       Matthias Butz <matze@odinms.de>
		       Jan Christian Meyer <vimes@odinms.de>

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation version 3 as published by
    the Free Software Foundation. You may not use, modify or distribute
    this program under any other version of the GNU Affero General Public
    License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/
/* Adobis
 * 
 * El Nath - The Door to Zakum (211042300)
 * 
 * Vs Zakum Recruiter NPC
 * 
 * Custom Quest 100200 = Whether you can start Zakum PQ
 * Custom Quest 100201 = Whether you have done the trials
*/

var status;
var em;
var selectedType;
var gotAllDocs;
var forgeRecipe;
var forgeItems;
var forgeTarget;

function start() {
    status = -1;
    action(1, 0, 0);
}

function action(mode, type, selection) {
    if (mode == -1) {
        cm.dispose();
    } else {
        if (mode == 0) {
            cm.dispose();
            return;
        }
        if (mode == 1) {
            status++;
        } else {
            status--;
        }

        if (cm.haveItem(4001109, 1)) {
            cm.warp(921100000, "out00");
            cm.dispose();
            return;
        }

        if (!(cm.isQuestStarted(100200) || cm.isQuestCompleted(100200))) {   // thanks Vcoc for finding out a need of reapproval from the masters for Zakum expeditions
            if (cm.getPlayer().getLevel() >= 50) {  // thanks Z1peR for noticing not-so-clear unmet requirements message here.
                cm.sendOk("Beware, for the power of olde has not been forgotten... If you seek to defeat #rZakum#k someday, earn the #bChief's Residence Council#k approval foremost and then #bface the trials#k, only then you will become eligible to fight.");
            } else {
                cm.sendOk("Beware, for the power of olde has not been forgotten...");
            }

            cm.dispose();
            return;
        }

        em = cm.getEventManager("ZakumPQ");
        if (em == null) {
            cm.sendOk("The Zakum PQ has encountered an error.");
            cm.dispose();
            return;
        }

        if (status == 0) {
            var menu = "#e#b<Party Quest: Zakum Campaign>\r\n#k#n" + em.getProperty("party") + "\r\n\r\nBeware, for the power of olde has not been forgotten... #b\r\n#L0#Enter the Unknown Dead Mine (Stage 1)#l\r\n#L1#Face the Breath of Lava (Stage 2)#l\r\n#L2#Forging the Eyes of Fire (Stage 3)#l";
            if (cm.getPlayer().getLevel() >= 200) {
                menu += "\r\n\r\n#e#d<Everleaf Endgame>#n#b\r\n#L3#Challenge Rooted Zakum (Lv. 200+, 3-6 players)#l";
                menu += "\r\n#L4#Use the Rooted Forge#l";
            }
            cm.sendSimple(menu);
        } else if (status == 1) {
            if (selection == 0) {
                if (cm.getParty() == null) {
                    cm.sendOk("You can participate in the party quest only if you are in a party.");
                    cm.dispose();
                } else if (!cm.isLeader()) {
                    cm.sendOk("Your party leader must talk to me to start this party quest.");
                    cm.dispose();
                } else {
                    var eli = em.getEligibleParty(cm.getParty());
                    if (eli.size() > 0) {
                        if (!em.startInstance(cm.getParty(), cm.getPlayer().getMap(), 1)) {
                            cm.sendOk("Another party has already entered the #rParty Quest#k in this channel. Please try another channel, or wait for the current party to finish.");
                        }
                    } else {
                        cm.sendOk("You cannot start this party quest yet, because either your party is not in the range size, some of your party members are not eligible to attempt it or they are not in this map. If you're having trouble finding party members, try Party Search.");
                    }

                    cm.dispose();
                }
            } else if (selection == 1) {
                if (cm.haveItem(4031061) && !cm.haveItem(4031062)) {
                    cm.sendYesNo("Would you like to attempt the #bBreath of Lava#k?  If you fail, there is a very real chance you will die.");
                } else {
                    if (cm.haveItem(4031062)) {
                        cm.sendNext("You've already got the #bBreath of Lava#k, you don't need to do this stage.");
                    } else {
                        cm.sendNext("Please complete the earlier trials first.");
                    }

                    cm.dispose();
                }
            } else if (selection == 3) {
                var rooted = cm.getEventManager("RootedZakumBattle");
                if (rooted == null) {
                    cm.sendOk("Rooted Zakum is temporarily unavailable.");
                    cm.dispose();
                    return;
                }
                if (cm.getParty() == null) {
                    cm.sendOk("Rooted Zakum requires a party of 3 to 6 players.");
                    cm.dispose();
                } else if (!cm.isLeader()) {
                    cm.sendOk("Your party leader must start the Rooted Zakum encounter.");
                    cm.dispose();
                } else {
                    var rootedEligible = rooted.getEligibleParty(cm.getParty());
                    if (rootedEligible.size() > 0) {
                        if (!rooted.startInstance(cm.getParty(), cm.getPlayer().getMap(), 200)) {
                            cm.sendOk("All Rooted Zakum instances are currently occupied. Please try again shortly.");
                        }
                    } else {
                        cm.sendOk("Your party must contain 3 to 6 level 200-250 players, and every member must be here at the Door to Zakum.");
                    }
                    cm.dispose();
                }
            } else if (selection == 4) {
                selectedType = 4;
                cm.sendSimple(
                    "#e#d<Rooted Forge>#n#k\r\n" +
                    "Forge upgrades are #bguaranteed#k and have no failure, downgrade, destruction, or random stat rolls. " +
                    "The upgraded equipment becomes untradeable.\r\n\r\n" +
                    "#b#L0#Rooted Weapon Refinement — 60 Verdant Marks, 6 Ember Cores, 3 Ancient Bark#l\r\n" +
                    "#L1#Rooted Armor Refinement — 45 Verdant Marks, 4 Ember Cores, 4 Ancient Bark#l"
                );
            } else {
                if (cm.haveItem(4031061) && cm.haveItem(4031062)) {
                    if (!cm.haveItem(4000082, 30)) {
                        cm.sendOk("You have completed the trials, however there's still the need of #b30 #t4000082##k to forge 5 #t4001017#.");
                    } else {
                        cm.completeQuest(100201);
                        cm.gainItem(4031061, -1);
                        cm.gainItem(4031062, -1);
                        cm.gainItem(4000082, -30);

                        cm.gainItem(4001017, 5);
                        cm.sendNext("You #rhave completed the trials#k, from now on having my approval to challenge Zakum.");
                    }

                    cm.dispose();
                } else {
                    cm.sendOk("You lack some of the required items to forge the #b#t4001017##k.");
                    cm.dispose();
                }
            }
        } else if (status == 2) {
            if (selectedType != 4) {
                cm.warp(280020000, 0);
                cm.dispose();
                return;
            }

            var RootedForgeRecipe = Java.type('everleaf.progression.RootedForgeRecipe');
            var RootedForgeOutcomeCatalog = Java.type('everleaf.progression.RootedForgeOutcomeCatalog');
            var RootedForgeTargetPolicy = Java.type('everleaf.progression.RootedForgeTargetPolicy');
            var InventoryType = Java.type('client.inventory.InventoryType');
            forgeRecipe = selection == 0
                ? RootedForgeRecipe.ROOTED_WEAPON_REFINEMENT
                : RootedForgeRecipe.ROOTED_ARMOR_REFINEMENT;
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
        } else if (status == 3 && selectedType == 4) {
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
            var ember = materials.get(RootedMaterial.EMBER_CORE);
            var bark = materials.get(RootedMaterial.ANCIENT_BARK);
            var costs = forgeRecipe.materialCosts();

            var preview = "#e#d" + forgeRecipe.displayName() + "#n#k\r\n";
            preview += "Target: #b#i" + forgeTarget.getItemId() + "# #t" + forgeTarget.getItemId() + "##k\r\n\r\n";
            preview += "Cost: " + forgeRecipe.verdantMarkCost() + " Verdant Marks (you have " + marks + ")";
            preview += "\r\nEmber Cores: " + costs.get(RootedMaterial.EMBER_CORE) + " (you have " + ember + ")";
            preview += "\r\nAncient Bark: " + costs.get(RootedMaterial.ANCIENT_BARK) + " (you have " + bark + ")";
            preview += "\r\n\r\nFixed upgrade: +" + delta.str() + " all stats";
            if (delta.weaponAttack() > 0) preview += ", +" + delta.weaponAttack() + " weapon/magic attack";
            if (delta.weaponDefense() > 0) preview += ", +" + delta.weaponDefense() + " weapon/magic defense";
            preview += ", +" + delta.hp() + " HP, +" + delta.mp() + " MP, +" + delta.accuracy() + " accuracy/avoidability.";
            preview += "\r\n\r\n#rThis equipment will become untradeable.#k Continue?";
            cm.sendYesNo(preview);
        } else if (status == 4 && selectedType == 4) {
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
}
