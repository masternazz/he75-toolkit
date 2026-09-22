# Verified Advanced Keys Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add profile-backed, capability-gated SnapKey and magnetic-mode foundations without guessing a physical key slot or sending macro/turbo actions.

**Architecture:** `advanced_keys.py` translates factory-labelled HE75 keys into the immutable physical slots recorded in the vendored HE75 matrix, validates saved definitions, and turns simple key names into vendor action bytes. `operations.py` is still the sole writer: it reads `keyboard.status()` first, applies only definitions supported by that board, and relies on the vendored driver's full readback. The UI starts with a clearly labelled SnapKey pair editor; DKS, Mod-Tap, and Toggle capability/status are shown but stay unavailable until their exact trigger semantics have been captured from HE75 firmware.

**Tech Stack:** Python 3.10+, tkinter, `unittest`, `epomaker_driver` magnetic protocol.

**Spec:** `docs/superpowers/specs/2026-09-21-profile-manager-design.md`

## Global Constraints

- Target only the verified EPOMAKER HE75 V2 (`device_id == 3518`) on wired USB.
- Derive physical slots from the vendored HE75 factory matrix; never infer them from a user remap.
- Query capabilities before every advanced write and reject unsupported definitions before HID I/O.
- Use `keyboard.set_snap` / `keyboard.set_magnetic_mode`; do not build raw HID packets in toolkit code.
- Do not add macros, turbo, timed repetition, arbitrary actions, or a LAN/cloud endpoint.
- Preview every edit and keep `operations.py` as the only hardware writer.

---

### Task 1: HE75 physical-key mapping and validated saved definitions

**Files:**
- Create: `advanced_keys.py`
- Create: `tests/test_advanced_keys.py`
- Modify: `profiles.py`

**Interfaces:**
- Produces `physical_slots(device_id: int) -> dict[str, int]`, `capabilities(status: dict) -> set[str]`, `validate(definition: dict, available: set[str]) -> dict`, and `advanced_summary(definition: dict) -> str`.
- `Profile.advanced["keys"]` holds only validated definition dictionaries.

- [ ] **Step 1: Write the failing mapping and validation tests**

```python
def test_he75_factory_map_resolves_distinct_a_and_d_slots(self):
    slots = physical_slots(3518)
    self.assertIn("a", slots)
    self.assertIn("d", slots)
    self.assertNotEqual(slots["a"], slots["d"])

def test_snap_pair_requires_two_different_known_keys(self):
    with self.assertRaisesRegex(ValueError, "two different"):
        validate({"kind": "snap", "keys": ["a", "a"]}, {"snap"})

def test_unsupported_mode_is_rejected_before_hardware(self):
    with self.assertRaisesRegex(ValueError, "not supported"):
        validate({"kind": "dks", "key": "w", "settings": {}}, {"snap"})
```

- [ ] **Step 2: Run the focused test file and verify RED**

Run: `python -m unittest tests.test_advanced_keys -v`

Expected: import failure because `advanced_keys.py` does not exist.

- [ ] **Step 3: Implement the closed, hardware-independent translator**

```python
def physical_slots(device_id: int) -> dict[str, int]:
    matrix = data_file("he60-matrices.json")[str(device_id)]["defaultMatrix"]
    return {
        name: slot
        for slot in range(128)
        for name in actions.KEYS
        if bytes(matrix[slot * 4 : slot * 4 + 4]) == actions.keyboard(name)
    }

def capabilities(status: dict) -> set[str]:
    reported = set(status.get("capabilities", []))
    return ({"snap"} if "snap" in reported else set()) | (
        {"dks", "mt", "tgl_hold", "tgl_dots"} if "magnetic-modes" in reported else set()
    )
```

Accept only `{"kind": "snap", "keys": ["label", "label"]}` in this first deliverable. Reject unknown fields, unsupported capabilities, non-string labels, duplicated keys, and labels absent from the HE75 factory map. Implement `advanced_summary` as `SnapKey: A ↔ D`.

- [ ] **Step 4: Run the focused test file and verify GREEN**

Run: `python -m unittest tests.test_advanced_keys -v`

Expected: PASS.

- [ ] **Step 5: Commit the independently testable foundation**

```powershell
git add advanced_keys.py profiles.py tests/test_advanced_keys.py
git commit -m "feat: validate HE75 advanced key definitions"
```

### Task 2: Capability-gated SnapKey preview and verified write

**Files:**
- Modify: `operations.py`
- Modify: `tests/test_operations.py`

**Interfaces:**
- Produces `preview_advanced(profile: Profile, status: dict) -> list[dict]` and adds advanced application to `apply_profile`.
- Consumes `advanced_keys.capabilities`, `advanced_keys.physical_slots`, and `advanced_keys.validate`.

- [ ] **Step 1: Write the failing capability and write-boundary tests**

```python
def test_preview_hides_snap_when_board_does_not_report_snap(self):
    profile = Profile("test", "Test", "game", advanced={"keys": [{"kind": "snap", "keys": ["a", "d"]}]})
    self.assertEqual(preview_advanced(profile, {"capabilities": []}), [])

def test_apply_snap_uses_he75_factory_slots_after_status_check(self):
    keyboard = FakeKeyboard(status={"capabilities": ["snap"]}, device_id=3518)
    profile = Profile("test", "Test", "game", advanced={"keys": [{"kind": "snap", "keys": ["a", "d"]}]})
    apply_profile(profile, open_keyboard=lambda: keyboard)
    self.assertEqual(keyboard.snap_calls, [(keyboard.slots["a"], keyboard.slots["d"])])
```

- [ ] **Step 2: Run the focused operation tests and verify RED**

Run: `python -m unittest tests.test_operations -v`

Expected: FAIL because `preview_advanced` and advanced application do not exist.

- [ ] **Step 3: Add the advanced operation boundary**

```python
def preview_advanced(profile, status):
    available = capabilities(status)
    return [
        {"summary": advanced_summary(item), "definition": validate(item, available)}
        for item in profile.advanced.get("keys", [])
        if item.get("kind") in available
    ]

def _apply_advanced(keyboard, profile):
    status = keyboard.status()
    for item in preview_advanced(profile, status):
        definition = item["definition"]
        first, second = (physical_slots(keyboard.expected_id)[key] for key in definition["keys"])
        keyboard.set_snap(first, second)
```

Call `_apply_advanced` within `DEVICE_LOCK` after identity and before lighting. Append only the driver's verified result to `ApplyResult.details`. Treat an unreported capability as a `ValueError`; never silently skip a saved request during Apply.

- [ ] **Step 4: Run operation and advanced-key tests and verify GREEN**

Run: `python -m unittest tests.test_operations tests.test_advanced_keys -v`

Expected: PASS.

- [ ] **Step 5: Commit the writer boundary**

```powershell
git add operations.py tests/test_operations.py
git commit -m "feat: apply verified HE75 SnapKey profiles"
```

### Task 3: SnapKey profile editor, clear capability messaging, and docs

**Files:**
- Modify: `app.py`
- Modify: `README.md`
- Create: `docs/advanced-keys.md`
- Modify: `tests/test_advanced_keys.py`

**Interfaces:**
- Consumes `advanced_summary`, `preview_advanced`, and saved `Profile.advanced` definitions.
- Produces an Advanced Keys panel for the selected profile with Add SnapKey, Remove, Preview, and Apply controls.

- [ ] **Step 1: Write the failing formatting test**

```python
def test_advanced_summary_formats_a_snap_pair_for_the_dashboard(self):
    self.assertEqual(
        advanced_summary({"kind": "snap", "keys": ["a", "d"]}),
        "SnapKey: A ↔ D",
    )
```

- [ ] **Step 2: Run the focused test and verify RED**

Run: `python -m unittest tests.test_advanced_keys -v`

Expected: FAIL because `advanced_summary` does not exist.

- [ ] **Step 3: Implement the profile editor**

Add an **Advanced keys** frame below the selected profile dashboard. Show the read-only message: `SnapKey is available after the keyboard reports it. DKS, Mod-Tap, and Toggle will be added after their HE75 trigger values are captured; they are not guessed.`

The Add dialog uses two readonly comboboxes listing only known HE75 factory labels. It rejects the same label on both sides, saves `{"kind":"snap","keys":[first,second]}` under `selected_profile.advanced["keys"]`, atomically saves the library, and re-renders. Preview shows the two labels and confirms it makes no board write. Apply calls existing `apply_profile_id`.

- [ ] **Step 4: Document the exact safety contract**

Document physical-label semantics, board capability gating, confirmed readback, and that SnapKey/SOCD suitability is game/tournament-rule dependent. Explain that DKS/MT/Toggle are deliberately not configured until HE75-specific trigger values are measured.

- [ ] **Step 5: Run the full suite and a read-only GUI smoke check**

Run: `python -m unittest discover -s tests -v`

Expected: PASS.

Run: `python app.py`

Expected: the app launches, Advanced Keys shows a no-write Preview path, and no keyboard configuration changes until Apply.

- [ ] **Step 6: Commit the UI and docs**

```powershell
git add app.py README.md docs/advanced-keys.md tests/test_advanced_keys.py
git commit -m "feat: add HE75 SnapKey profile editor"
```

## Plan self-review

- **Spec coverage:** profiles, capability gating, preview, verified device writing, plain-language UI, documentation, and no macro/automation path are covered. DKS/MT/Toggle configuration is intentionally deferred because neither the current HE75 driver nor captured board state assigns safe meanings to their trigger bytes.
- **Placeholder scan:** no placeholders, generic validation steps, or cross-task references remain.
- **Type consistency:** profile definitions are dicts under `advanced["keys"]`; `advanced_keys.py` owns validation/mapping; `operations.py` owns the only write path.
