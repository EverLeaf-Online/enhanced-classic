package soloMapling.ArtificialPlayer.BotCommandsPack;

import client.Character;
import client.inventory.Item;
import client.inventory.InventoryType;
import client.inventory.WeaponType;
import net.server.channel.handlers.AbstractDealDamageHandler.AttackTarget;
import server.ItemInformationProvider;
import soloMapling.ArtificialPlayer.BotAttackSystem.BotAttackData;
import soloMapling.ArtificialPlayer.GCMoveSystem.GCMovement;
import tools.PacketCreator;

import java.util.Collections;
import java.util.Map;

/**
 * SoloMapling's server-side basic attack animation helper, adapted for EverLeaf's
 * headless QA bot. Damage is deliberately separate so EverLeaf's normal monster
 * kill/drop/EXP path remains authoritative.
 */
public final class BotAttack {
    private static final short EQUIP_SLOT_WEAPON = -11;

    private BotAttack() {
    }

    public static void basicSwing(Character chr) {
        if (chr == null || chr.getMap() == null) {
            return;
        }

        Boolean gcFacing = GCMovement.isFacingLeft(chr);
        boolean facingLeft = gcFacing != null ? gcFacing : (chr.getStance() & 1) == 0;
        int facingMask = facingLeft ? BotAttackData.FACING_LEFT_MASK : BotAttackData.FACING_RIGHT_MASK;
        WeaponType weaponType = resolveEquippedWeaponType(chr);
        int bodyActionId = BotAttackData.randomActionFor(weaponType);
        Map<Integer, AttackTarget> emptyTargets = Collections.emptyMap();

        chr.getMap().broadcastMessage(
                chr,
                PacketCreator.closeRangeAttack(
                        chr,
                        0,
                        0,
                        facingMask,
                        0,
                        emptyTargets,
                        BotAttackData.DEFAULT_ATTACK_SPEED,
                        bodyActionId,
                        0),
                false);
    }

    public static WeaponType resolveEquippedWeaponType(Character chr) {
        Item weapon = chr.getInventory(InventoryType.EQUIPPED).getItem(EQUIP_SLOT_WEAPON);
        if (weapon == null) {
            return null;
        }
        return ItemInformationProvider.getInstance().getWeaponType(weapon.getItemId());
    }
}
