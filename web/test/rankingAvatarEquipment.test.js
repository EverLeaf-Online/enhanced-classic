const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("fs");
const path = require("path");

const avatar = require("../src/routes/avatar")._test;

function appearance(equipment=[]) {
  return {
    skincolor:0,
    hair:30020,
    face:20000,
    equipment
  };
}

test("local renderer keeps only Character.wz-visible equipment categories", () => {
  const visible = [
    1002001, // cap
    1012001, // face accessory
    1022001, // eye accessory
    1032001, // earring
    1040002, // coat
    1050001, // overall
    1060002, // pants
    1072001, // shoes
    1082001, // gloves
    1092001, // shield
    1102001, // cape
    1302000, // weapon
    1702000  // cash weapon
  ];
  const nonVisual = [
    1112000, // ring
    1122000, // pendant
    1132000, // belt
    1142000  // medal
  ];

  for (const id of visible) assert.equal(avatar.localRenderableEquipmentId(id),true,id);
  for (const id of nonVisual) assert.equal(avatar.localRenderableEquipmentId(id),false,id);

  assert.deepEqual(
    avatar.localRendererEquipmentIds(appearance([...visible,...nonVisual])),
    visible
  );
});

test("non-visual equipped slots cannot poison the full WZ compose request", () => {
  const ids = avatar.localRendererIds(appearance([
    1040002,
    1060002,
    1072001,
    1112000,
    1122000,
    1142000,
    1302000
  ]),true);

  assert.deepEqual(ids,[
    "00002000",
    "00012000",
    "00030020",
    "00020000",
    "01040002",
    "01060002",
    "01072001",
    "01302000"
  ]);
});

test("equipmentless retry is explicitly marked as a fallback", () => {
  const source = fs.readFileSync(path.join(__dirname,"../src/routes/avatar.js"),"utf8");
  assert.match(source,/includeEquipment \? "local-wz" : "local-wz-base"/);
  assert.match(source,/X-EverLeaf-Avatar-Mode/);
  assert.match(source,/base-fallback/);
  assert.match(source,/X-EverLeaf-Avatar-Equipment-Count/);
});
