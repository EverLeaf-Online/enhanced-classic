const GAME_PASSWORD_MIN_LENGTH = 8;
const GAME_PASSWORD_MAX_LENGTH = 12;

function isGameCompatiblePassword(value) {
  const length = String(value || "").length;
  return length >= GAME_PASSWORD_MIN_LENGTH && length <= GAME_PASSWORD_MAX_LENGTH;
}

module.exports = {
  GAME_PASSWORD_MIN_LENGTH,
  GAME_PASSWORD_MAX_LENGTH,
  isGameCompatiblePassword
};
