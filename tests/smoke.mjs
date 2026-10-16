// End-to-end checks for OpenWatt, run in headless Chromium with a simulated
// FTMS trainer. Usage:  npm install && npx playwright install chromium && npm test
import { chromium } from "playwright";
import { fileURLToPath, pathToFileURL } from "node:url";
import { dirname, join } from "node:path";
import { DOMParser } from "@xmldom/xmldom";

const PAGE = pathToFileURL(join(dirname(fileURLToPath(import.meta.url)), "..", "index.html")).href;

// Fake Web Bluetooth: one FTMS trainer. Only writeValue() (no
// writeValueWithResponse) and concurrent writes throw, like iOS.
const MOCK_BLE = `
(() => {
  const log = (window.__ble = { requests: [], writes: [] });
  const U = (n) => "0000" + n.toString(16).padStart(4, "0") + "-0000-1000-8000-00805f9b34fb";
  class Char extends EventTarget {
    constructor(uuid, props) { super(); this.uuid = uuid; this.properties = props; }
    async startNotifications() { return this; }
    async writeValue(d) {
      if (window.__busy) throw new Error("GATT operation already in progress");
      window.__busy = true; await new Promise((r) => setTimeout(r, 20)); window.__busy = false;
      log.writes.push(Array.from(d));
      if (this === cp) {
        const ok = !(window.__refuseControl && d[0] === 0x00);
        const res = new DataView(new Uint8Array([0x80, d[0], ok ? 1 : 5]).buffer);
        setTimeout(() => this.emit(res), 5);
      }
    }
    emit(dv) { Object.defineProperty(this, "value", { value: dv, configurable: true }); this.dispatchEvent(new Event("characteristicvaluechanged")); }
  }
  const data = new Char(U(0x2ad2), { notify: true });
  const cp = new Char(U(0x2ad9), { indicate: true, write: true });
  const svc = (uuid, chars) => ({ uuid, async getCharacteristic(u) { const c = chars.find((c) => c.uuid === u); if (!c) throw new Error("no char"); return c; }, async getCharacteristics() { return chars; } });
  const services = { [U(0x1826)]: svc(U(0x1826), [data, cp]) };
  const device = new EventTarget();
  device.name = "KICKR BIKE TEST";
  const server = { device, async getPrimaryServices() { return Object.values(services); },
    async getPrimaryService(u) { if (typeof u !== "string") throw new Error("numeric UUID"); const s = services[u]; if (!s) throw new Error("not found"); return s; } };
  device.gatt = { async connect() { if (window.__refuseConnect) throw new Error("Connection failed"); return server; },
    disconnect() { device.dispatchEvent(new Event("gattserverdisconnected")); } };
  window.__device = device;
  // flags: cadence(2) + power(6) + HR(9); "more data" bit 0 set so no speed field
  window.__notify = (watts, cad, hr) => {
    const dv = new DataView(new ArrayBuffer(9));
    dv.setUint16(0, 1 | (1 << 2) | (1 << 6) | (1 << 9), true);
    dv.setUint16(2, cad * 2, true); dv.setInt16(4, watts, true); dv.setUint8(6, hr);
    data.emit(dv);
  };
  Object.defineProperty(navigator, "bluetooth", { value: { async requestDevice(o) { log.requests.push(JSON.parse(JSON.stringify(o))); return device; } } });
})();`;

let failures = 0;
const check = (name, ok, detail = "") => {
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}${detail ? "  (" + detail + ")" : ""}`);
  if (!ok) failures++;
};

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 375, height: 667 }, isMobile: true, hasTouch: true, acceptDownloads: true });
const errors = [];
const open = async (withBle) => {
  const p = await ctx.newPage();
  if (withBle) await p.addInitScript(MOCK_BLE);
  p.on("pageerror", (e) => errors.push(e.message));
  await p.route("https://fonts.googleapis.com/**", (r) => r.fulfill({ contentType: "text/css", body: "" }));
  await p.goto(PAGE);
  await p.waitForTimeout(400);
  return p;
};

// ---- Demo-mode behaviour (no Bluetooth) -------------------------------------
let p = await open(false);
const riders = await p.evaluate(() => state.profiles.map((r) => `${r.name}:${r.ftp}`).join(","));
check("built-in riders Matt (320) and Kate (280), Matt active", riders === "Matt:320,Kate:280" && (await p.evaluate(() => getActiveProfile().name)) === "Matt", riders);

// Existing device with the old placeholder plus a custom rider: built-ins added once.
await p.evaluate(() => {
  localStorage.clear();
  localStorage.setItem("openwatt_profiles_v2", JSON.stringify([
    { id: "p1", name: "Rider 1", ftp: 250, bias: 100 },
    { id: "x", name: "kate", ftp: 265, bias: 100 },
  ]));
});
await p.reload();
await p.waitForTimeout(300);
const migrated = await p.evaluate(() => state.profiles.map((r) => `${r.name}:${r.ftp}`).join(","));
check("existing devices get Matt added, keep their own Kate, lose the placeholder", migrated === "Matt:320,kate:265", migrated);
await p.evaluate(() => { removeProfile("rider_matt"); });
await p.reload();
await p.waitForTimeout(300);
check("a deleted built-in rider stays deleted", !(await p.evaluate(() => state.profiles.some((r) => r.name === "Matt"))));
await p.evaluate(() => localStorage.clear());
await p.reload();
await p.waitForTimeout(300);
check("fits a 375px phone without horizontal scroll", (await p.evaluate(() => document.documentElement.scrollWidth)) <= 375);
check("Bluetooth notice shown when unavailable", !(await p.$eval("#ble-notice", (e) => e.classList.contains("hidden"))));
check("Tailwind is inlined (no CDN)", await p.evaluate(() => !document.querySelector('script[src*="tailwind"]') && getComputedStyle(document.body).display === "flex"));

// chart preview: hovering a block shows its target and timing
const ramps = await p.evaluate(() => {
  const w = WORKOUT_PRESETS.find((x) => x.id === "mz_stairs60");
  return buildSegments(w.blocks, 320).filter((g) => g.ramp).map((g) => `${g.a}-${g.b}`).join(",");
});
check("ramp steps are grouped into single ramps", ramps === "60-65,65-70,70-60,60-50", ramps);
{
  const box = await p.$eval("#chart-area", (e) => { e.scrollIntoView({ block: "center" }); const r = e.getBoundingClientRect(); return { x: r.x, y: r.y, w: r.width, h: r.height }; });
  await p.touchscreen.tap(box.x + box.w * 0.5, box.y + box.h * 0.4);
  await p.waitForTimeout(200);
  const tip = await p.$eval("#chart-tip", (e) => (e.classList.contains("hidden") ? "" : e.innerText));
  check("tapping the chart previews that block", /% FTP · \d+ W/.test(tip) && /Starts at/.test(tip), tip.replace(/\n+/g, " | "));
}

await p.click("#btn-engine-control");
check("first Start without a trainer asks before a demo ride", await p.evaluate(() => state.runState === "STOPPED"));
await p.click("#btn-engine-control");
check("second Start begins a demo ride", await p.evaluate(() => state.runState === "RUNNING" && state.rideIsDemo));

const r1 = await p.evaluate(() => {
  for (let i = 0; i < 90; i++) tickLoop();
  mutateSection("RESTART");
  for (let i = 0; i < 20; i++) tickLoop();
  const t = state.history.map((h) => h.t);
  return t.every((v, i) => i === 0 || v > t[i - 1]);
});
check("ride timestamps stay increasing after Restart", r1);

const perf = await p.evaluate(() => {
  for (let i = 0; i < 5400; i++) addToStats({ p: 200, cad: 90, hr: 140 });
  const t0 = performance.now();
  for (let i = 0; i < 100; i++) updateStatsBar();
  return (performance.now() - t0) / 100;
});
check("stats update stays cheap at 90 min", perf < 1, `${perf.toFixed(3)} ms`);

await p.evaluate(() => terminateWorkoutRun());
await p.evaluate(() => {
  parseWorkoutFileContent("test.ERG", "[COURSE HEADER]\nMINUTES WATTS\n[END COURSE HEADER]\n[COURSE DATA]\n0 200\n10 200\n[END COURSE DATA]\n");
});
const erg = await p.evaluate(() => {
  const b = state.activeWorkout.blocks[0];
  const out = [];
  for (const ftp of [150, 300]) out.push(targetWattsFor(b, { ftp, bias: 100 }));
  return out;
});
check(".erg (uppercase ext) loads as absolute watts for any FTP", erg[0] === 200 && erg[1] === 200, erg.join("/"));

await p.reload();
await p.waitForTimeout(400);
check("loaded workout survives a reload", await p.evaluate(() => state.activeWorkout.name === "test"));

// unfinished ride -> offered for resume after reload
await p.evaluate(() => {
  state.demoConfirmUntil = Date.now() + 5000;
  toggleEngineExecution();
  for (let i = 0; i < 45; i++) tickLoop();
  saveRide(false);
});
await p.reload();
await p.waitForTimeout(700);
const offered = await p.$eval("#toast-action", (e) => !e.classList.contains("hidden") && e.textContent.trim() === "Resume");
check("unfinished ride is offered for resume", offered);
if (offered) await p.click("#toast-action");
check("resume restores position and samples (paused)", await p.evaluate(() => state.runState === "PAUSED" && state.history.length === 45 && state.clockTime === 45));
await p.close();

// ---- Real-trainer behaviour (mock FTMS) ------------------------------------
p = await open(true);
await p.evaluate(() => localStorage.clear());
await p.reload();
await p.waitForTimeout(400);
await p.click("#nav-devices");
await p.click("#btn-connect-trainer");
await p.waitForTimeout(500);
const req = await p.evaluate(() => window.__ble.requests[0]);
check("requests FTMS by full 128-bit UUID", req && req.filters[0].services[0] === "00001826-0000-1000-8000-00805f9b34fb");
check("requests control then start", JSON.stringify(await p.evaluate(() => window.__ble.writes)) === "[[0],[7]]");

await p.click("#nav-workout");
await p.selectOption("#select-workout", "3"); // Tempo 3x10: 600s @50%, then 85%
await p.click("#btn-engine-control");
check("Start with a trainer begins immediately", await p.evaluate(() => state.runState === "RUNNING" && !state.rideIsDemo));

const avg = await p.evaluate(async () => {
  window.__notify(200, 90, 150);
  window.__notify(300, 92, 151);
  tickLoop();
  return { p: state.history.at(-1).p, hr: state.telemetry.hr, cad: state.history.at(-1).cad };
});
check("records the per-second mean of trainer power", avg.p === 250, `got ${avg.p}`);
check("reads HR relayed by the trainer", avg.hr === 151);

await p.evaluate(() => { window.__ble.writes = []; state.clockTime = 598; state.blockTimeElapsed = 598; for (let i = 0; i < 3; i++) tickLoop(); });
await p.waitForTimeout(300);
const w = await p.evaluate(() => window.__ble.writes.map((x) => x[1] + (x[2] << 8)));
const ftpNow = await p.evaluate(() => getActiveProfile().ftp);
check("new ERG target sent as soon as the block changes", w.includes(Math.round(ftpNow * 0.85)), JSON.stringify(w));

await p.evaluate(() => { window.__refuseConnect = true; window.__device.gatt.disconnect(); tickLoop(); tickLoop(); });
check("dropped trainer records zero watts, not demo data", await p.evaluate(() => state.history.slice(-2).every((h) => h.p === 0)));
await p.evaluate(() => { window.__refuseConnect = false; });
await p.waitForTimeout(3500);
check("trainer reconnects automatically", await p.evaluate(() => !!state.ble.trainer));

await p.evaluate(() => { window.__refuseControl = true; sendControlOpcode(new Uint8Array([0x00])); });
await p.waitForTimeout(400);
check("warns when the trainer refuses control", (await p.$eval("#toast-msg", (e) => e.textContent)).includes("won't take commands"));

// TCX export
await p.evaluate(() => { for (let i = 0; i < 20; i++) tickLoop(); });
await p.click("#btn-engine-control"); // pause
const dl = p.waitForEvent("download", { timeout: 4000 });
await p.click("#btn-end");
const file = await (await dl).createReadStream();
let xml = "";
for await (const c of file) xml += c;
const doc = new DOMParser().parseFromString(xml, "application/xml");
const times = Array.from(doc.getElementsByTagName("Time")).map((n) => Date.parse(n.textContent));
check("TCX is well-formed with increasing timestamps", times.length > 20 && times.every((v, i) => i === 0 || v > times[i - 1]), `${times.length} points`);

check("no uncaught page errors", errors.length === 0, errors.join(" | "));
await browser.close();
if (failures) {
  console.log(`\n${failures} check(s) failed`);
  process.exit(1);
}
console.log("\nAll checks passed");
