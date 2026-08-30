package everleaf.progression;

import client.inventory.Equip;
import constants.inventory.ItemConstants;

/** Pure equipment-category and stage validation for Rooted forge delivery. */
public final class RootedForgeTargetPolicy {
    private RootedForgeTargetPolicy() {}

    public record Check(boolean allowed, String reason) {
        public static Check allow() { return new Check(true, "ok"); }
        public static Check deny(String reason) { return new Check(false, reason); }
    }

    public static Check validate(Equip equip, RootedForgeOutcomeCatalog.Outcome outcome) {
        if (equip == null) return Check.deny("equipment_required");
        if (outcome == null) return Check.deny("forge_outcome_required");

        boolean weapon = ItemConstants.isWeapon(equip.getItemId());
        if (outcome.recipe() == RootedForgeRecipe.ROOTED_WEAPON_REFINEMENT && !weapon) {
            return Check.deny("weapon_required");
        }
        if (outcome.recipe() == RootedForgeRecipe.ROOTED_ARMOR_REFINEMENT && weapon) {
            return Check.deny("armor_required");
        }
        if (equip.getEverleafForgeStage() >= outcome.stage()) {
            return Check.deny("stage_already_applied");
        }
        if (equip.getEverleafForgeStage() != outcome.stage() - 1) {
            return Check.deny("previous_stage_required");
        }
        return Check.allow();
    }
}
