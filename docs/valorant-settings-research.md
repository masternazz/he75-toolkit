# VALORANT Hall-Effect Settings: Research Note

Researched September 21, 2026. This is a conservative starting profile for an
EPOMAKER HE75 V2; its labels may differ from Wooting's. It is not an official
Riot configuration or a guarantee of competitive eligibility.

## Recommended starting point

| Control | Actuation | Rapid Trigger | Why |
| --- | ---: | --- | --- |
| `W`, `A`, `S`, `D` | 0.3 mm | On; 0.3 mm press and release sensitivity | Fast stops and direction changes without beginning at the most twitchy setting. |
| Left `Ctrl` (crouch) | 0.7 mm | Off initially; enable at 0.3 mm only if you deliberately tap-crouch in fights | Avoids accidental crouches while still being responsive. |
| `Shift` (walk) | 1.0 mm | Off | Deliberate walk control. |
| Ability keys (`Q`, `E`, `C`, `X`) | 1.5 mm (`X`: 2.2 mm) | Off | Reduces accidental utility/ultimate usage. |
| `Space` (jump) | 2.0 mm | Off | Reduces accidental jumps. |
| `Esc` and Windows | 4.0 mm | Off | Makes accidental interruptions unlikely. |

**Tune it in the Range or Deathmatch:** if holding a movement key causes
jitter/stutter, raise the Rapid Trigger press/release sensitivity one step
(e.g., from 0.3 to 0.4 mm). If it feels stable but too slow, lower it one step.
Do not chase the smallest number just because it exists.

For the question "half press versus full press": use **one normal action per
key** in VALORANT. Set one actuation point as above; do **not** assign an action
at half press and another at full press (DKS/Dynamic Keystroke), and do not use
Combo Keys or macro sequences in competitive play. The benefit of a Hall-effect
board here is its physical key travel and reset behavior, not turning one press
into multiple game actions.

## What the manufacturer guidance says

Wooting's current VALORANT guide is useful manufacturer guidance for Hall-effect
keyboards, but it is **not Riot policy** and is not specific to the HE75 V2:

- Its published starting ranges are WASD 0.2–0.5 mm; crouch 0.5–1.0 mm;
  abilities 1.0–2.0 mm; ultimate 2.0 mm or deeper; walk 1.0 mm; jump 2.0 mm;
  and Windows/Escape 4.0 mm. It says to enable Rapid Trigger on WASD first.
  [Wooting VALORANT guide](https://wooting.io/zh-CN/post/wooting-valorant-guide-in-game-benefits-settings-and-pro-profiles)
- For Rapid Trigger sensitivity, its recommended starting band is **0.2–0.4 mm**.
  Lower values respond sooner but may treat small finger movements as releases;
  increase it if movement jitters. [Wooting VALORANT guide](https://wooting.io/zh-CN/post/wooting-valorant-guide-in-game-benefits-settings-and-pro-profiles)
- Continuous Rapid Trigger is not useful at low 0.1–0.5 mm actuation points;
  Wooting suggests leaving it off initially and considering it only for movement
  keys at 2.0 mm or higher. [Wooting VALORANT guide](https://wooting.io/zh-CN/post/wooting-valorant-guide-in-game-benefits-settings-and-pro-profiles)

### Pro settings: what is actually substantiated

There is no universal "pro setting." Wooting publishes two imported profiles in
its guide: a recommended 60HE/60HE v2 profile (`90640006733bdcbcc0c3a96b39c8d9228449`)
with Snappy Tappy enabled, and a TenZ 80HE profile
(`28cf2e9f936cd72fed9bc326a36c49eaf3ea`) with Rappy Snappy. It also says TenZ
prefers Rappy Snappy. Those are **individual/vendor profile examples**, not
settings transferable verbatim to a different keyboard or proof of what every
professional uses. [Wooting VALORANT guide](https://wooting.io/zh-CN/post/wooting-valorant-guide-in-game-benefits-settings-and-pro-profiles)

Wooting additionally says its TenZ edition ships with his Wootility
configuration, including actuation and Rapid Trigger tuning, but it does not
publish the exact individual values on that page. [Wooting 80HE TenZ Takeover](https://wooting.io/wooting-80he-tenz)

## Riot-policy boundary and safe configuration

Riot's current public VALORANT/Riot-wide material located for this research does
**not specifically approve or ban** Rapid Trigger, SnapKey/SOCD, or a particular
actuation depth. Do not treat a manufacturer statement as an official Riot
ruling.

Riot's Terms prohibit unauthorized third-party programs including scripts,
bots, trainers, and automation programs that interact with Riot services, and
allow discipline for cheating or other anti-competitive behavior. Its Community
Pact defines scripting as third-party software **or hardware** taking automated
actions or responding to game events on a player's behalf. Riot Support says
unauthorized hardware or software that creates an unfair advantage, including
auto-clickers, can lead to a permanent ban. Sources:

- [Riot Games Terms of Service, §7.1 and §9](https://www.riotgames.com/en/terms-of-service)
- [Riot Community Pact: No Cheating or Scripting](https://www.riotgames.com/en/community-pact)
- [Riot Support: Addressing Cheating in VALORANT](https://support.riotgames.com/en-us/valorant/support-tools/addressing-cheating-in-valorant/)
- [Riot Support: Third-Party Applications](https://support.riotgames.com/en-us/riot/events/third-party-applications)

Therefore the conservative ranked setup is:

- **Use:** normal single-key mapping, per-key actuation, and Rapid Trigger.
- **Leave off:** Macro Settings, Combo Keys, Dynamic Keystroke/DKS multi-stage
  mappings, toggle/auto-repeat behavior, and software that changes inputs from
  game state.
- **SnapKey/SOCD:** leave it **off** for the conservative profile. Wooting says
  its last-input-priority Snappy Tappy is allowed in VALORANT, but Riot has not
  published a VALORANT-specific confirmation found in this research. If you
  decide to test it, use only an onboard A/D last-input-priority setting, test
  it in the Range/Deathmatch first, and re-check Riot rules before tournament
  play. Never use it for CS2—Wooting states it is banned there.

This is a risk-minimizing interpretation, not legal advice or a claim that a
simple onboard key feature is prohibited. Riot can change enforcement or rules,
especially for a specific tournament; use that event's rules where applicable.
