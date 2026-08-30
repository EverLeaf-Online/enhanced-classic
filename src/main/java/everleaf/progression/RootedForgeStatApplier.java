package everleaf.progression;

import client.inventory.Equip;
import constants.inventory.ItemConstants;

/** Applies one fixed forge outcome exactly once to a persistent equipment item. */
public final class RootedForgeStatApplier {
    private RootedForgeStatApplier() {}

    public record Result(boolean applied, String reason, int stageAfter) {
        public static Result success(int stageAfter) { return new Result(true, "ok", stageAfter); }
        public static Result rejected(String reason, int stageAfter) { return new Result(false, reason, stageAfter); }
    }

    public static Result apply(Equip equip, RootedForgeOutcomeCatalog.Outcome outcome) {
        var check = RootedForgeTargetPolicy.validate(equip, outcome);
        if (!check.allowed()) return Result.rejected(check.reason(), equip == null ? 0 : equip.getEverleafForgeStage());

        synchronized (equip) {
            check = RootedForgeTargetPolicy.validate(equip, outcome);
            if (!check.allowed()) return Result.rejected(check.reason(), equip.getEverleafForgeStage());

            ForgeStatDelta delta = outcome.statDelta();
            short str = add(equip.getStr(), delta.str());
            short dex = add(equip.getDex(), delta.dex());
            short intel = add(equip.getInt(), delta.intel());
            short luk = add(equip.getLuk(), delta.luk());
            short watk = add(equip.getWatk(), delta.weaponAttack());
            short matk = add(equip.getMatk(), delta.magicAttack());
            short wdef = add(equip.getWdef(), delta.weaponDefense());
            short mdef = add(equip.getMdef(), delta.magicDefense());
            short hp = add(equip.getHp(), delta.hp());
            short mp = add(equip.getMp(), delta.mp());
            short acc = add(equip.getAcc(), delta.accuracy());
            short avoid = add(equip.getAvoid(), delta.avoidability());

            equip.setStr(str);
            equip.setDex(dex);
            equip.setInt(intel);
            equip.setLuk(luk);
            equip.setWatk(watk);
            equip.setMatk(matk);
            equip.setWdef(wdef);
            equip.setMdef(mdef);
            equip.setHp(hp);
            equip.setMp(mp);
            equip.setAcc(acc);
            equip.setAvoid(avoid);
            equip.setFlag((short) (equip.getFlag() | ItemConstants.UNTRADEABLE));
            equip.setEverleafForgeStage((byte) outcome.stage());
            return Result.success(outcome.stage());
        }
    }

    private static short add(short current, int delta) {
        int next = Math.addExact(current, delta);
        if (next > Short.MAX_VALUE) throw new IllegalStateException("forge_stat_overflow");
        return (short) next;
    }
}
