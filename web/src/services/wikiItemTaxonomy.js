const cashEquipIndex = require("../generated/wiki-cash-equip-ids.json");
const CASH_EQUIP_IDS = new Set((cashEquipIndex.cashEquipIds || []).map(Number));
const CASH_MODES = new Set(["all", "noncash", "cash"]);

const GROUPS = [
  {
    label: "Equipment",
    options: [
      ["equipment", "All Equipment"],
      ["equipment-appearance", "All Hair / Face"],
      ["equipment-face-style", "Face Styles"],
      ["equipment-hair-style", "Hair Styles"],
      ["equipment-hat", "Hats"],
      ["equipment-face", "Face Accessories"],
      ["equipment-eye", "Eye Accessories"],
      ["equipment-earring", "Earrings"],
      ["equipment-top", "Tops"],
      ["equipment-overall", "Overalls"],
      ["equipment-bottom", "Bottoms"],
      ["equipment-shoes", "Shoes"],
      ["equipment-gloves", "Gloves"],
      ["equipment-shield", "Shields"],
      ["equipment-cape", "Capes"],
      ["equipment-ring", "Rings"],
      ["equipment-pendant", "Pendants"],
      ["equipment-belt", "Belts"],
      ["equipment-medal", "Medals"],
      ["equipment-shoulder", "Shoulder Accessories"],
      ["equipment-other-accessory", "Badges / Emblems / Totems / Other Accessories"],
      ["equipment-weapon", "Weapons / Tools"],
      ["equipment-cash-weapon", "Cash Weapons"],
      ["equipment-pet", "Pet Equipment"],
      ["equipment-mount", "Mounts / Saddles"],
      ["equipment-other", "Other Equipment"]
    ]
  },
  {
    label: "Consumables",
    options: [
      ["consumables", "All Consumables"],
      ["consumable-scroll", "Scrolls"],
      ["consumable-potion-food", "Potions / Food"],
      ["consumable-cure", "Cures / Status Recovery"],
      ["consumable-ammo", "Throwing Stars / Arrows / Bullets"],
      ["consumable-skill-book", "Skill / Mastery Books"],
      ["consumable-travel", "Travel / Return Items"],
      ["consumable-summon", "Summoning Sacks"],
      ["consumable-monster-card", "Monster Cards"],
      ["consumable-pet-food", "Pet Food"],
      ["consumable-other", "Other Consumables"]
    ]
  },
  {
    label: "Install / Setup",
    options: [
      ["install", "All Install / Setup"],
      ["install-chair", "Chairs"],
      ["install-other", "Other Install / Setup"]
    ]
  },
  {
    label: "ETC",
    options: [
      ["etc", "All ETC"],
      ["etc-monster-drop", "Monster Drops"],
      ["etc-material", "Ores / Crystals / Materials"],
      ["etc-quest", "Quest Items"],
      ["etc-crafting", "Crafting / Production"],
      ["etc-storybook", "Storybooks / Manuals"],
      ["etc-token", "Coins / Tokens / Currencies"],
      ["etc-other", "Other ETC"]
    ]
  },
  {
    label: "Cash / Pets",
    options: [
      ["cash", "All Cash Items"],
      ["pets", "Pets"],
      ["cash-pet", "Pet Care / Pet Skills"],
      ["cash-appearance", "Hair / Face / Appearance Coupons"],
      ["cash-travel", "Teleport / Travel"],
      ["cash-messaging", "Megaphones / Messages / Chalkboards"],
      ["cash-shop", "Store / Merchant Items"],
      ["cash-exp-drop", "EXP / Drop Coupons"],
      ["cash-ticket-box", "Tickets / Boxes / Keys"],
      ["cash-reset", "AP / SP / Character Services"],
      ["cash-other", "Other Cash Items"]
    ]
  }
];

const LABELS = new Map([["all", "All Item Categories"]]);
for (const group of GROUPS) for (const [key, label] of group.options) LABELS.set(key, label);

function itemPrefix(entity) {
  const id = Number(entity?.id);
  if (!Number.isInteger(id) || id < 0) return -1;
  return Math.floor(id / 10000);
}

function itemFamily(entity) {
  const subtype = String(entity?.subtype || "");
  if (subtype === "Equipment") return "equipment";
  if (subtype === "Consumable") return "consumables";
  if (subtype === "Install / Chair") return "install";
  if (subtype === "ETC") return "etc";
  if (subtype === "Cash") return "cash";
  if (subtype === "Pet") return "pets";
  return "other";
}

function validCashMode(value) {
  const mode = String(value || "all").toLowerCase();
  return CASH_MODES.has(mode) ? mode : "all";
}

// Mirror server.ItemInformationProvider#isCash exactly: every type-5 item is
// cash, and type-1 equipment is cash only when Character.wz info/cash=1.
function isCashItem(entity) {
  const id = Number(entity?.id);
  if (!Number.isInteger(id) || id <= 0) return false;
  const itemType = Math.floor(id / 1000000);
  if (itemType === 5) return true;
  if (itemType !== 1) return false;
  return CASH_EQUIP_IDS.has(id);
}

function matchesCash(entity, mode = "all") {
  const selected = validCashMode(mode);
  if (selected === "all") return true;
  const cash = isCashItem(entity);
  return selected === "cash" ? cash : !cash;
}

function cashCounts(rows = []) {
  let cash = 0;
  for (const row of rows) if (isCashItem(row)) cash += 1;
  return { all: rows.length, cash, noncash: rows.length - cash };
}

function leafCategory(entity) {
  const family = itemFamily(entity);
  const prefix = itemPrefix(entity);
  const id = Number(entity?.id || 0);
  const name = String(entity?.name || "");

  if (family === "equipment") {
    if (id >= 20000 && id < 30000) return "equipment-face-style";
    if (id >= 30000 && id < 1000000) return "equipment-hair-style";
    if (prefix === 100) return "equipment-hat";
    if (prefix === 101) return "equipment-face";
    if (prefix === 102) return "equipment-eye";
    if (prefix === 103) return "equipment-earring";
    if (prefix === 104) return "equipment-top";
    if (prefix === 105) return "equipment-overall";
    if (prefix === 106) return "equipment-bottom";
    if (prefix === 107) return "equipment-shoes";
    if (prefix === 108) return "equipment-gloves";
    if (prefix === 109) return "equipment-shield";
    if (prefix === 110) return "equipment-cape";
    if (prefix === 111) return "equipment-ring";
    if (prefix === 112) return "equipment-pendant";
    if (prefix === 113) return "equipment-belt";
    if (prefix === 114) return "equipment-medal";
    if (prefix === 115) return "equipment-shoulder";
    if ([116, 117, 118, 119, 120, 169].includes(prefix)) return "equipment-other-accessory";
    if (prefix >= 121 && prefix <= 159) return "equipment-weapon";
    if (prefix === 170) return "equipment-cash-weapon";
    if (prefix >= 180 && prefix <= 183) return "equipment-pet";
    if (prefix >= 190 && prefix <= 199) return "equipment-mount";
    return "equipment-other";
  }

  if (family === "consumables") {
    if (prefix === 204 || prefix === 234 || /\bscroll\b/i.test(name)) return "consumable-scroll";
    if ([200, 201].includes(prefix) || /\b(?:potion|elixir|pill|food|juice|milk|water)\b/i.test(name)) return "consumable-potion-food";
    if (prefix === 205) return "consumable-cure";
    if ([206, 207, 233].includes(prefix)) return "consumable-ammo";
    if ([228, 229].includes(prefix) || /\b(?:skill|mastery)\s+book\b/i.test(name)) return "consumable-skill-book";
    if ([203, 232].includes(prefix) || /\b(?:return|teleport|warp)\b/i.test(name)) return "consumable-travel";
    if (prefix === 210 || /summoning\s+sack/i.test(name)) return "consumable-summon";
    if (prefix === 238 || /\bcard\b/i.test(name) && /monster/i.test(String(entity?.description || ""))) return "consumable-monster-card";
    if (prefix === 212 || /\bpet\s+food\b/i.test(name)) return "consumable-pet-food";
    return "consumable-other";
  }

  if (family === "install") {
    if (prefix === 301 || /\bchair\b/i.test(name)) return "install-chair";
    return "install-other";
  }

  if (family === "etc") {
    if (prefix === 400) return "etc-monster-drop";
    if ([401, 402, 425, 426, 444].includes(prefix)) return "etc-material";
    if (prefix === 403) return "etc-quest";
    if ([411, 413, 433].includes(prefix)) return "etc-crafting";
    if ([416, 446].includes(prefix) || /\b(?:storybook|manual)\b/i.test(name)) return "etc-storybook";
    if ([431, 443].includes(prefix) || /\b(?:coin|token|currency)\b/i.test(name)) return "etc-token";
    return "etc-other";
  }

  if (family === "pets") return "pets";

  if (family === "cash") {
    if ([517, 518, 519, 524, 538, 546].includes(prefix) || /\bpet\b/i.test(name)) return "cash-pet";
    if ([515, 542].includes(prefix) || /\b(?:hair|face|skin|cosmetic)\b.*\bcoupon\b/i.test(name)) return "cash-appearance";
    if ([504, 533].includes(prefix) || /\b(?:teleport|travel|delivery)\b/i.test(name)) return "cash-travel";
    if ([507, 508, 509, 537, 539].includes(prefix) || /\b(?:megaphone|messenger|chalkboard|banner|note)\b/i.test(name)) return "cash-messaging";
    if ([503, 514, 545, 547].includes(prefix) || /\b(?:store|merchant|cashier)\b/i.test(name)) return "cash-shop";
    if ([521, 536].includes(prefix) || /\b(?:exp|drop)\b.*\b(?:coupon|card)\b/i.test(name)) return "cash-exp-drop";
    if ([522, 525, 549, 553].includes(prefix) || /\b(?:ticket|box|key|gachapon)\b/i.test(name)) return "cash-ticket-box";
    if ([505, 540, 543].includes(prefix) || /\b(?:ap reset|sp reset|character name change|character transfer|character slot)\b/i.test(name)) return "cash-reset";
    return "cash-other";
  }

  return "other";
}

function validCategory(value) {
  const key = String(value || "all");
  return LABELS.has(key) ? key : "all";
}

function matches(entity, category) {
  const key = validCategory(category);
  if (key === "all") return true;
  const family = itemFamily(entity);
  if (["equipment", "consumables", "install", "etc", "cash", "pets"].includes(key)) return family === key;
  const leaf = leafCategory(entity);
  if (key === "equipment-appearance") return leaf === "equipment-face-style" || leaf === "equipment-hair-style";
  return leaf === key;
}

function counts(rows = []) {
  const result = Object.fromEntries([...LABELS.keys()].map(key => [key, 0]));
  result.all = rows.length;
  for (const row of rows) {
    const family = itemFamily(row);
    const leaf = leafCategory(row);
    if (result[family] != null) result[family] += 1;
    if (result[leaf] != null && leaf !== family) result[leaf] += 1;
    if ((leaf === "equipment-face-style" || leaf === "equipment-hair-style") && result["equipment-appearance"] != null) result["equipment-appearance"] += 1;
  }
  return result;
}

function decorate(entity) {
  if (entity?.type !== "items") return entity;
  const key = leafCategory(entity);
  return {
    ...entity,
    itemFamily: itemFamily(entity),
    itemCategory: key,
    itemCategoryLabel: LABELS.get(key) || "Other"
  };
}

module.exports = {
  GROUPS,
  LABELS,
  itemFamily,
  leafCategory,
  validCategory,
  validCashMode,
  isCashItem,
  matchesCash,
  cashCounts,
  matches,
  counts,
  decorate,
  _test: { itemPrefix }
};
