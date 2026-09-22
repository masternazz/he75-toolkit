# Development

## Layout

```
app.py            tkinter app. Workers never touch Tk: they put ("busy"|"status", text) tuples and log text
                  on a queue that the main thread's pump() drains. stdout is redirected into the log box.
hall.py           key-settings logic: PRESETS, apply_preset, show. CLI wrapper at the bottom.
autogame.py       process watcher: watch(); DEVICE_LOCK serialises HID access (shared with the app).
light.ps1         standalone lighting CLI (PowerShell + hid.dll P/Invoke). Independent of the Python code.
winhid.py         hid.dll transport (WinHidIO), device-path discovery, open_keyboard().
scripts/          install-autostart.ps1
tests/            packet tests. No keyboard needed.
vendor/           epomaker-driver-linux (MIT) with the UTF-8 patch. See NOTICE.md.
docs/
```

Data flow: `app.py` / `autogame.py` / `hall.py` -> `winhid.open_keyboard()` -> vendored `HEKeyboard` -> `Transport` -> `WinHidIO` -> `hid.dll`.

## Tests

```powershell
python -m unittest discover -s tests -v
```

They check the lighting packet against a packet captured from the official app, and the checksum rules. They do not need a keyboard.

Everything that touches hardware is exercised by hand: `python hall.py show`, `powershell -File light.ps1 -Read`, and `python autogame.py --map notepad.exe=apex --once`.

## Add a preset

In `hall.py`:

```python
PRESETS["cs2"] = lambda a: [("wasd", 0.15, 0.1), (["lshift"], 0.5, None), (["lctrl"], 0.8, None)]
```

`(keys, actuation_mm, rapid_trigger_mm_or_None)`. `keys` is a list of key names or a string of letters. Then map a game to it in `autogame.GAMES`, and add the button to `GAME_BUTTONS` in `app.py`. Document the reasoning and sources in `docs/game-settings.md`.

## Add a lighting effect

Effects come from the vendored `codec.LIGHT_MODES` / `SIDE_MODES`. The app builds its dropdowns from them (minus effects this board rejects), so a new effect id in the vendor code appears automatically. Check `he_lighting.py` for per-effect speed/colour rules.

## Porting to another board

1. Confirm the device id with `identify` (`kb.identify()`); the vendored `models.json` lists ids and capabilities.
2. Set `winhid.open_keyboard(pid=...)` and the `MI_xx` interface for your device.
3. Check `docs/` in [epomaker-driver-linux](https://github.com/ramarivera/epomaker-driver-linux) for your model. Its README marks which models have hardware verification. **Read-only commands first** (`hall.show`, `light.ps1 -Read`), and read [protocol.md](protocol.md) before writing anything.

## Updating the vendored driver

Replace `vendor/epomaker_driver/` from a newer upstream commit, re-apply the UTF-8 patch (`sed -i 's/\.read_text()/.read_text(encoding="utf-8")/g' vendor/epomaker_driver/*.py`), update the commit hash in `NOTICE.md`, and re-run the tests and a `hall.py show`.

## Style

Small files, standard library only, no config files. Simplifications with a known ceiling are marked in comments.
