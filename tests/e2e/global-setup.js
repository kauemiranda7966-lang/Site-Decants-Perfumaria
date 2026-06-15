const { spawn } = require("node:child_process");
const { existsSync } = require("node:fs");
const { join } = require("node:path");

function findPython() {
  const candidates = [
    process.env.PYTHON,
    join(process.cwd(), ".venv", "Scripts", "python.exe"),
    process.env.USERPROFILE
      ? join(
          process.env.USERPROFILE,
          ".cache",
          "codex-runtimes",
          "codex-primary-runtime",
          "dependencies",
          "python",
          "python.exe"
        )
      : ""
  ].filter(Boolean);
  return candidates.find(candidate => existsSync(candidate)) || "python";
}

async function waitForServer(child) {
  const deadline = Date.now() + 30000;
  while (Date.now() < deadline) {
    if (child.exitCode !== null) {
      throw new Error(`Servidor E2E encerrou com codigo ${child.exitCode}.`);
    }
    try {
      const response = await fetch("http://127.0.0.1:8765/api/products");
      if (response.ok) return;
    } catch (error) {
      // O processo ainda esta inicializando.
    }
    await new Promise(resolve => setTimeout(resolve, 200));
  }
  throw new Error("Servidor E2E nao ficou disponivel em 30 segundos.");
}

module.exports = async () => {
  const python = findPython();
  const child = spawn(python, ["tests/e2e_server.py"], {
    cwd: process.cwd(),
    env: process.env,
    stdio: "ignore",
    windowsHide: true
  });

  await waitForServer(child);

  return async () => {
    if (child.exitCode !== null) return;
    child.kill();
    await Promise.race([
      new Promise(resolve => child.once("exit", resolve)),
      new Promise(resolve => setTimeout(resolve, 5000))
    ]);
  };
};
