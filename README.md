# OpenWatt

A single-file ERG/SIM trainer cockpit that drives a smart trainer straight from the browser over Web Bluetooth. You don't need an account or a server, and no ride data leaves your machine. It's tuned for the Wahoo KICKR Bike and works with any FTMS-compatible trainer.

## Quick start

1. Open `index.html` in **desktop Chrome or Edge**, or on iPhone/iPad open the hosted page in the free [Bluefy](https://apps.apple.com/app/id1492822055) browser. Web Bluetooth isn't available in Safari, Chrome for iOS, or Firefox.
2. Pick a rider profile, which sets FTP and bias.
3. Load a workout from the built-in library, or drag and drop a `.zwo` / `.erg` / `.mrc` file. A `.zwo` exported from TrainingPeaks works.
4. Connect the trainer and, if you want, a heart-rate strap.
5. Choose **ERG** or **SIM** mode and hit start.
6. When you finish, export a `.tcx` and upload it to TrainingPeaks, Strava, or intervals.icu.

## On iPhone (Bluefy)

Bluefy needs the page served over HTTPS, so use the hosted copy rather than a local file.

- Phone layout: dial on top, interval/HR/cadence cards below, big touch controls at the bottom.
- The screen stays awake during a ride where the browser supports it. If it doesn't, the app tells you to set Auto-Lock to Never.
- Keep Bluefy in the foreground while riding. iOS pauses background pages, which would stop ERG updates.
- If the trainer drops, OpenWatt reconnects on its own and re-sends the current target.
- Rides are saved on the device as you go. **Profile › Last Ride › Export .TCX** opens the iOS share sheet (Files, AirDrop, Mail).
- Workouts: export a `.zwo` from TrainingPeaks to Files, then tap **Upload File**.

The app is one self-contained file: its CSS is compiled and inlined, so it works on a flaky connection once loaded. The only external request is the Space Grotesk web font, which falls back to the system font.

If Web Bluetooth isn't available, OpenWatt falls back to **demo mode** with a simulated rider. You can still try the whole cockpit without hardware.

## Features

- **ERG mode**: holds target watts through FTMS `Set Target Power`.
- **SIM mode**: sends grade through FTMS simulation parameters, and the KICKR Bike's shifters control resistance.
- **Built-in library**: nine workouts (recovery through VO₂max and sprints), defined in %FTP so they rescale to each rider.
- **Live cockpit**: radial power, cadence, and HR dials; a zone-colored workout profile with a playhead; a power-vs-target trace; and a rolling average.
- **Live section editing**: restart, ±30s, or skip the current block mid-ride (`←` `−` `+` `→`).
- **Bias control**: scales all targets from 50% to 150%, saved per rider.
- **Multiple rider profiles**: each has its own FTP and bias, stored in `localStorage`. Edit names and FTP under **Profile › Riders**.
- **KICKR Bike button inspector (experimental)**: shows live hex/binary bytes from Wahoo's proprietary characteristics. You can bind button bits to actions such as skip, bias ±, grade ±, and toggle mode.
- **TCX export**: per-second power (the mean of all trainer readings in that second), cadence, and HR, with TPX power extensions. The ride is checkpointed every 15 seconds and when the app goes to the background; after a crash or reload, OpenWatt offers to resume where you left off.
- **Workout memory**: the loaded workout (including an imported `.zwo`) survives a reload.
- **Demo guard**: starting without a trainer asks first, and connecting a trainer mid-demo discards the simulated data.
- **Trainer HR**: uses heart rate relayed by the trainer (a strap paired to the KICKR Bike) when no strap is connected directly.
- **Auto-reconnect**: trainer and HR strap reconnect with backoff after a Bluetooth drop.

## Bluetooth services

| Service | UUID |
|---|---|
| Fitness Machine (FTMS) | `0x1826` (Indoor Bike Data `0x2AD2`, Control Point `0x2AD9`) |
| Cycling Power | `0x1818` |
| Heart Rate | `0x180D` / `0x2A37` |
| Wahoo proprietary (buttons) | `a026ee01-…`, `a026ee0b-…`, `a026ee0d-…` |

## Repository layout

```
index.html              The app (everything in one file)
docs/spec.md            Full functional spec
tests/smoke.mjs         End-to-end checks against a simulated FTMS trainer
scripts/build-css.mjs   Rebuilds the inlined Tailwind CSS
scripts/                Older one-off patch scripts (already applied; kept for history)
```

## Development

```
npm install
npx playwright install chromium
npm test                 # runs tests/smoke.mjs
npm run build:css        # after adding or changing Tailwind classes
```

## Known limitations

- Web Bluetooth works in desktop Chrome or Edge, and in Bluefy on iOS. Not in Safari or Firefox.
- There's no automatic TrainingPeaks sync because their API is limited to partners. Use manual `.zwo` import and `.tcx` export instead.
- The KICKR Bike button mapping is reverse-engineered and may need tuning for your unit or firmware, using the inspector.
- Distance in the TCX export is estimated from power, not GPS.
- `.erg` ramps (two points with different watts) are imported as a step at the end value.
- Free-ride blocks in `.zwo` files hold 50% FTP in ERG rather than releasing resistance.

See [`docs/spec.md`](docs/spec.md) for full details.
