const env = require("../config/env");
const { getPool, safeIdent: I } = require("../db/game");
const game = require("./gameService");

async function baseAppearance(characterId) {
  const id = Number(characterId);
  if (!Number.isInteger(id) || id <= 0) return null;
  const db = getPool(), g = env.gameDb;
  const [characters] = await db.query(`
    SELECT
      c.${I(g.characterId)} id,
      c.${I(g.characterJob)} job,
      c.${I(g.characterSkin)} skincolor,
      c.${I(g.characterFace)} face,
      c.${I(g.characterHair)} hair
    FROM ${I(g.charactersTable)} c
    INNER JOIN ${I(g.accountsTable)} a
      ON a.${I(g.accountId)}=c.${I(g.characterAccountId)}
    WHERE c.${I(g.characterId)}=?
      AND COALESCE(c.${I(g.characterGm)},0)=0
      AND COALESCE(a.${I(g.accountBanned)},0)=0
    LIMIT 1
  `,[id]);
  const character = characters[0];
  if (!character) return null;
  return {
    id:Number(character.id),
    job:Number(character.job || 0),
    skincolor:Number(character.skincolor || 0),
    face:Number(character.face || 0),
    hair:Number(character.hair || 0),
    equipment:[]
  };
}

async function characterAppearance(characterId) {
  try {
    return await game.characterAppearance(characterId);
  } catch (error) {
    console.warn(`Full character appearance lookup failed for ${Number(characterId) || 0}; retrying without equipment:`,error.message);
    return baseAppearance(characterId);
  }
}

module.exports = { characterAppearance, baseAppearance };
