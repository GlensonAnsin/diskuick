# Diskuick

Keeps your game drive "awake" so it doesn't stall when a game suddenly asks for data.

## The problem it targets

Some SSDs - especially budget, DRAM-less SATA models - drop into a low-power / idle state and are
slow to respond to the first reads after sitting idle. In a game this shows up as hitches while
assets stream in. Running a disk scanner (e.g. HD Tune's error scan) in the background makes the
stutter disappear because it keeps the drive continuously busy.

Diskuick does the same thing, but **gently and only when needed**: a tiny, steady, read-only load on
the drive while your game is running.

> **Honest caveat:** this is a workaround, not a cure, and it only helps if idle wake-up is your
> actual problem. That's what the built-in **Benchmark & auto-tune** and **Lag check** are for - they
> measure your own drive instead of asking you to take this on faith. If your drive is nearly full,
> failing, overheating, or the bottleneck is your CPU/RAM/GPU, Diskuick won't fix it (the app will
> tell you when it spots those).

## Features

- **Tray app + dashboard** with live read-latency graph, stall log and session stats
- **Auto-detect games** from Steam, Epic Games and GOG; add others by picking a running program
- **Per-game profiles** (drive + intensity) and **multi-drive** support
- Starts/stops automatically with your game; optional **pause on battery** and **only while focused**
- **Benchmark & auto-tune**: finds the lightest setting that actually helps *your* drive
- **Lag check**: 30 s of real disk / CPU / RAM sampling while you play, with plain-language findings
- **Drive health** (model, health, free space, temperature/wear when Windows exposes them) and tips
- Optional **latency overlay** (off by default): a small click-through readout in a screen corner
- Tray notifications, dark/light/system theme, English + Filipino, start with Windows

## How it works / safety

- Reads a small random-data **probe file** (`<drive>:\.diskuick\probe.bin`, 256 MB, written once) with
  unbuffered I/O so reads really hit the disk. Reads cause no flash wear.
- It never touches your game files and never injects into or inspects game processes (it only looks at
  the list of running program *names*), so it doesn't interact with anti-cheat. The optional overlay is
  a separate click-through window - not a hook - so it only shows over windowed/borderless games, not
  exclusive fullscreen.
- **Privacy:** the only network access is the update check (`api.github.com` for the repo in
  `version.py`; switch it off in Settings). Nothing about you or your PC is sent.
- **Updates:** a newer GitHub release shows an "Update now" banner. It only installs after you click it,
  only from GitHub's own HTTPS hosts, and only if the download matches the release's SHA-256 checksum.

## Use it

1. Run `Diskuick.exe` (single file, no install needed). First launch opens the **Games** tab.
2. Click **Detect installed games** and tick your games. Or use **Add running program…**.
3. (Optional) **Tools → Run auto-tune** to pick the best intensity for your drive.
4. Close the window - Diskuick keeps working from the system tray.

Settings apply instantly. Data lives in `%APPDATA%\diskuick\` (config, stats, `stalls.log`).
Temperature/wear need Administrator rights on most PCs; run as admin if you want them.

### Command line

```
python diskuick.py bench D      # idle-latency test with/without keep-alive
python diskuick.py run D --process game.exe
python diskuick.py clean D      # delete the probe file
```

## Publishing a release (so users get updates)

1. Bump `VERSION` in `version.py`, then run `.\build.ps1`.
2. Create a GitHub release tagged `v<version>` (e.g. `v1.2.0`) and attach **all** of
   `dist\Diskuick-Setup-<version>.exe`, `dist\Diskuick-Setup-<version>.exe.sha256` and
   `dist\Diskuick-portable-<version>.zip`. For example:
   `gh release create v1.2.0 dist\Diskuick-Setup-1.2.0.exe dist\Diskuick-Setup-1.2.0.exe.sha256 dist\Diskuick-portable-1.2.0.zip --title "Diskuick 1.2.0"`
3. Installed copies offer "Update now"; the portable exe offers "Download" (opens the release page).

## Build from source

```
.\build.ps1            # runs tests, builds dist\Diskuick.exe + portable zip (+ installer if Inno Setup is installed)
.\build.ps1 -SkipTests
```

Requires Python 3.12+. Dependencies: `requirements.txt`. Tests: `python -m unittest discover -s tests`.

| File | Purpose |
|---|---|
| `diskuick.py` | Engine: unbuffered reads, keep-alive thread, benchmark, CLI |
| `controller.py` | Decides which drives to keep awake (games, drives, battery, focus) |
| `games.py` | Steam / Epic / GOG game detection |
| `health.py`, `lagcheck.py` | Drive health + "why am I lagging" analysis |
| `app_ui.py`, `widgets.py`, `overlay.py` | The window (CustomTkinter) and the optional overlay |
| `diskuick_tray.py` | Entry point: tray icon, config, autostart |
| `logo.py`, `make_icon.py` | The one logo, used for exe/tray/window icons |
| `installer.iss` | Inno Setup script (builds `Diskuick-Setup-<version>.exe`) |

## Not done / needs you

- **Code signing:** unsigned exes trigger Windows SmartScreen warnings. A code-signing certificate
  costs money; `build.ps1` will sign automatically if you set `DISKUICK_SIGN_PFX` / `DISKUICK_SIGN_PASSWORD`
  (untested - no certificate was available).
- **Filipino translation** is best-effort; please have a native speaker review `i18n_fil.py`.
- **GPU** and network aren't measured by the lag check. Game exe detection is a best guess.
