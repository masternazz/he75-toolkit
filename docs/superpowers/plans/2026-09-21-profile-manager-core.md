# HE75 Profile Manager Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build persistent Desktop and per-game profiles, focused-game switching, and a profile-card dashboard in the existing HE75 Toolkit.

**Architecture:** `profiles.py` owns schema, migration, and atomic storage; `switcher.py` resolves foreground/running-process state into transitions without USB dependencies. `operations.py` is the sole board-write entrypoint. `app.py` renders profile cards and invokes operations, while `autogame.py` becomes a CLI wrapper over the shared switcher.

**Tech Stack:** Python 3.10+, tkinter, standard-library `unittest`, Windows `ctypes`/`tasklist`, existing `winhid.py` and vendored EPOMAKER protocol.

**Spec:** `docs/superpowers/specs/2026-09-21-profile-manager-design.md`

## Global Constraints

- Windows 10/11 and wired HE75 V2 only; official EPOMAKER driver must be closed during writes.
- Persist unlimited PC profiles; the board still has only two onboard slots.
- Desktop is required; when no linked game runs it is the fallback profile.
- Foreground mapped games win; non-game alt-tabs retain the last running mapped game.
- All writes use the existing device lock, save a board backup, and verify readback.
- Do not add cloud control, LAN binding, or game automation.

---

### Task 1: Profile schema and persistent library

**Files:**
- Create: `profiles.py`
- Create: `tests/test_profiles.py`

**Interfaces:**
- Produces `Profile`, `ProfileStore`, `normalize_exe(name: str) -> str`, and `default_library() -> list[Profile]`.
- `Profile` fields: `id`, `name`, `kind`, `executables`, `lighting`, `hall`, `advanced`.
- `ProfileStore(path).load() -> list[Profile]` and `.save(profiles: list[Profile]) -> None`.

- [ ] **Step 1: Write the failing profile tests**

```python
def test_load_creates_desktop_profile_for_missing_library(self):
    library = ProfileStore(self.path).load()
    self.assertEqual([(p.name, p.kind) for p in library], [("Desktop", "desktop")])

def test_save_load_round_trip_normalizes_executables(self):
    profiles = [Profile.new("Apex", "game", executables=["R5APEX.EXE"])]
    ProfileStore(self.path).save([Profile.desktop(), *profiles])
    loaded = ProfileStore(self.path).load()
    self.assertEqual(loaded[1].executables, ["r5apex.exe"])
```

- [ ] **Step 2: Verify the tests fail**

Run: `python -m unittest tests.test_profiles -v`

Expected: FAIL because `profiles` does not exist.

- [ ] **Step 3: Implement the smallest serializable profile model**

```python
@dataclass
class Profile:
    id: str
    name: str
    kind: Literal["desktop", "game"]
    executables: list[str] = field(default_factory=list)
    lighting: dict[str, Any] = field(default_factory=dict)
    hall: dict[str, Any] = field(default_factory=dict)
    advanced: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def desktop(cls) -> "Profile":
        return cls("desktop", "Desktop", "desktop")
```

Use JSON written to a temporary sibling file then `Path.replace()`; retain a timestamped copy before replacing an existing malformed library.

- [ ] **Step 4: Verify profile tests pass**

Run: `python -m unittest tests.test_profiles -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add profiles.py tests/test_profiles.py
git commit -m "feat: add persistent profile library"
```

### Task 2: Deterministic game/focus transition resolver

**Files:**
- Create: `switcher.py`
- Create: `tests/test_switcher.py`

**Interfaces:**
- Consumes `Profile` from `profiles.py`.
- Produces `ProcessSnapshot(running: set[str], foreground: str | None)`, `SwitchState(active_id: str, last_game_id: str | None)`, and `resolve(snapshot, profiles, state) -> SwitchState`.

- [ ] **Step 1: Write failing transition tests**

```python
def test_foreground_mapped_game_wins_between_running_games(self):
    state = SwitchState("desktop", None)
    result = resolve(ProcessSnapshot({"r5apex.exe", "valorant-win64-shipping.exe"}, "valorant-win64-shipping.exe"), self.profiles, state)
    self.assertEqual(result.active_id, "valorant")

def test_alt_tab_to_unmapped_window_retains_running_game(self):
    state = SwitchState("apex", "apex")
    result = resolve(ProcessSnapshot({"r5apex.exe", "discord.exe"}, "discord.exe"), self.profiles, state)
    self.assertEqual(result.active_id, "apex")

def test_no_linked_processes_restores_desktop(self):
    result = resolve(ProcessSnapshot({"discord.exe"}, "discord.exe"), self.profiles, SwitchState("apex", "apex"))
    self.assertEqual(result.active_id, "desktop")
```

- [ ] **Step 2: Verify tests fail**

Run: `python -m unittest tests.test_switcher -v`

Expected: FAIL because `switcher` does not exist.

- [ ] **Step 3: Implement pure resolution logic and Windows snapshot adapter**

```python
def resolve(snapshot: ProcessSnapshot, profiles: Sequence[Profile], state: SwitchState) -> SwitchState:
    linked = {exe: profile for profile in profiles for exe in profile.executables}
    foreground = linked.get(normalize_exe(snapshot.foreground or ""))
    if foreground:
        return SwitchState(foreground.id, foreground.id)
    if state.last_game_id and any(state.last_game_id == p.id and set(p.executables) & snapshot.running for p in profiles):
        return state
    return SwitchState("desktop", None)
```

Keep process/window collection behind `snapshot_windows() -> ProcessSnapshot`; tests call `resolve` only.

- [ ] **Step 4: Verify tests pass**

Run: `python -m unittest tests.test_switcher -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add switcher.py tests/test_switcher.py
git commit -m "feat: resolve focused game profiles"
```

### Task 3: Safe profile preview/apply operations

**Files:**
- Create: `operations.py`
- Create: `tests/test_operations.py`
- Modify: `hall.py` only to expose existing preset/Hall helpers without CLI parsing.

**Interfaces:**
- Consumes `Profile` and existing `hall`, `winhid`, lighting codec.
- Produces `preview(profile, current) -> list[dict]` and `apply_profile(profile, open_keyboard=winhid.open_keyboard) -> ApplyResult`.
- `ApplyResult(profile_id, changed: bool, verified: bool, details: list[str])`.

- [ ] **Step 1: Write failing preview tests**

```python
def test_preview_contains_only_changed_lighting_fields(self):
    result = preview(self.profile, {"lighting": {"keys": {"mode": "wave", "rgb": 1}}})
    self.assertEqual(result, [{"section": "lighting.keys", "from": {"mode": "wave", "rgb": 1}, "to": self.profile.lighting["keys"]}])

def test_apply_requires_readback_verification(self):
    with self.assertRaises(VerificationError):
        apply_profile(self.profile, open_keyboard=lambda: FakeKeyboard(readback_matches=False))
```

- [ ] **Step 2: Verify tests fail**

Run: `python -m unittest tests.test_operations -v`

Expected: FAIL because `operations` does not exist.

- [ ] **Step 3: Implement shared serialized writer**

```python
DEVICE_LOCK = threading.Lock()

def apply_profile(profile, open_keyboard=winhid.open_keyboard):
    with DEVICE_LOCK:
        keyboard = open_keyboard()
        try:
            keyboard.identify()
            # capture current board state, write selected profile sections, then read and compare
        finally:
            keyboard.transport.close()
```

Reuse the existing Hall backup/readback path and `set_light` readback; do not allow an arbitrary command payload.

- [ ] **Step 4: Verify tests pass and run packet regression tests**

Run: `python -m unittest tests.test_operations tests.test_packets -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add operations.py hall.py tests/test_operations.py
git commit -m "feat: add safe profile preview and apply"
```

### Task 4: Dashboard and shared auto-switch integration

**Files:**
- Modify: `app.py`
- Modify: `autogame.py`
- Create: `tests/test_autogame.py`
- Modify: `README.md`
- Modify: `docs/autogame.md`

**Interfaces:**
- Consumes `ProfileStore`, `resolve`, `apply_profile`.
- Produces `ProfileMonitor` with `tick(snapshot) -> ApplyResult | None` and a dashboard showing active profile, cards, manual Apply, Add profile, and Add app.

- [ ] **Step 1: Write failing monitor tests**

```python
def test_monitor_applies_only_when_resolved_profile_changes(self):
    monitor = ProfileMonitor(self.profiles, apply=self.calls.append)
    monitor.tick(ProcessSnapshot({"r5apex.exe"}, "r5apex.exe"))
    monitor.tick(ProcessSnapshot({"r5apex.exe", "discord.exe"}, "discord.exe"))
    self.assertEqual([profile.id for profile in self.calls], ["apex"])
```

- [ ] **Step 2: Verify tests fail**

Run: `python -m unittest tests.test_autogame -v`

Expected: FAIL because `ProfileMonitor` does not exist.

- [ ] **Step 3: Implement monitor and dashboard without advanced editor controls**

Add a top active-profile status, editable profile cards, a `ttk.Treeview` for linked apps, and an Add App dialog. Populate Running apps using the process snapshot; Browse uses `filedialog.askopenfilename(filetypes=[("Programs", "*.exe")])`. Keep existing lighting controls as the selected profile's basic editor.

- [ ] **Step 4: Verify automated tests and smoke-test the UI**

Run: `python -m unittest discover -s tests -v`

Expected: PASS.

Run: `python app.py`

Expected: Profile dashboard opens, an existing profile can be applied manually, and Add App lists running processes without writing to the keyboard.

- [ ] **Step 5: Commit**

```bash
git add app.py autogame.py README.md docs/autogame.md tests/test_autogame.py
git commit -m "feat: add desktop game profile dashboard"
```
