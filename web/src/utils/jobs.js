const jobs = {
  0:"Beginner",
  100:"Warrior",110:"Fighter",111:"Crusader",112:"Hero",
  120:"Page",121:"White Knight",122:"Paladin",130:"Spearman",131:"Dragon Knight",132:"Dark Knight",
  200:"Magician",210:"F/P Wizard",211:"F/P Mage",212:"F/P Arch Mage",220:"I/L Wizard",221:"I/L Mage",222:"I/L Arch Mage",
  230:"Cleric",231:"Priest",232:"Bishop",
  300:"Bowman",310:"Hunter",311:"Ranger",312:"Bowmaster",320:"Crossbowman",321:"Sniper",322:"Marksman",
  400:"Thief",410:"Assassin",411:"Hermit",412:"Night Lord",420:"Bandit",421:"Chief Bandit",422:"Shadower",
  500:"Pirate",510:"Brawler",511:"Marauder",512:"Buccaneer",520:"Gunslinger",521:"Outlaw",522:"Corsair",
  800:"MapleLeaf Brigadier",900:"GM",910:"SuperGM",
  1000:"Noblesse",
  1100:"Dawn Warrior",1110:"Dawn Warrior",1111:"Dawn Warrior",1112:"Dawn Warrior",
  1200:"Blaze Wizard",1210:"Blaze Wizard",1211:"Blaze Wizard",1212:"Blaze Wizard",
  1300:"Wind Archer",1310:"Wind Archer",1311:"Wind Archer",1312:"Wind Archer",
  1400:"Night Walker",1410:"Night Walker",1411:"Night Walker",1412:"Night Walker",
  1500:"Thunder Breaker",1510:"Thunder Breaker",1511:"Thunder Breaker",1512:"Thunder Breaker",
  2000:"Legend",2001:"Evan",
  2100:"Aran",2110:"Aran",2111:"Aran",2112:"Aran",
  2200:"Evan",2210:"Evan",2211:"Evan",2212:"Evan",2213:"Evan",2214:"Evan",2215:"Evan",2216:"Evan",2217:"Evan",2218:"Evan"
};
module.exports = id => jobs[Number(id)] || `Job ${id}`;
