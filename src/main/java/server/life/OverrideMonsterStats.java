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

public class OverrideMonsterStats {

    public int hp;
    public int exp, mp;
    private int watk = -1;
    private int matk = -1;
    private int wdef = -1;
    private int mdef = -1;
    private int level = -1;

    public OverrideMonsterStats() {
        hp = 1;
        exp = 0;
        mp = 0;
    }

    public OverrideMonsterStats(int hp, int mp, int exp, boolean change) {
        this.hp = hp;
        this.mp = mp;
        this.exp = exp;
    }

    public OverrideMonsterStats(int hp, int mp, int exp) {
        this(hp, mp, exp, true);
    }

    /** Full override used by imported encounters whose donor combat stats are not compatible with v83 balance. */
    public OverrideMonsterStats(int hp, int mp, int exp, int watk, int matk, int wdef, int mdef, int level) {
        this(hp, mp, exp);
        this.watk = watk;
        this.matk = matk;
        this.wdef = wdef;
        this.mdef = mdef;
        this.level = level;
    }

    public int getExp() { return exp; }
    public void setOExp(int exp) { this.exp = exp; }
    public int getHp() { return hp; }
    public void setOHp(int hp) { this.hp = hp; }
    public int getMp() { return mp; }
    public void setOMp(int mp) { this.mp = mp; }
    public int getWatk() { return watk; }
    public int getMatk() { return matk; }
    public int getWdef() { return wdef; }
    public int getMdef() { return mdef; }
    public int getLevel() { return level; }
}
