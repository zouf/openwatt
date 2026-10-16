// Rebuilds the Tailwind CSS that is inlined in index.html.
// The page used to load the Tailwind Play CDN, which compiles CSS in the
// browser on every load and leaves the app unstyled without a connection.
// Run this after adding or changing any Tailwind classes:
//
//   node scripts/build-css.mjs
//
import { readFileSync, writeFileSync, mkdtempSync } from "node:fs";
import { execFileSync } from "node:child_process";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const root = join(dirname(fileURLToPath(import.meta.url)), "..");
const file = join(root, "index.html");
const START = '<style id="tailwind">';
const END = "</style><!-- /tailwind -->";

const html = readFileSync(file, "utf8");
const i = html.indexOf(START);
const j = html.indexOf(END);
if (i < 0 || j < i) throw new Error("tailwind markers not found in index.html");

// Scan the page without the previous build so stale classes drop out.
const dir = mkdtempSync(join(tmpdir(), "openwatt-css-"));
writeFileSync(join(dir, "src.html"), html.slice(0, i) + html.slice(j + END.length));
writeFileSync(join(dir, "in.css"), "@tailwind base;\n@tailwind components;\n@tailwind utilities;\n");
execFileSync(
  "npx",
  ["--yes", "tailwindcss@3.4.17", "-i", join(dir, "in.css"), "--content", join(dir, "src.html"), "-o", join(dir, "out.css"), "--minify"],
  { stdio: "inherit" },
);
const css = readFileSync(join(dir, "out.css"), "utf8").trim();
writeFileSync(file, html.slice(0, i) + START + css + END + html.slice(j + END.length));
console.log(`Inlined ${css.length} bytes of CSS into index.html`);
