const game = require("../services/gameService");

async function requireAdmin(req, res, next) {
  // Existing standalone CMS admin login remains supported.
  if (req.session?.admin && req.session.admin.source !== "player") {
    return next();
  }

  // Game-account web admin.
  const player = req.session?.player;

  if (!player) {
    if (req.session?.admin?.source === "player") {
      delete req.session.admin;
    }

    return res.redirect("/admin/login");
  }

  try {
    const allowed = await game.isWebAdmin(player.id);

    if (!allowed) {
      if (req.session?.admin?.source === "player") {
        delete req.session.admin;
      }

      return res.status(403).send("Web admin access denied.");
    }

    req.session.admin = {
      id: null,
      username: player.name,
      source: "player",
      playerId: player.id
    };

    return next();
  } catch (error) {
    console.error("Web admin authorization check failed:", error);

    return res
      .status(503)
      .send("Admin authorization is temporarily unavailable.");
  }
}

module.exports = { requireAdmin };
