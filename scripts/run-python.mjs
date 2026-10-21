import { spawnSync } from "node:child_process";
import { resolve } from "node:path";
const executable = resolve(
  "backend/.venv",
  process.platform === "win32" ? "Scripts/python.exe" : "bin/python",
);
const result = spawnSync(executable, process.argv.slice(2), {
  stdio: "inherit",
});
if (result.error) {
  process.stderr.write("Configure o ambiente Python em backend/.venv.\n");
}
process.exit(result.status ?? 1);
