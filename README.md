# OpenWatt

A single-file ERG/SIM trainer cockpit that drives a smart trainer straight from the browser over Web Bluetooth. You don't need an account or a server, and no ride data leaves your machine. It's tuned for the Wahoo KICKR Bike and works with any FTMS-compatible trainer.

## Quick start

1. Open `openwatt.html` in **desktop Chrome or Edge**. Web Bluetooth isn't available in Safari or Firefox.
2. Pick a rider profile, which sets FTP and bias.
3. Load a workout from the built-in library, or drag and drop a `.zwo` / `.erg` / `.mrc` file. A `.zwo` exported from TrainingPeaks works.
4. Connect the trainer and, if you want, a heart-rate strap.
5. Choose **ERG** or **SIM** mode and hit start.
6. When you finish, export a `.tcx` and upload it to TrainingPeaks, Strava, or intervals.icu.

There's no build step. The page loads Tailwind from its CDN, so the first load needs an internet connection.

If Web Bluetooth isn't available, OpenWatt falls back to **demo mode** with a simulated rider. You can still try the whole cockpit without hardware.

## Features

- **ERG mode**: holds target watts through FTMS `Set Target Power`.
- **SIM mode**: sends grade through FTMS simulation parameters, and the KICKR Bike's shifters control resistance.
- **Built-in library**: nine workouts (recovery through VO₂max and sprints), defined in %FTP so they rescale to each rider.
- **Live cockpit**: radial power, cadence, and HR dials; a zone-colored workout profile with a playhead; a power-vs-target trace; and a rolling average.
- **Live section editing**: restart, ±30s, or skip the current block mid-ride (`←` `−` `+` `→`).
- **Bias control**: scales all targets from 50% to 150%, saved per rider.
- **Multiple rider profiles**: each has its own FTP and bias, stored in `localStorage`.
- **KICKR Bike button inspector (experimental)**: shows live hex/binary bytes from Wahoo's proprietary characteristics. You can bind button bits to actions such as skip, bias ±, grade ±, and toggle mode.
- **TCX export**: per-second power, cadence, and HR, with TPX power extensions.

## Bluetooth services

| Service | UUID |
|---|---|
| Fitness Machine (FTMS) | `0x1826` (Indoor Bike Data `0x2AD2`, Control Point `0x2AD9`) |
| Cycling Power | `0x1818` |
| Heart Rate | `0x180D` / `0x2A37` |
| Wahoo proprietary (buttons) | `a026ee01-…`, `a026ee0b-…`, `a026ee0d-…` |

## Repository layout

```
openwatt.html   The app (everything in one file)
docs/spec.md    Full functional spec
scripts/        One-off patch scripts used during development (already applied; kept for history)
```

## Known limitations

- Web Bluetooth only works in desktop Chrome or Edge.
- There's no automatic TrainingPeaks sync because their API is limited to partners. Use manual `.zwo` import and `.tcx` export instead.
- The KICKR Bike button mapping is reverse-engineered and may need tuning for your unit or firmware, using the inspector.
- Distance in the TCX export is estimated from power, not GPS.

See [`docs/spec.md`](docs/spec.md) for full details.
