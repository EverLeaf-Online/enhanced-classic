const fs = require("fs");
const path = require("path");
const dotenv = require("dotenv");

const [webRoot, envPath, outputPath] = process.argv.slice(2);
if (!webRoot || !envPath || !outputPath) {
  throw new Error("Web root, environment path, and output path are required.");
}

const values = dotenv.parse(fs.readFileSync(envPath));
const configuredPath = values.CMS_DB_PATH || "./data/everleaf-cms.sqlite";
const databasePath = path.isAbsolute(configuredPath)
  ? configuredPath
  : path.resolve(webRoot, configuredPath);
const Database = require(path.join(webRoot, "node_modules", "better-sqlite3"));

(async () => {
  const database = new Database(databasePath, { readonly: true, fileMustExist: true });
  try {
    await database.backup(outputPath);
  } finally {
    database.close();
  }
  fs.chmodSync(outputPath, 0o600);
  console.log("cms_backup=ready");
})().catch((error) => {
  console.error(`CMS backup failed: ${error.message}`);
  process.exitCode = 1;
});
