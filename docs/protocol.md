# The HE75 V2 HID protocol

What this toolkit sends to the keyboard, how it was worked out, and the Windows-specific quirks. All of it is for the **EPOMAKER HE75 V2** (device id `3518`, USB `3151:5054`, firmware `0x0504`). Other RY5088-family boards share most of it, but nothing here is verified on them.

## Provenance

1. The official **EPOMAKER Driver v4** (3.2.22) is an Electron app. Its renderer sends commands through a small local gRPC-web helper. I hooked `fetch` in the running renderer and logged what it sent while changing the lighting effect. That gave real packets, e.g. Ripple / purple.
2. [ramarivera/epomaker-driver-linux](https://github.com/ramarivera/epomaker-driver-linux) documents the same command set (`docs/he75-v2.md`, `docs/magnetic-protocol.md`, `codec.py`). Its packet layout matched the capture byte for byte, and it supplied the effect ids and the magnetic-key fields.
3. Everything below marked **(verified)** was checked against the real board by writing a value and reading it back.

You do not need the official app to use the toolkit. This is just the paper trail.

## Transport

- The keyboard enumerates several HID interfaces. Commands go to the **vendor-defined interface `MI_02`** (`HID\VID_3151&PID_5054&MI_02\...`). **(verified)**
- A command is a **feature report, report id 0, 64 bytes**. Windows wants the id prefixed, so the buffer is 65 bytes: `00` + 64 bytes. Sent with `HidD_SetFeature`; replies are read with `HidD_GetFeature`. **(verified)**
- The device path is built from the PnP instance id: replace `\` with `#`, prefix `\\?\`, append `#{4d1e55b2-f16f-11cf-88cb-001111000030}` (the HID class GUID).

### Checksum

Byte `k` of the 64-byte command holds `0xFF - (sum(bytes[0..k-1]) & 0xFF)`.

| Command kind | `k` |
|---|---|
| Lighting writes (`0x07`, `0x08`) | 8 |
| Queries (`0x87`, `0x88`, `0x84`, `0x8F`) | 7 |
| Magnetic reads/writes | 7 |

A query with the checksum in the wrong place is not rejected loudly: `GetFeature` just hands your own request back. **(verified: cost me an hour)**

## Identity and profile

| Command | Reply |
|---|---|
| `8F` | `8F`, device id (u32 LE at 1), USB version (u16 LE at 7), boot flag at 9. Id `3518` = HE75 V2. |
| `84` | `84`, active onboard profile index at byte 1 (0-based; the app calls index 1 "Profile 2"). |

## Lighting

### Keys: write `07`, read `87`

```
 0    1     2          3           4      5  6  7   8         9..63
07  mode  4-speed  brightness  flags    R  G  B  checksum   00...
```

- `speed` is stored inverted (`4 - speed`), range 0-4. Modes with no speed (`solid`) use 0.
- `brightness` 0-4.
- `flags` = `(option << 4) | color_mode`. `color_mode` **7 = use the RGB bytes**, **8 = rainbow ("dazzling")**. `option` is a per-effect variant, 0 for the effects used here.
- Pure white `FFFFFF` is sent as `FA FF FA`. (Firmware quirk carried over from the vendor codec.)
- **Captured example** (Ripple, `#8A2BE2`, speed 4, brightness 4): `07 05 00 04 07 8A 2B E2 51`, and `0xFF - (07+05+00+04+07+8A+2B+E2 & FF) = 0x51`. This packet is a unit test.
- Reply to `87` has the same layout with byte 0 = `87`. Compare bytes 2-8 to verify a write (byte 1 differs: `07` vs `87`).

Effect ids (keys): `off 0, solid 1, breathing 2, neon 3, wave 4, ripple 5, raindrop 6, snake 7, reactive 8, convergence 9, sine 10, kaleidoscope 11, line-wave 12, picture 13, laser 14, circle-wave 15, dazzling 16, rain 17, meteor 18, reactive-off 19, screen 21, music 22`. `off` is not supported on the HE75 V2's key lighting; `neon`, `picture`, `screen` take no colour.

### Light bar ("side light"): write `08`, read `88`

Same layout with three differences: byte 0 is `08`, **speed is not inverted**, and the effect ids are `off 0, solid 1, breathing 2, neon 3, wave 4, snake 5`. On the HE75 V2 the bar supports `off / solid / neon / wave`. `off` requires brightness 4; `solid` and `off` require speed 0; `neon` uses flags `08` and ignores colour (it cycles rainbow). **(verified)**

## Hall-effect key settings (magnetic)

Per-key parameters live in **128 slots per profile**. A slot number is the key's position in the profile's 128 x 4-byte keymap matrix (`read_matrix`); decode the 4 bytes to find which key a slot is. On the profile I used: `LShift 4, LCtrl 5, A 9, W 14, S 15, D 21, C 28, Space 41`. **Do not hardcode slots**, since they depend on the layout; `hall.py` looks them up by key name.

Fields (bulk-read with `E5 field 01 page`, written with `65 field 00 key-index commit ...`):

| Field | Meaning | Encoding |
|---|---|---|
| 0 | Actuation (travel) | u16 LE |
| 1 | Release (lift) travel | u16 LE |
| 2 / 3 | Rapid Trigger press / release step | u16 LE |
| 4 | Dynamic travel | u16 LE |
| 6 | Bottom dead zone | u16 LE |
| 7 | Mode byte; **high bit = Rapid Trigger enabled** | u8 |
| 9 | Snap (SOCD) pairing | u8 |
| 251 | Top dead zone | u8 (firmware >= 0x0400) |
| 252 | Switch / axis type | u8 |

**Units:** value / multiplier = mm. The multiplier depends on firmware: `10` below `0x0300`, `100` up to `0x04FF`, **`200` from `0x0500`** (this board, `0x0504`): stock `0x0190` = 400 -> 2.00 mm. **(verified)** Values are truncated, not rounded, so the smallest step is 0.005 mm.

Write order matters (mode field first, then changed fields, only the last command carries the commit flag); the vendored planner handles it, and the toolkit reads every touched field back to confirm.

Rapid Trigger step values are only accepted for a key whose Rapid Trigger is on. The planner raises `rapid-trigger settings require fire enabled` otherwise. This is why "reset to stock" writes only travel/lift/off.

## Windows quirks

1. **Echo instead of an answer.** `HidD_GetFeature` right after `HidD_SetFeature` can return the previous buffer (your own request, or the previous page's reply) before the board has answered. `winhid.py` waits 30 ms first, then retries while the reply equals the request. A few queries never get a distinct reply (the wireless-dongle version query with no dongle attached); after 15 tries the echo is returned as the answer, which is what the driver code expects.
2. **cp1252.** The vendored driver reads its JSON data files with the platform default encoding. On Windows that crashes on a UTF-8 file. Patched (see `NOTICE.md`).
3. **`fcntl`.** The vendored `transport.py` imports it at module load even on the USB path. A stub module is registered before import.
4. **Exclusive-ish access.** The official app keeps the device open. Two programs writing at once can interleave a multi-page transaction, so close it.

## Further reading

- Upstream: `docs/he75-v2.md`, `docs/magnetic-protocol.md`, `docs/glyph-protocol.md` in [epomaker-driver-linux](https://github.com/ramarivera/epomaker-driver-linux).
- The official web configurator, `hub.epomaker.com`, exposes the same features in a browser (WebHID).
