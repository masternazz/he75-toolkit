# VALORANT advanced-key settings: evidence and safe recommendations

Research date: 2026-09-21.  This note separates documented VALORANT guidance from general keyboard marketing. It does **not** treat a feature being common, technically possible, or marketed by a keyboard maker as a Riot approval.

## Bottom line

Use **Rapid Trigger on WASD** and **SnapKey/SOCD last-input priority on A/D** if it feels good. Those are the only advanced-key features for which a current keyboard maker's VALORANT-specific guide gives a concrete recommendation. Wooting's current guide explicitly says its equivalent of SnapKey (Snappy Tappy) is allowed in VALORANT, recommends A/D last-input priority, and offers a Valorant profile with the feature enabled. That is strong vendor evidence of ordinary use, but it is **not a Riot ruling**.

There is no public Riot page found that individually approves DKS, Mod-Tap, Toggle, Combo Keys, or keyboard macros for VALORANT. Riot's published enforcement language prohibits unauthorized hardware or software that gives an unfair advantage and calls out auto-clickers and automation. Therefore a one-physical-key-to-one-normal-game-input use (for example, a crouch toggle or a tap/hold remap) has a materially different risk profile from one press that creates multiple timed inputs, a combo, repeated input, or automated movement. The latter should remain off.

## Recommended Valorant profile

| Feature | Recommendation | Evidence / reason |
| --- | --- | --- |
| Adjustable actuation | WASD 0.2-0.5 mm; crouch 0.5-1.0 mm; abilities 1.0-2.0 mm; ultimate and jump >=2.0 mm; walk 1.0 mm | Wooting's Valorant-specific starting points. |
| Rapid Trigger | On for WASD. Start sensitivity at 0.2-0.4 mm; raise it if holding a direction produces jitter. Optionally test Left Ctrl only if you frequently tap crouch while strafing. | Wooting's Valorant-specific guidance says the biggest impact is on WASD and recommends WASD only as the starting point. |
| SnapKey / SOCD | Pair **A + D**, last-input priority. Optional W + S only after testing. | Wooting calls this Snappy Tappy and specifically recommends A/D last-input priority for Valorant. |
| Rappy / depth priority | An alternative to last-input priority, not an upgrade. Test it separately on A/D; use either it or SnapKey, not both. | Wooting says neither is universally better; its TenZ profile uses depth priority. |
| DKS / Dynamic Keystroke | Leave off for competitive Valorant. There is no Valorant-specific recommendation or pro profile evidence for it. | Its documented purpose is multiple actions—including combos—from one physical press, which is not needed to strafe or shoot. |
| Mod-Tap | Optional only for a non-combat convenience remap where a tap and hold each produce one ordinary input. Not a competitive movement setting. | Vendor documents it as tap Action A / hold Action B; no Valorant-specific recommendation found. |
| Toggle | Prefer VALORANT's in-game toggle/hold option. A keyboard toggle is only reasonable if it maps one key to one sustained normal action, such as crouch; it is not a performance setting. | Vendor gives toggled crouch as its generic example; no Valorant-specific recommendation found. |
| Combo Keys / macro sequences / turbo | Keep off. Do not put several game inputs, timed actions, repeated presses, movement-cleaning scripts, or recoil/aim behavior behind one physical key. | Riot says auto-clickers and unauthorized hardware/software giving an unfair advantage are permanently bannable; it also prohibits unauthorized automation programs. |

## Feature-by-feature evidence

### Rapid Trigger and travel

Wooting's June 2026 [Valorant guide](https://wooting.io/ja/post/wooting-valorant-guide-in-game-benefits-settings-and-pro-profiles) says Rapid Trigger has its biggest effect on WASD, recommends enabling it on WASD only as the initial configuration, and says Left Ctrl can help players who tap crouch while strafing. Its recommended sensitivity range is **0.2-0.4 mm**. It cautions that values that are too low can produce movement jitter/stutter from small finger movements; increase the value until that stops. The same guide's travel starting points are captured in the table above.

This is current, VALORANT-specific vendor guidance; it is not an assertion that every pro uses exactly those numbers.

### SnapKey / SOCD (Wooting: Snappy Tappy)

The same [Wooting Valorant guide](https://wooting.io/ja/post/wooting-valorant-guide-in-game-benefits-settings-and-pro-profiles) defines Snappy Tappy as last-input priority when opposite directions overlap. It recommends it primarily for A/D, says W/S is optional, and states: **"Snappy Tappy is not banned in Valorant"** (while saying it is banned in CS2). Its recommended ready-to-use 60HE profile has Snappy Tappy enabled.

This is the closest match to Epomaker's **SnapKey** when SnapKey is configured to prioritize the most recently pressed A or D. Epomaker's [HE75 V2 manual](https://epomaker.com/blogs/manuals/epomaker-he75-v2-manual) confirms the board is configured through Epomaker Hub, but it does not publish an equivalent VALORANT tuning guide or a public Riot-policy interpretation. Do not generalize the CS2 restriction to VALORANT, and disable SnapKey before playing a game or tournament whose rules prohibit SOCD.

### Rappy Snappy / depth-priority SOCD

Wooting describes [Rappy Snappy](https://wooting.io/uwu) as allowing only the more deeply pressed of two paired keys to remain active. Its [Valorant guide](https://wooting.io/ja/post/wooting-valorant-guide-in-game-benefits-settings-and-pro-profiles) says depth priority and last-input priority are both viable, explicitly says neither is universally better, and says TenZ prefers Rappy Snappy. That is evidence of a named pro's preference as reported by the manufacturer, not evidence that all pros use it.

For an Epomaker profile, choose **one** A/D behavior: last-input SnapKey for predictability, or depth-priority if the Hub exposes it and it genuinely feels better. Do not stack competing directional-priority features.

### DKS / Dynamic Keystroke

Wooting's [feature documentation](https://wooting.io/uwu) defines DKS as mapping multiple actions to one Hall-effect key: for example, one at a half press, another at full press, plus actions on release. The manufacturer explicitly describes it as capable of performing combos with one press. Wooting’s [Advanced Keys presets announcement](https://wooting.io/ja/post/wootility-5-4-app-linking-and-advanced-keys-presets) lists DKS on WASD for walking/running as a **generic game** preset, not a VALORANT recommendation.

The current Valorant guide covers actuation, Rapid Trigger, Snappy Tappy, Rappy Snappy, and Continuous Rapid Trigger; it does **not** recommend DKS for Valorant. With no Riot feature-level allowance and no Valorant-specific pro-setting evidence found, DKS should not be presented as “the best” Valorant setting. Do not bind a half/full press to multiple combat or movement inputs.

### Mod-Tap (MT)

Wooting's [feature documentation](https://wooting.io/uwu) defines Mod-Tap as tap = Action A and hold = Action B. It is a dual-role key remap, not a Hall-effect movement advantage. Wooting’s current Valorant guide does not recommend Mod-Tap or list it in a Valorant profile. If used at all, restrict it to a convenience key where each physical decision produces one normal in-game action; do not use it to create a rapid sequence or multiple simultaneous game actions.

### Toggle

Wooting's [feature documentation](https://wooting.io/uwu) defines Toggle Key as tapping to lock an action on/off while holding retains the normal action, and gives toggling crouch as its generic example. Its Valorant guide does not recommend keyboard Toggle as a competitive setting. VALORANT already exposes hold/toggle preferences for relevant actions, so use the in-game setting first. A hardware toggle is not needed for counter-strafing or aim.

### Combo Keys and macros

The Epomaker [HE75 V2 manual](https://epomaker.com/blogs/manuals/epomaker-he75-v2-manual) says its Hub can remap keys and set macros, but it does not publish a Valorant-specific macro policy. Wooting describes DKS as multiple actions and “combos” from one press; that distinction matters because a DKS/Combo configuration can become a macro in effect.

Riot's [VALORANT cheating guidance](https://support.riotgames.com/en-us/valorant/support-tools/addressing-cheating-in-valorant/) says that cheating with **auto-clickers, aimbots, and other unauthorized hardware or software that gives an unfair advantage** can result in a permanent ban. Riot's [Privacy Notice, Anti-Cheat section](https://www.riotgames.com/en/privacy-notice) says its Terms prohibit unauthorized third-party programs interacting with Riot services, including scripts, bots, trainers, and automation programs.

Those pages do not define an exhaustive rule for every onboard keyboard macro. The defensible reading is to avoid configurations that automate gameplay: multi-input combos on one press, turbo/repeat, timed press/release sequences, recoil control, auto-counter-strafe, or scripts that clean or alter inputs. A plain one-to-one key remap is fundamentally different, but Riot has not published a guarantee for every hardware implementation.

## What “pros use it” actually establishes

Wooting says its hardware is widely used by professional VALORANT players and names a TenZ profile with Rappy Snappy in its [Valorant guide](https://wooting.io/ja/post/wooting-valorant-guide-in-game-benefits-settings-and-pro-profiles). This supports testing **Rapid Trigger plus one SOCD option**. It does not establish that DKS, Mod-Tap, Toggle, Combo Keys, or macros are standard pro Valorant settings. The vendor's current guide specifically recommends only the movement/travel features above and omits the rest.

## Configuration guardrails


1. Keep one physical press associated with one intentional game action whenever possible.
2. Use the keyboard's onboard profile, not a background automation script, for normal settings.
3. Test one change at a time in the Range or Deathmatch. If Rapid Trigger jitters, increase its threshold; if SnapKey makes your movement less predictable, disable it.
4. Before Premier, LAN, or another organized event, read that event's current rules. Tournament policy can be narrower than ordinary matchmaking rules.
5. This document is research, not a Riot approval or a guarantee against enforcement. If Riot changes its policy or Vanguard flags a configuration, remove the feature and follow Riot Support’s direction.

