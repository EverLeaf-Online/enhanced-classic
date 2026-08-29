const fs = require("fs");
const { spawn } = require("child_process");
const dotenv = require("dotenv");

const [envPath, outputPath] = process.argv.slice(2);
if (!envPath || !outputPath) {
  throw new Error("Environment path and output path are required.");
}

const values = dotenv.parse(fs.readFileSync(envPath));
const required = ["GAME_DB_HOST", "GAME_DB_USER", "GAME_DB_PASSWORD", "GAME_DB_NAME"];
for (const name of required) {
  if (!values[name]) throw new Error(`Missing required database setting: ${name}`);
}

function completion(child, name) {
  return new Promise((resolve, reject) => {
    child.once("error", reject);
    child.once("close", (code, signal) => {
      if (code === 0) resolve();
      else reject(new Error(`${name} failed with ${signal || `exit code ${code}`}.`));
    });
  });
}

(async () => {
  const output = fs.openSync(outputPath, "wx", 0o600);
  const dump = spawn("mysqldump", [
    "--single-transaction",
    "--quick",
    "--routines",
    "--triggers",
    "--events",
    "--hex-blob",
    "--default-character-set=utf8mb4",
    `--host=${values.GAME_DB_HOST}`,
    `--port=${values.GAME_DB_PORT || "3306"}`,
    `--user=${values.GAME_DB_USER}`,
    "--databases",
    values.GAME_DB_NAME,
  ], {
    env: { ...process.env, MYSQL_PWD: values.GAME_DB_PASSWORD },
    stdio: ["ignore", "pipe", "inherit"],
  });
  const gzip = spawn("gzip", ["-9"], {
    stdio: [dump.stdout, output, "inherit"],
  });
  fs.closeSync(output);

  try {
    await Promise.all([completion(dump, "mysqldump"), completion(gzip, "gzip")]);
    fs.chmodSync(outputPath, 0o600);
    console.log("mysql_backup=ready");
  } catch (error) {
    fs.rmSync(outputPath, { force: true });
    throw error;
  }
})().catch((error) => {
  console.error(`MySQL backup failed: ${error.message}`);
  process.exitCode = 1;
});
