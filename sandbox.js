/**
 * generate-project.cjs
 *
 * Generates project structure from JSON templates, installs dependencies,
 * runs Docker Compose, collects logs per service, sends logs to Gemini,
 * and opens the frontend app automatically after logs are processed.
 */

const fs = require("fs");
const path = require("path");
const { execSync } = require("child_process");
const https = require("https");
const http = require("http");
const { exec } = require("child_process");

// ------------------------------
// Load .env
// ------------------------------
function loadEnv() {
  const envPath = path.join(__dirname, ".env");
  if (!fs.existsSync(envPath)) return;

  const lines = fs.readFileSync(envPath, "utf-8").split("\n");
  lines.forEach((line) => {
    if (!line.includes("=")) return;
    if (line.trim().startsWith("#")) return;

    const [key, value] = line.split("=");
    process.env[key.trim()] = value.trim();
  });
}

loadEnv();

// ------------------------------
// Read ENV values
// ------------------------------
const GEMINI_KEY = process.env.GEMINI_API_KEY;
if (!GEMINI_KEY) {
  console.error("❌ Missing GEMINI_API_KEY in .env");
  process.exit(1);
}

let GEMINI_URL = process.env.GEMINI_API_URL;

// Fallback to stable model if unspecified or wrong
if (!GEMINI_URL || GEMINI_URL.includes("v1beta")) {
  GEMINI_URL =
    "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent";
}

const FINAL_GEMINI_URL = `${GEMINI_URL}?key=${GEMINI_KEY}`;

const INPUT_FILES = ["frontend.json", "backend.json", "tests.json", "docker-compose.json"];
const PROJECT_ROOT = "project";
const LOG_ROOT = path.join(PROJECT_ROOT, "docker_logs");

// ------------------------------
// Utility
// ------------------------------
function ensureDir(dir) {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
}

// ------------------------------
function processJson(jsonFile) {
  console.log(`\nProcessing ${jsonFile}...`);

  const parsed = JSON.parse(fs.readFileSync(jsonFile, "utf-8"));

  for (const filepath in parsed) {
    const full = path.join(PROJECT_ROOT, filepath);
    ensureDir(path.dirname(full));
    fs.writeFileSync(full, parsed[filepath]);
    console.log(`Created: ${filepath}`);
  }
}

// ------------------------------
function runNpmInstall(folder) {
  const fullPath = path.join(PROJECT_ROOT, folder);
  if (!fs.existsSync(fullPath)) return console.log(`Missing ${folder}`);

  console.log(`\nInstalling dependencies in ${folder}...`);
  execSync("npm install", { cwd: fullPath, stdio: "inherit" });
}

// ------------------------------
function startDocker() {
  console.log("\nStarting docker compose in detached mode...");
  execSync("docker compose up -d --build", {
    cwd: PROJECT_ROOT,
    stdio: "inherit",
  });
}

// ------------------------------
function getComposeServices() {
  const composePath = path.join(PROJECT_ROOT, "docker-compose.yml");
  if (!fs.existsSync(composePath)) return [];

  const raw = fs.readFileSync(composePath, "utf-8");
  return [...raw.matchAll(/^\s*([a-zA-Z0-9_-]+):\s*$/gm)]
    .map((m) => m[1])
    .filter((n) => n !== "services");
}

// ------------------------------
function detectFrontendPort() {
  const composePath = path.join(PROJECT_ROOT, "docker-compose.yml");
  if (!fs.existsSync(composePath)) return 3000;

  const raw = fs.readFileSync(composePath, "utf-8");

  const match = raw.match(/frontend:[\s\S]*?ports:\s*-\s*["']?(\d+):/);
  return match ? Number(match[1]) : 3000;
}

// ------------------------------
function waitForFrontend(port, timeout = 300000) {
  return new Promise((resolve) => {
    console.log(`\n⏳ Waiting for frontend to be ready on port ${port} ...`);

    const start = Date.now();

    const check = () => {
      http
        .get(`http://localhost:${port}`, () => resolve(true))
        .on("error", () => {
          if (Date.now() - start > timeout) resolve(false);
          else setTimeout(check, 2000);
        });
    };

    check();
  });
}

// ------------------------------
function openBrowser(url) {
  console.log(`\n🌐 Opening browser at: ${url}`);

  const cmds = {
    win32: `start "" "${url}"`,
    darwin: `open "${url}"`,
    linux: `xdg-open "${url}"`,
  };

  exec(cmds[process.platform] || cmds.linux);
}

// ------------------------------
function saveLogs() {
  ensureDir(LOG_ROOT);
  console.log("\nSaving container logs...");

  const services = getComposeServices();
  const ts = new Date().toISOString().replace(/[:.]/g, "-");

  const outFiles = [];

  services.forEach((svc) => {
    const logFile = path.join(LOG_ROOT, `${svc}_log_${ts}.txt`);
    try {
      const logs = execSync(`docker compose logs --no-color ${svc}`, {
        cwd: PROJECT_ROOT,
        encoding: "utf-8",
      });
      fs.writeFileSync(logFile, logs);
      console.log(`✓ Saved logs for ${svc}`);
      outFiles.push(logFile);
    } catch {
      fs.writeFileSync(logFile, "ERROR: Failed to read logs");
      outFiles.push(logFile);
    }
  });

  return outFiles;
}

// ------------------------------
function sendToGemini(files) {
  console.log("\nSending logs to Gemini...");

  const fullText = files
    .map((f) => `### LOG: ${path.basename(f)}\n\n${fs.readFileSync(f, "utf-8")}`)
    .join("\n\n");

  const payload = JSON.stringify({
    contents: [
      {
        parts: [{ text: fullText }],
      },
    ],
  });

  return new Promise((resolve, reject) => {
    const url = new URL(FINAL_GEMINI_URL);

    const req = https.request(
      {
        hostname: url.hostname,
        path: url.pathname + url.search,
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Content-Length": Buffer.byteLength(payload),
        },
      },
      (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => resolve(data));
      }
    );

    req.on("error", reject);
    req.write(payload);
    req.end();
  });
}

// ------------------------------
async function main() {
  console.log("\n=== Generating Project ===");
  ensureDir(PROJECT_ROOT);

  INPUT_FILES.forEach(processJson);

  runNpmInstall("frontend");
  runNpmInstall("backend");
  runNpmInstall("tests");

  startDocker();

  const logs = saveLogs();

  const response = await sendToGemini(logs);

  const outFile = path.join(LOG_ROOT, "gemini_analysis.txt");
  fs.writeFileSync(outFile, response);

  console.log("\n✓ Gemini analysis saved to:", outFile);

  // -------------------------
  // AUTO-OPEN FRONTEND NOW
  // -------------------------
  const port = detectFrontendPort();
  const url = `http://localhost:${port}`;

  const ready = await waitForFrontend(port);
  if (ready) {
    console.log(`\n🚀 Frontend is ready at: ${url}`);
    openBrowser(url);
  } else {
    console.log(`\n⚠ Frontend did not become ready. Start manually: ${url}`);
  }

  console.log("\n🎉 Done!");
}

main();
