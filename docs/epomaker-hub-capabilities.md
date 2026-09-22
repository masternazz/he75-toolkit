# EPOMAKER Hub / HE75 V2 capability check

Checked 2026-09-21 against EPOMAKER's current first-party pages and the JavaScript served by `hub.epomaker.com`. This is a design reference for the Toolkit; it does **not** change the keyboard.

## What EPOMAKER explicitly confirms for the base HE75 V2

- The **EPOMAKER Hub** can configure the HE75 V2 in a browser: key remapping, macros, and lighting. The manual describes it as web-based/no-download. [HE75 V2 manual](https://epomaker.com/blogs/manuals/epomaker-he75-v2-manual)
- EPOMAKER also lists the HE75 V2 in **Driver 3.0** (Windows/macOS) and states that Hub needs desktop Chrome or Edge; Firefox and Safari cannot connect. [Driver 3.0 download page](https://epomaker.com/blogs/software/epomaker-driver-3-0)
- The product page documents adjustable Hall-effect actuation from **0.1 to 3.5 mm** in 0.005 mm increments, per-key RGB/front-light controls, and wired/2.4 GHz/BT polling characteristics. [HE75 V2 product page](https://epomaker.com/products/epomaker-he75-v2)

That is the safe feature baseline for the Toolkit: settings pages for key mapping, macros, lighting, and per-key actuation.

## Advanced keys: supported by Hub's architecture, not yet confirmed per HE75 V2

Hub has an `Advanced Keys` area. Its current official client code contains handlers for:

- **RS** (Rapid Trigger)
- **SOCD** / opposite-direction handling
- **SNAP** (SnapKey pair)
- **DKS** (four actions over press/release travel positions)
- **MT** (tap action and held action with a configurable hold time)
- **TGL** (toggle action; optional long press where the device advertises it)
- **CB** / combo (modifiers plus a normal key)

The same code makes the menu and individual controls conditional on the connected model's device configuration. In other words, the Hub code proves the UI/protocol family has these concepts, but it is not proof that every one is enabled in base HE75 V2 firmware. [Hub](https://hub.epomaker.com/) · [Advanced Keys implementation](https://hub.epomaker.com/assets/AdvancedKeyView-JF2R0izZ.js)

EPOMAKER's generic Hall-effect guide explains DKS, Mod-Tap, Toggle, and SOCD, but it is a product-family guide—not a HE75 V2 feature matrix. It also warns that RT/SOCD/DKS can be treated as unauthorized in some games. [How to use a Hall-effect keyboard](https://epomaker.com/blogs/guides/how-to-use-a-hall-effect-keyboard)

### Toolkit implication

Do not label DKS, MT, Toggle, Combo, SOCD, or SnapKey as universally available. The app should query the connected keyboard first, display only advertised capabilities, and preserve an unsupported feature as a draft profile setting rather than attempting a write.

## Profiles and profile switching

The Hub source contains generic keyboard-profile functionality, including a current device profile and four profile labels, as well as profile save/import/export paths. Those are device-family facilities and should again be capability-gated for HE75 V2. [Hub client](https://hub.epomaker.com/assets/index-niFDUSiN.js)

No first-party source found documents **game/process-linked profile switching** for the HE75 V2 or Hub. The Toolkit's planned custom-game watcher is therefore a useful local feature, not an official-Hub clone:

- Custom games should store an executable path/name, selected Toolkit profile, enabled state, and optional launch arguments only for matching.
- Profile application should be explicit in logs and have a desktop/neutral fallback profile.
- Manual profile switching must always override the watcher until the next game detection event (or until the user re-enables auto switching).

## WebHID and external integration

Hub's code uses the browser's WebHID capability (`navigator.hid`); this matches EPOMAKER's Chrome/Edge requirement. It is a browser-to-device implementation, not a published third-party API. [Hub](https://hub.epomaker.com/) · [Hub client](https://hub.epomaker.com/assets/index-niFDUSiN.js)

No official EPOMAKER documentation was found for a stable public HID protocol, REST/localhost API, SDK, open port, or AI integration. The Toolkit should therefore provide its own **localhost-only, authenticated integration API** rather than claiming an EPOMAKER API. It should be off by default and expose:

- read-only device/capability/status/log endpoints;
- profile listing, dry-run validation, and explicit apply endpoints;
- no arbitrary raw-HID write endpoint in the first release;
- an API token stored locally, bound to `127.0.0.1`, with each write logged.

## Scope guard: HE75 V2 vs. HE75 V2 TMR

EPOMAKER markets separate HE75 V2 TMR material with a different feature set. Do not copy a capability claim from that model to the base HE75 V2 unless the connected board reports it or EPOMAKER documents it for the base model. [HE75 V2 product page](https://epomaker.com/products/epomaker-he75-v2)

## Recommended app backlog, in order

1. Add a connection/capability inspector and only surface verified controls.
2. Add named local Toolkit profiles with import/export, backup, diff, and dry-run.
3. Add manual profile switching, then custom-game executable matching and clear fallback behavior.
4. Add advanced-key editors only behind capability flags, beginning with Rapid Trigger and SnapKey.
5. Add the localhost authenticated API and a diagnostics page after profile writes are fully reliable.

