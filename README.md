# HE75 Toolkit

Control an **EPOMAKER HE75 V2** hall-effect keyboard from Windows **without the official driver app**: per-key actuation and Rapid Trigger, lighting for the keys and the top light bar, and automatic per-game profiles that switch when a game starts.

- **A small desktop app** (`app.py`): game presets, lighting, auto-switch toggle, live log.
- **Command-line tools** for everything the app does, so it is scriptable.
- **Per-game presets** for Apex Legends, Marvel Rivals and Valorant, built from published guidance (sources in [docs/game-settings.md](docs/game-settings.md)).
- **Every write is verified** by reading it back from the keyboard, and a backup of the profile is saved first.
- **Zero pip installs.** Standard-library Python plus the Windows `hid.dll`.

> **Status:** works on my HE75 V2 (internal model 3518, USB `3151:5054`, firmware `0x0504`). It is untested on any other board. It writes to the keyboard's onboard memory, so read [Safety](#safety) before using it.
>
> This is an independent project. It is not affiliated with or endorsed by EPOMAKER.

## Requirements

- Windows 10/11
- Python 3.10+ with tkinter (the standard python.org installer includes it)
- The keyboard connected **by USB cable** (wired mode)
- The **EPOMAKER driver app closed**. It holds the device open, and only one program should talk to the keyboard at a time.

## Quick start

```powershell
git clone https://github.com/masternazz/he75-toolkit
cd he75-toolkit
python app.py
```

The window shows *"EPOMAKER HE75 V2 connected"* when it finds the board. Use `pythonw app.py` to run without a console window.

### The app

| Section | What it does |
|---|---|
| **Hall-effect presets** | One click applies Apex / Rivals / Valorant / Generic FPS settings to the *active* onboard profile, or resets every key to stock. Takes about two minutes (each key is written, then verified). |
| **Lighting** | Effect, colour, brightness and speed for the keys and, separately, the light bar. One-click looks: *Cyberpunk* (hot pink keys, cyan bar) and *Dark purple*. |
| **Per-game auto-switch** | Watches for a game's process. When it starts, applies that game's preset; when it closes, restores your idle setup (`reset` = stock keys, or `gaming`). |

### Command line

```powershell
python hall.py show                    # keys that differ from stock
python hall.py apex                    # or: rivals | valorant | gaming | reset
python hall.py gaming --move 0.1 --rt 0.05

powershell -File light.ps1 -Mode ripple -Color FF0090 -Brightness 4 -Speed 3
powershell -File light.ps1 -Side -Mode wave -Color 00F0FF -Speed 2
powershell -File light.ps1 -Read       # what the board has stored (add -Side for the bar)

python autogame.py                     # watch for games until Ctrl+C
powershell -File scripts\install-autostart.ps1    # run the watcher at every logon
```

Lighting modes: keys `wave ripple raindrop snake reactive convergence sine kaleidoscope line-wave laser circle-wave dazzling rain meteor solid breathing neon`; light bar `off solid neon wave`. Neon's colours are fixed by the firmware, so it ignores `-Color`.

## Presets at a glance

| | Movement keys | Jump / crouch | Abilities |
|---|---|---|---|
| **Apex Legends** | A/D 0.2 mm, W/S 0.4 mm, Rapid Trigger 0.1 mm | Space 0.2, Shift 0.3, Ctrl/C 0.4 | 2.0 mm, no Rapid Trigger |
| **Marvel Rivals** | WASD 1.0 mm, Rapid Trigger 0.2 mm | Space/Ctrl/Shift 2.0 | stock |
| **Valorant** | WASD 0.3 mm, Rapid Trigger 0.2 mm | Shift 0.5, Ctrl 0.8, Space 2.0 | 1.2 mm, ult 1.8 |

Reasoning and sources: [docs/game-settings.md](docs/game-settings.md). These are starting points, not gospel. Tune by feel, and if a key double-types, raise the Rapid Trigger step.

## Safety

- **It writes to the keyboard's onboard flash.** The commands are the same ones the official app sends (captured from it, and matching an independent open-source implementation), and every write is read back and compared. Still: use at your own risk.
- **Backups.** Before any change, the profile's current magnetic settings are saved to `backups/`. `python hall.py reset` returns every key to stock (2.0 mm, Rapid Trigger off).
- **Profiles.** The board has two onboard profiles. Presets apply to whichever is active; the other is untouched.
- **Anti-cheat.** The tool only talks to the keyboard over USB HID (the same way the vendor app does) and reads the process list. It does not touch any game. Even so, if you are worried about a particular anti-cheat, apply presets before launching the game rather than during it, or do not use auto-switch for that game.
- **Tournament rules.** Rapid Trigger is currently allowed in Valorant. SOCD/Snap Tap is banned in CS2. This tool does not enable SOCD.

## How it works (short version)

The keyboard exposes a vendor HID interface. Commands are 64-byte feature reports with an 8-bit checksum. The command set is the *RY5088* family protocol; the codec is a vendored copy of [ramarivera/epomaker-driver-linux](https://github.com/ramarivera/epomaker-driver-linux) (Linux/hidraw only), and `winhid.py` adds a Windows `hid.dll` transport underneath it. Details, packet layouts and the Windows quirks I hit are in [docs/protocol.md](docs/protocol.md).

## Docs

| | |
|---|---|
| [docs/game-settings.md](docs/game-settings.md) | Per-game settings, the reasoning, and the sources |
| [docs/autogame.md](docs/autogame.md) | Per-game auto-switch: how it works, adding games, run at logon |
| [docs/protocol.md](docs/protocol.md) | The HID protocol, packet formats, checksums, Windows quirks |
| [docs/troubleshooting.md](docs/troubleshooting.md) | "Not found", "cannot open", double-typing, and more |
| [docs/development.md](docs/development.md) | Layout, tests, how to add a preset or port to another board |

## Project layout

```
app.py            desktop app (tkinter)
hall.py           per-key actuation / Rapid Trigger CLI + presets
light.ps1         lighting CLI (PowerShell + hid.dll, no Python needed)
autogame.py       per-game watcher
winhid.py         Windows hid.dll transport for the vendored driver
scripts/          install-autostart.ps1
tests/            packet tests (no keyboard needed)
vendor/           epomaker-driver-linux (MIT), lightly patched, see NOTICE.md
docs/
```

## Credits and license

MIT, see [LICENSE](LICENSE). The protocol implementation is the work of Ramiro Rivera's [epomaker-driver-linux](https://github.com/ramarivera/epomaker-driver-linux) (MIT), vendored under `vendor/`. See [NOTICE.md](NOTICE.md). "EPOMAKER" is a trademark of its owner and is used here only to say which hardware this works with.
