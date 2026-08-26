package service.enhanced;

import client.Character;

/**
 * Applies Enhanced Classic permanent MaxHP floors to characters.
 *
 * <p>This operation is intentionally idempotent: once a character is at or
 * above the floor, applying it again changes nothing.</p>
 */
public class SurvivabilityService {

    public int applyCurrentFloor(Character character) {
        if (character == null) {
            throw new IllegalArgumentException("character cannot be null");
        }

        int currentMaxHp = character.getMaxHp();
        int increase = SurvivabilityPolicy.requiredIncrease(
                character.getJob(), character.getLevel(), currentMaxHp);

        if (increase <= 0) {
            return 0;
        }

        return character.applyEnhancedPermanentMaxHpFloor(currentMaxHp + increase);
    }
}
