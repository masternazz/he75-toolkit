# Per-game auto-switch

The keyboard has only two onboard profiles and no way to detect games itself, so switching is done from your PC. The desktop app has saved named profiles; its watcher chooses one based on the foreground window and running processes.

## Desktop app profiles

On first launch the app creates a local profile library at `%LOCALAPPDATA%\HE75 Toolkit\profiles.json`:

- **Desktop** is the work/lounge fallback (stock Hall settings with dim purple lighting).
- **Apex Legends**, **Marvel Rivals**, **Valorant**, and **Generic FPS** are starting profiles with Hall settings and the Cyberpunk lighting look.

Use **+ Add profile** to make another game profile. On its card, choose **+ App** to link a process from the currently running-app list or browse to a game `.exe`. Executable matching is case-insensitive and saves only the filename, so moving a game installation does not break it.

The app resolves profiles as follows:

1. A linked game in the foreground wins when more than one linked game is running.
2. If you alt-tab to an unlinked app such as Discord or a browser, the last linked game stays active while it remains running.
3. Desktop applies only when no linked game process is still running.

Profile application is serialized so only one keyboard write happens at a time. Hall and lighting writes are read back and must verify before the app reports success.

## Legacy command-line watcher

## How it works

1. Every 5 seconds `autogame.py` lists running processes (`tasklist`, no hooks, no injection).
2. If a known game's executable is running, it applies that game's preset (`hall.apply_preset`).
3. When the game exits, it applies the **idle** preset. Default `reset` = every key back to stock (2.0 mm, no Rapid Trigger), so typing feels normal. `--idle gaming` restores the generic FPS setup instead.
4. If applying fails (driver app open, cable unplugged), it logs the error and retries on the next tick.

It starts by assuming the board is already in the idle state, so launching it does not rewrite anything.

Each apply resets the keys the previous preset touched, then writes the new preset, verifying every key by readback. That is about **two minutes**, so it happens while the game is loading. If you alt-tab in very early, the old settings may still be active.

## Watched games

| Game | Process name (verified on a real install) | Preset |
|---|---|---|
| Apex Legends | `r5apex_dx12.exe` (also `r5apex.exe`) | `apex` |
| Marvel Rivals | `Marvel-Win64-Shipping.exe` | `rivals` |
| Valorant | `VALORANT-Win64-Shipping.exe` | `valorant` |

Add or change games without editing code:

```powershell
python autogame.py --map eldenring.exe=gaming --map cs2.exe=gaming
```

or edit the `GAMES` dict at the top of `autogame.py`. Find a game's process name in Task Manager -> Details while it runs.

## Try it without a game

```powershell
notepad
python autogame.py --idle gaming --map notepad.exe=valorant --once
```

Notepad stands in for the game: the Valorant preset is applied, and when you close Notepad the idle preset is restored and the script exits (`--once`).

## Run it at every logon

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install-autostart.ps1              # idle = reset
powershell -ExecutionPolicy Bypass -File scripts\install-autostart.ps1 -Idle gaming
powershell -ExecutionPolicy Bypass -File scripts\install-autostart.ps1 -Remove
```

This registers a per-user scheduled task ("HE75 Toolkit Auto-Switch") that runs `pythonw autogame.py` with no window at logon. No admin rights needed. Check it with `Get-ScheduledTask "HE75 Toolkit Auto-Switch"`.

Logs from a windowless run are not kept. To debug, run `python autogame.py` in a terminal.

## The app's toggle

The app's **Per-game auto-switch** checkbox uses its saved profile library and shows activity in the log. The command-line watcher remains useful for scripts and scheduled tasks. Use one or the other, not both: two watchers would fight over the device.

## Limitations

- Presets apply to the **active** onboard profile. Switching onboard profiles yourself changes which one that is.
- The official EPOMAKER driver app must stay closed.
- Anti-cheat: the watcher reads the process list and talks to the keyboard over USB HID, like the vendor app. It does not touch any game. If you are cautious about a specific anti-cheat, apply the preset before launching the game, or skip auto-switch for that game.
- Wired only. Bluetooth and the 2.4 GHz dongle use a different path this toolkit does not implement.
