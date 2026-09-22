# Troubleshooting

## "keyboard not found (USB cable in?)"

The tool looks for the HID interface `VID_3151 & PID_5054 & MI_02`. Check:

- The board is plugged in **by USB cable** and its mode switch is on wired (not Bluetooth / 2.4 GHz).
- `Get-PnpDevice -PresentOnly | Where-Object InstanceId -like 'HID\VID_3151*'` lists devices. If yours has a different `PID`, it is a different model: the codec may not apply and **you should not write to it**. Open an issue with the output.

## "cannot open ... (close the EPOMAKER driver app)"

The official app (and its helpers) has the device open. Close it and end leftovers:

```powershell
Get-Process 'EPOMAKER Driver v4','iot_manager_rs','common_hid_rs','system_info_hid_rs','rhythm_service','screen_capture_service','keyboard_monitor_service' -ErrorAction SilentlyContinue | Stop-Process -Force
```

## "magnetic readback differs; state may be partial"

Usually a stale reply on Windows rather than a bad write (see [protocol.md](protocol.md#windows-quirks)). `hall.py` already re-checks from a fresh read and retries up to 4 times. If it still fails, run `python hall.py show` to see what is actually on the board, then re-run the preset; already-correct keys are skipped.

## "rapid-trigger settings require fire enabled"

You tried to set a Rapid Trigger step on a key whose Rapid Trigger is off. Set them together (`fire=True`); `hall.py` presets do.

## A key double-types, or a held key seems to release

The Rapid Trigger step is too small; finger tremor crosses it. Use 0.1 mm or more (0.2-0.3 mm if it persists). You can also raise actuation slightly, or recalibrate (Travel Calibration in the official app).

## The colour looks washed out or pinkish

LEDs mix colour additively and hide low values. For a deep purple keep green at 0 and blue about twice red (`4B0082`), and control depth with brightness rather than dimmer colour values. The `light.ps1` `-Brightness` and `-Speed` options range 0-4.

## The light bar is rainbow, not my colour

`neon` on the bar has fixed firmware colours and ignores the colour you pass. Use `solid` or `wave` for a chosen colour.

## The app window is blank / a button does nothing

Long actions (presets take ~2 minutes) disable the buttons and show a yellow "Applying ..." line. Progress prints into the log. Errors appear in the log prefixed `ERROR:`.

## A screenshot or debugging via the official app hangs

Unrelated to the toolkit, but if you script the official Electron app: `ELECTRON_RUN_AS_NODE=1` in the environment (VS Code sets it) makes `Electron.exe` behave as plain Node and exit immediately with "bad option". Unset it before launching.

## Undo everything

```powershell
python hall.py reset        # all keys: 2.0 mm, Rapid Trigger off
```

Backups of each profile's previous settings are in `backups/*.json` (one per write).
