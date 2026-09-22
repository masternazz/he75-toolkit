# Hall-effect settings by game

Apply with `python hall.py <preset>`, the **Presets** buttons in the app, or let [auto-switch](autogame.md) do it when the game starts. Values are **actuation depth** in mm and the **Rapid Trigger step** (how far you release or press again before the key resets or re-fires).

> **Method and limits.** These come from manufacturer and esports guides, not from measuring your hands. Community forums (Reddit) could not be searched when this was written, so treat the numbers as well-sourced starting points and tune them. If you find better values, open an issue or PR.

## What Rapid Trigger buys you

A normal switch resets only after it passes a fixed reset point. With Rapid Trigger, the key resets the moment it moves up by the step size and re-fires the moment it moves down by the step size, wherever it is in the travel. For movement that means near-instant stops (counter-strafing), instant direction changes (strafing), and fast repeated taps.

Very low actuation adds little once Rapid Trigger is on (the key already fires almost immediately); the step size does most of the work. Set it too small (0.005 mm and under) and finger tremor causes double-typing or a "released" key while you hold it.

## Apex Legends: `apex`

| Keys | Actuation | Rapid Trigger | Why |
|---|---|---|---|
| A, D | 0.2 mm | 0.1 mm | hair-trigger strafe keys: tap-strafe and lurch-strafe redirect momentum in the air |
| W, S | 0.4 mm | 0.1 mm | slightly deeper so W does not drift forward while you strafe |
| Space | 0.2 mm | 0.1 mm | fast, repeatable jump for superglide / bunny-hop timing |
| Left Shift | 0.3 mm | 0.1 mm | |
| Left Ctrl, C (crouch / slide) | 0.4 mm | 0.1 mm | the crouch of a superglide must register right after the jump |
| 1-6, Q, Z, R (heals, abilities, reload) | 2.0 mm | off | deepest, so a resting finger does not misfire mid-fight |

**Superglide:** the jump has to register in the last ~0.1-0.2 s of a mantle and the crouch exactly one frame after the jump (a 2-3 frame window at 60 fps, about 33-50 ms). If the crouch registers first it fails. Rapid Trigger makes both keys consistent, but the crouch-after-jump rhythm is still practice.

Sources:
- [Corsair, "Best Rapid Trigger Settings for Apex Legends"](https://www.corsair.com/us/en/explorer/gamer/keyboards/best-rapid-trigger-settings-for-apex-legends/): 0.4 mm actuation / 0.1 mm Rapid Trigger for movement keys, deepest actuation with 0.3 mm on heal/ability keys.
- [DrunkDeer, hall-effect settings by game](https://drunkdeer.com/blogs/news/best-hall-effect-keyboard-settings-for-every-fps-game-cs2-valorant-apex-r6-more): Apex WASD 0.1, Space 0.2, Ctrl 0.3-0.5, Shift 0.3.
- [Attack Shark, Apex movement with Rapid Trigger](https://attackshark.com/blogs/knowledges/apex-legends-movement-rapid-trigger-guide): A/D 0.1-0.2, W about 0.4 (seen through a search summary).
- Superglide window: [Setup.gg](https://www.setup.gg/game/apex-legends/how-to-super-glide/) and the Apex movement community.

## Marvel Rivals: `rivals`

| Keys | Actuation | Rapid Trigger |
|---|---|---|
| W A S D | 1.0 mm | 0.2 mm |
| Space, Left Ctrl, Left Shift | 2.0 mm | off |

This is NetEase's own recommendation as relayed by [Razer](https://www.razer.com/blog/best-razer-keyboard-settings-for-marvel-rivals). Space, Ctrl and Shift are ability-adjacent (ascend, descend, hero movement), hence deep. Razer also suggests SOCD ("Snap Tap") on A/D, which this toolkit does **not** enable. If 1.0 mm feels sluggish, edit the preset to 0.5 mm.

## Valorant: `valorant`

| Keys | Actuation | Rapid Trigger |
|---|---|---|
| W A S D | 0.3 mm | 0.2 mm |
| Left Shift (walk) | 0.5 mm | off |
| Left Ctrl (crouch) | 0.8 mm | off |
| Space | 2.0 mm | off |
| C, Q, E (abilities) | 1.2 mm | off |
| X (ultimate) | 1.8 mm | off |

Sources: [Wooting's Valorant guide](https://wooting.io/post/wooting-valorant-guide-in-game-benefits-settings-and-pro-profiles) (WASD 0.2-0.5, Rapid Trigger 0.2-0.4, crouch 0.5-1.0, abilities 1.0-2.0, ultimate 2.0+, jump 2.0+, and a warning that a too-small step makes the character jitter) and [DrunkDeer](https://drunkdeer.com/blogs/news/best-hall-effect-keyboard-settings-for-every-fps-game-cs2-valorant-apex-r6-more) (WASD 0.2-0.3, abilities 1.2-1.5, ultimate 1.8).

## Generic FPS: `gaming`

WASD 0.2 / Rapid Trigger 0.1, Space/Shift/Ctrl/C 0.3 / Rapid Trigger 0.1, Q E R F G V Z X 1-5 at 1.2 with Rapid Trigger off. Adjustable: `python hall.py gaming --move 0.1 --action 0.3 --ability 1.5 --rt 0.15`.

## Rules to know

- **Rapid Trigger** itself is not banned in Valorant or CS2 competition as of this writing. Check the rules of any league or tournament you enter.
- **SOCD / Snap Tap** (last-key-wins on opposing directions) is banned by Valve in CS2 (since Aug 2024) and permitted by the current Valorant tournament ruleset, though Riot's general terms refer to "unfair advantage". This toolkit only sets actuation and Rapid Trigger, no SOCD.

## Editing or adding a preset

Presets are a plain dict in `hall.py`: `preset -> [(keys, actuation_mm, rapid_trigger_mm_or_None)]`. Key names are lowercase letters, digits, `space`, `lshift`, `lctrl`, `lalt`, `tab`, `caps`, `esc`. Add an entry, then `python hall.py yourpreset`.
