const fs = require("fs");
const { spawn } = require("child_process");
const dotenv = require("dotenv");

const [envPath, outputPath] = process.argv.slice(2);
if (!envPath || !outputPath) {
  throw new Error("Environment path and output path are required.");
}

const values = dotenv.parse(fs.readFileSync(envPath));
if (!values.GAME_DB_NAME) {
  throw new Error("Missing required database setting: GAME_DB_NAME");
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

function resolveDumpConnection() {
  const host = values.GAME_DB_HOST || "127.0.0.1";
  const localHosts = new Set(["127.0.0.1", "localhost", "::1"]);
  const runningAsRoot = typeof process.getuid === "function" && process.getuid() === 0;

  // Production backup-production.sh is run through sudo/systemd on the same
  // host as MySQL. Use MySQL's local root/socket authentication for backups so
  // the website account can remain least-privileged and the dump still covers
  // the complete game schema.
  if (runningAsRoot && localHosts.has(host)) {
    return {
      args: ["--protocol=socket", "--user=root"],
      env: process.env,
      mode: "local-root-socket",
    };
  }

  const required = ["GAME_DB_HOST", "GAME_DB_USER", "GAME_DB_PASSWORD"];
  for (const name of required) {
    if (!values[name]) throw new Error(`Missing required database setting: ${name}`);
  }
  return {
    args: [
      `--host=${values.GAME_DB_HOST}`,
      `--port=${values.GAME_DB_PORT || "3306"}`,
      `--user=${values.GAME_DB_USER}`,
    ],
    env: { ...process.env, MYSQL_PWD: values.GAME_DB_PASSWORD },
    mode: "configured-user",
  };
}

(async () => {
  const connection = resolveDumpConnection();
  const output = fs.openSync(outputPath, "wx", 0o600);
  const dump = spawn("mysqldump", [
    "--single-transaction",
    "--quick",
    "--routines",
    "--triggers",
    "--events",
    "--hex-blob",
    "--default-character-set=utf8mb4",
    ...connection.args,
    // Intentionally do not use --databases here. A schema-neutral dump can
    // be restored safely into a temporary verification database without
    // embedded CREATE DATABASE / USE directives redirecting the import.
    values.GAME_DB_NAME,
  ], {
    env: connection.env,
    stdio: ["ignore", "pipe", "inherit"],
  });
  const gzip = spawn("gzip", ["-9"], {
    stdio: [dump.stdout, output, "inherit"],
  });
  fs.closeSync(output);

  try {
    await Promise.all([completion(dump, "mysqldump"), completion(gzip, "gzip")]);
    fs.chmodSync(outputPath, 0o600);
    console.log(`mysql_backup_mode=${connection.mode}`);
    console.log("mysql_backup=ready");
  } catch (error) {
    fs.rmSync(outputPath, { force: true });
    throw error;
  }
})().catch((error) => {
  console.error(`MySQL backup failed: ${error.message}`);
  process.exitCode = 1;
});
