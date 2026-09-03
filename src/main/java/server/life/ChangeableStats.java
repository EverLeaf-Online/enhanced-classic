/*
This file is part of the OdinMS Maple Story Server
Copyright (C) 2008 ~ 2010 Patrick Huy <patrick.huy@frz.cc>
Matthias Butz <matze@odinms.de>
Jan Christian Meyer <vimes@odinms.de>
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License version 3
as published by the Free Software Foundation. You may not use, modify
or distribute this program under any other version of the
GNU Affero General Public License.
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.
You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */
package server.life;

import constants.game.GameConstants;

public class ChangeableStats extends OverrideMonsterStats {

    public int watk, matk, wdef, mdef, level;

    public ChangeableStats(MonsterStats stats, OverrideMonsterStats ostats) {
        hp = ostats.getHp();
        exp = ostats.getExp();
        mp = ostats.getMp();
        watk = ostats.getWatk() >= 0 ? ostats.getWatk() : stats.getPADamage();
        matk = ostats.getMatk() >= 0 ? ostats.getMatk() : stats.getMADamage();
        wdef = ostats.getWdef() >= 0 ? ostats.getWdef() : stats.getPDDamage();
        mdef = ostats.getMdef() >= 0 ? ostats.getMdef() : stats.getMDDamage();
        level = ostats.getLevel() >= 0 ? ostats.getLevel() : stats.getLevel();
    }

    public ChangeableStats(MonsterStats stats, int newLevel, boolean pqMob) {
        final double mod = (double) newLevel / (double) stats.getLevel();
        final double hpRatio = (double) stats.getHp() / (double) stats.getExp();
        final double pqMod = (pqMob ? 1.5 : 1.0);
        hp = Math.min((int) Math.round((!stats.isBoss() ? GameConstants.getMonsterHP(newLevel) : (stats.getHp() * mod)) * pqMod), Integer.MAX_VALUE);
        exp = Math.min((int) Math.round((!stats.isBoss() ? (GameConstants.getMonsterHP(newLevel) / hpRatio) : (stats.getExp())) * pqMod), Integer.MAX_VALUE);
        mp = Math.min((int) Math.round(stats.getMp() * mod * pqMod), Integer.MAX_VALUE);
        watk = Math.min((int) Math.round(stats.getPADamage() * mod), Integer.MAX_VALUE);
        matk = Math.min((int) Math.round(stats.getMADamage() * mod), Integer.MAX_VALUE);
        wdef = Math.min(Math.min(stats.isBoss() ? 30 : 20, (int) Math.round(stats.getPDDamage() * mod)), Integer.MAX_VALUE);
        mdef = Math.min(Math.min(stats.isBoss() ? 30 : 20, (int) Math.round(stats.getMDDamage() * mod)), Integer.MAX_VALUE);
        level = newLevel;
    }

    public ChangeableStats(MonsterStats stats, float statModifier, boolean pqMob) {
        this(stats, (int) (statModifier * stats.getLevel()), pqMob);
    }
}
