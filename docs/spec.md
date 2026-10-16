# OpenWatt — ERG/SIM Trainer Cockpit

A single-file, self-contained web app that drives a smart trainer (FTMS-compatible, tuned for the Wahoo KICKR Bike) directly from the browser via Web Bluetooth. No account, no server, no telemetry leaves the machine. Built as an open alternative to TrainerRoad-style ERG apps, with a manual export/import bridge to TrainingPeaks.

**File:** `index.html`, hosted at https://zouf.github.io/openwatt/. Open in desktop Chrome or Edge, or in Bluefy on iOS (Web Bluetooth required; Safari and Firefox unsupported).

---

## Core Loop

1. Pick a rider profile (sets FTP and bias).
2. Load a workout — built-in library or imported `.zwo` / `.erg` / `.mrc` file.
3. Connect the trainer (and optionally a heart-rate strap).
4. Choose ERG or SIM mode.
5. Start. The app drives the trainer, displays live telemetry, and records the ride.
6. End & export — produces a `.tcx` file for upload to TrainingPeaks, Strava, or intervals.icu.

---

## Workout Sources

### Built-in Library
Nine workouts defined in `%FTP`, so every target rescales automatically to the active rider's FTP:

| Workout | Tagline | Approx. duration |
|---|---|---|
| Z1 Recovery | Easy spin | 30 min |
| Z2 Endurance | Aerobic base | 60 min |
| Z2 Endurance · Long | 90 min base | 90 min |
| Tempo 3×10 | Z3 sustained | ~40 min |
| Sweet Spot 3×12 | 90% FTP | ~55 min |
| Threshold 2×20 | 97% FTP | ~80 min |
| Over/Unders 3×9 | 105% / 90% FTP | ~55 min |
| VO₂max 4×4 | 118% FTP | ~50 min |
| Sprints 6×30s | Neuromuscular | ~40 min |

The Library menu shows each workout's duration, Intensity Factor (IF), Training Stress Score (TSS), and the actual watt range at the current rider's FTP.

### File Import
Supports `.zwo` (Zwift workout XML — warmup/ramp/cooldown, steady state, interval repeats, free ride), `.erg` (absolute watts course data), and `.mrc` (%FTP course data). Drag-and-drop or file picker.

### TrainingPeaks Bridge
No automatic sync — TrainingPeaks' API is partner-gated and not available to individual accounts. The supported path is manual export/import:
- Export structured workouts from TrainingPeaks as `.zwo`, `.erg`, `.mrc`, or `.fit` (per-workout via Files menu, or bulk via Settings → Export).
- Load into OpenWatt.
- Completed rides export back out as `.tcx` for re-upload to TrainingPeaks/Strava/intervals.icu.

A future iteration could add cookie-based auto-pull of the TP calendar via an unofficial/reverse-engineered endpoint, but this sits in a ToS gray area and isn't included by default.

---

## Modes

### ERG Mode
Sends FTMS `Set Target Power` (opcode `0x05`) for the current workout block. The trainer holds that wattage regardless of cadence or gear. Re-asserted every 3 seconds, throttled on change.

### SIM Mode
Sends FTMS `Set Indoor Bike Simulation Parameters` (opcode `0x11`) with a grade value instead of a fixed target. Because the KICKR Bike performs virtual shifting internally, **the physical shifters control resistance** in this mode, just like riding outdoors.

- Toggle between ERG and SIM via the mode switch or the `m` hotkey.
- Grade is adjustable via slider or ±0.5% step buttons (range −10% to +20%).
- In SIM, the "Target" readout becomes a guide value rather than a hard target.

---

## Live Cockpit

- **Power, Target, Cadence, Heart Rate** — large readouts with zone-colored indicators (Z1–Z7, standard %FTP zone model).
- **Profile chart** — the full workout rendered as a zone-colored power profile, with a live playhead.
- **Power-vs-target trace** — rolling 3-minute chart of actual vs. target power.
- **Time readouts** — elapsed, time remaining in current section, time remaining in workout.
- **Bias control** — scales every target up or down on the fly (50%–150%), e.g. for a bad day or a strong one. Persisted per rider profile.

---

## Live Section Editing

The current workout block can be adjusted mid-ride without stopping:

| Action | Control | Hotkey |
|---|---|---|
| Restart current section | Button | `←` |
| Shorten section by 30s | Button | `−` |
| Lengthen section by 30s | Button | `+` |
| Skip to next section | Button | `→` |

The profile chart and remaining-time readouts update immediately. Useful for trimming a cooldown, extending recovery between intervals, or bailing early on a block.

---

## Rider Profiles

- Multiple profiles supported (e.g. one per household member), shown as chips in the header.
- Each profile stores its own **FTP** and **bias**, persisted locally via `localStorage`.
- Click a chip to switch active rider (instantly rescales the loaded workout); `+` adds a profile (prompts for name and FTP); `✕` removes one (minimum of one profile retained).

---

## Trainer Hardware Integration

### Connection
- **Trainer**: Web Bluetooth pairing via the standard FTMS service (`0x1826`). Reads Indoor Bike Data (power, cadence) via notifications on `0x2AD2`; writes targets via the Fitness Machine Control Point (`0x2AD9`), after requesting control (`0x00`) and sending start/resume (`0x07`).
- **Heart rate**: separate Web Bluetooth pairing via the standard Heart Rate service (`0x180D` / `0x2A37`).

### KICKR Bike Buttons (Experimental)
The KICKR Bike reports gear/button state over an **undocumented, reverse-engineered Wahoo proprietary characteristic** (`a026e039-0a7d-4ab3-97fa-f1500f9feb8b`, alongside the trainer-control characteristic `a026e005-...`). Because the byte layout isn't publicly specified, OpenWatt provides a live inspector rather than a hardcoded assumption:

- After connecting the trainer, the inspector subscribes to the channel.
- Raw incoming bytes are displayed live in both hex and binary formats as you press buttons on the bike.
- An **event log** tracks and displays exact bit flips (e.g. "Byte 3, Bit 1 went HIGH") when you press a button.
- You can add custom **Bit Bindings**, mapping any specific byte/bit combination's "pressed" (HIGH) state to an action:
  - Skip section
  - Restart section
  - +30s / −30s on current section
  - Bias +2% / −2%
  - Grade +0.5% / −0.5%
  - Toggle ERG/SIM
  - Start/pause
  - None
- A "buttons control the workout" checkbox disables/enables binding execution without disconnecting.

**Caveat**: SIM mode already uses the shifters for resistance via the bike's internal virtual shifting. Bindings are most useful in ERG mode, where the shifters otherwise have no effect.

---

## Demo Mode

If Web Bluetooth is unavailable (e.g. inside a sandboxed preview, or on Safari/Firefox), OpenWatt automatically falls back to a simulated rider: power eases toward target with realistic noise, cadence and heart rate respond plausibly to intensity. This allows the full cockpit — library, profiles, section editing, mode switching, and `.tcx` export — to be exercised without hardware.

---

## Export Format

Completed rides export as `.tcx` (Garmin TrainingCenterDatabase v2):
- One lap per ride, with per-second trackpoints (time, distance estimate, cadence, heart rate if available, power via the `ns3:TPX` extension).
- Lap-level average and max watts via the `ns3:LX` extension.
- Filename: `openwatt-<timestamp>.tcx`.
- Compatible with TrainingPeaks, Strava, and intervals.icu manual upload.

---

## Known Limitations

- Web Bluetooth requires desktop Chrome or Edge; not supported in Safari, Firefox, or most sandboxed iframes (falls back to demo mode).
- No automatic TrainingPeaks sync (see TrainingPeaks Bridge above).
- KICKR Bike button mapping is reverse-engineered and may require per-unit/firmware tuning via the live inspector.
- Distance in the `.tcx` export is a cosmetic power-based estimate, not GPS-derived.
