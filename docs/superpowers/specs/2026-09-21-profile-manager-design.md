# Profile Manager and Local API Design

## Goal

Evolve the existing HE75 Toolkit desktop app into a profile-first controller.
The user can create a Desktop profile for work and lounging, create game-specific
profiles, link them to executables, and have the active profile change based on
running/focused games. A local, authenticated HTTP API exposes the same state and
controlled writes to an AI assistant or other local automation.

The application remains a Windows-only, direct-USB controller for the EPOMAKER
HE75 V2. It does not expose the keyboard to the network and never sends board
data to an AI service itself.

## Scope

### Profile library

Profiles are saved on the PC as JSON, not limited to the keyboard's two onboard
profile slots. Each profile has a stable ID, display name, kind (`desktop` or
`game`), optional lighting settings, optional Hall-effect settings, optional
advanced-key settings, and zero or more executable links.

The single Desktop profile is required and is the fallback when no mapped game
is running. Existing Apex, Marvel Rivals, Valorant, generic FPS, lighting looks,
and current board settings can be imported into library profiles without a board
write until the user chooses Apply.

### Switching behavior

The monitor polls running processes and foreground window identity on a short
interval.

1. Collect every running executable that has a linked profile.
2. If the foreground executable has a linked profile, make that profile active.
3. Otherwise retain the most recently active linked game profile while any
   linked game remains running. Alt-tabbing to Discord, a browser, or another
   unmapped program therefore does not restore Desktop.
4. Restore Desktop only after no linked game remains running.

The monitor applies a profile only on a profile transition. Writes are serialized
through the existing device lock, logged, backed up, and verified by board
readback. If a game profile cannot apply, the last verified board state remains
active and the monitor reports a retryable error.

### App experience

The desktop window becomes a profile dashboard with:

- An active-profile header showing the source (`manual`, `foreground`, or
  `fallback`) and the connected board/profile slot.
- A card grid for Desktop and saved game profiles. Cards show linked apps,
  lighting color/effect, and Hall-effect summary; one-click Apply is available
  for every card.
- An Add profile flow with a name and game/desktop type.
- An Add app flow offering **Running apps** (deduplicated visible process/window
  names) and **Browse for .exe**. The saved executable name is the matching key;
  a full path is displayed only for clarity and is not required for a match.
- A profile editor split into Lighting, Key response, and Advanced keys.

Advanced controls are capability-gated after device discovery. The app will only
show writable SnapKey/SOCD, DKS, Mod-Tap, Toggle, Combo, or macro controls when
the connected model and protocol report support. Each advanced edit includes a
plain-language description and a preview of affected key outputs. No macro or
multi-action configuration is enabled by default.

### Local API and AI integration

The app optionally starts a loopback-only HTTP server on `127.0.0.1` using an
ephemeral per-install bearer token stored locally. It is disabled until enabled
in Settings, binds no LAN interface, and displays its port/token-copy control in
the UI. The API has versioned endpoints:

- `GET /v1/status`: connected device, active profile, monitor status, capabilities.
- `GET /v1/profiles`: profile summaries; `GET /v1/profiles/{id}`: full profile.
- `POST /v1/profiles`: create/update a profile after schema validation.
- `POST /v1/preview`: calculate board changes without writing.
- `POST /v1/apply/{id}`: apply a saved profile; writes require an explicit
  `confirm: true` body field.
- `GET /v1/logs`: recent redacted activity entries.

The API has no endpoint to run arbitrary commands, alter its bind address, or
return a token. It shares the same validation, device lock, backups, and
readback verification as UI operations. It is an integration surface for an AI
assistant, not an embedded model or a cloud service.

## Architecture

Extract application behavior from `app.py` into focused modules:

```
profiles.py       profile schema, storage, import/export, validation
switcher.py       running/foreground process resolution and transition state
operations.py     preview/apply orchestration, backup/readback/device locking
local_api.py      loopback HTTP server and bearer-token middleware
app.py            tkinter dashboard, profile editor, settings and event log
autogame.py       compatibility wrapper around switcher for CLI/autostart
```

`operations.py` is the sole writer to the keyboard. Both the UI and the local
API call it, which prevents different validation or write behavior by caller.
`profiles.py` remains hardware-independent and unit-testable without a keyboard.
`switcher.py` receives process/window snapshots through an adapter so priority
and fallback behavior are unit-testable.

## Data and safety

Profile storage lives under a user-local application-data directory, with an
atomic write and a timestamped backup before destructive profile replacement.
The current settings backup mechanism remains in place for every board write.

Loading an older toolkit install creates a Desktop profile from its current
generic/idle behavior and migrates built-in presets into editable profiles.
Malformed data is preserved as a backup and surfaced to the user instead of
silently resetting profiles.

## Testing

Unit tests will cover profile serialization/migration/validation, executable
normalization, foreground priority, non-game alt-tab retention, all-games-closed
fallback, API authentication, API preview versus explicit-confirm apply, and
capability gating.

Existing packet tests remain unchanged. Hardware smoke checks will verify device
identification, a dry-run preview, a read-only profile-state query, and an
explicit manual profile apply followed by readback. The local API is tested only
against loopback and with a generated test token.

## Non-goals

- LAN, cloud, or unauthenticated remote control.
- An embedded AI model or automatic AI-initiated keyboard writes.
- Replacing the official EPOMAKER Hub.
- Supporting boards other than the verified HE75 V2 in this iteration.
- Automating or generating game macros.
