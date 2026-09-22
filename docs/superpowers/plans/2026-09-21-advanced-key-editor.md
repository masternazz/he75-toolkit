# HE75 Advanced-Key Editor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add capability-gated, profile-backed advanced-key editing and previews to the profile dashboard.

**Architecture:** Extend profile data with declarative advanced-key definitions. A dedicated `advanced_keys.py` validates definitions and translates only supported actions into existing HE protocol operations. The UI never builds raw packets and queries board capabilities before displaying editable controls.

**Tech Stack:** Python 3.10+, tkinter, `unittest`, existing vendored `epomaker_driver` protocol.

**Spec:** `docs/superpowers/specs/2026-09-21-profile-manager-design.md`

## Global Constraints

- Implement after `2026-09-21-profile-manager-core.md`.
- Show controls only when the connected HE75 V2 reports support.
- Preview every advanced-key modification; board writes stay in `operations.py`.
- Do not add game macros, turbo, timed repetition, or arbitrary action execution.

---

### Task 1: Advanced-key definitions and validation

**Files:**
- Create: `advanced_keys.py`
- Create: `tests/test_advanced_keys.py`
- Modify: `profiles.py`

**Interfaces:**
- Produces `AdvancedKey(kind, keys, settings)`, `capabilities(status) -> set[str]`, and `validate(definition, available) -> AdvancedKey`.

- [ ] **Step 1: Write failing validation tests**

```python
def test_snap_pair_requires_two_distinct_keys(self):
    with self.assertRaisesRegex(ValueError, "two different"):
        validate({"kind": "snap", "keys": ["a", "a"], "settings": {}}, {"snap"})

def test_unsupported_dks_is_rejected_before_write(self):
    with self.assertRaisesRegex(ValueError, "not supported"):
        validate({"kind": "dks", "keys": ["w"], "settings": {}}, {"snap"})
```

- [ ] **Step 2: Verify tests fail**

Run: `python -m unittest tests.test_advanced_keys -v`

Expected: FAIL because `advanced_keys` does not exist.

- [ ] **Step 3: Implement a closed set of supported definitions**

Accept only `snap`, `dks`, `mt`, `tgl_hold`, `tgl_dots`, and `combo` with explicit key lists and depth/action settings. Reject unknown fields and unsupported capability names.

- [ ] **Step 4: Verify tests pass**

Run: `python -m unittest tests.test_advanced_keys -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add advanced_keys.py profiles.py tests/test_advanced_keys.py
git commit -m "feat: validate advanced key profiles"
```

### Task 2: Capability-gated operations and preview

**Files:**
- Modify: `operations.py`
- Modify: `tests/test_operations.py`

**Interfaces:**
- Produces `preview_advanced(profile, status) -> list[dict]` and integrates validated definitions into `apply_profile`.

- [ ] **Step 1: Write failing operation tests**

```python
def test_preview_omits_advanced_definition_not_supported_by_board(self):
    profile = Profile.new("Test", "game", advanced={"keys": [{"kind": "snap", "keys": ["a", "d"], "settings": {}}]})
    self.assertEqual(preview_advanced(profile, {"capabilities": []}), [])
```

- [ ] **Step 2: Verify tests fail**

Run: `python -m unittest tests.test_operations -v`

Expected: FAIL because `preview_advanced` does not exist.

- [ ] **Step 3: Implement capability discovery and protocol adapter**

Call `keyboard.status()`/identity before building the plan. Use `keyboard.set_snap` for SnapKey and existing mode planner only for definitions that validate; add verification after every protocol write.

- [ ] **Step 4: Verify tests pass**

Run: `python -m unittest tests.test_operations tests.test_advanced_keys -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add operations.py tests/test_operations.py
git commit -m "feat: preview and apply supported advanced keys"
```

### Task 3: Profile editor controls and documentation

**Files:**
- Modify: `app.py`
- Modify: `README.md`
- Create: `docs/advanced-keys.md`

**Interfaces:**
- Consumes `validate`, `preview_advanced`, and profile editor selection state.
- Produces an Advanced Keys panel that displays capabilities, edits one selected definition, and requires Preview before Apply.

- [ ] **Step 1: Write a failing UI-independent formatting test**

```python
def test_advanced_summary_names_snap_pair(self):
    self.assertEqual(advanced_summary({"kind": "snap", "keys": ["a", "d"], "settings": {}}), "SnapKey: A ↔ D")
```

- [ ] **Step 2: Verify test fails**

Run: `python -m unittest tests.test_advanced_keys -v`

Expected: FAIL because `advanced_summary` does not exist.

- [ ] **Step 3: Implement panel and docs**

Use a read-only capability notice, a tree of saved definitions, Add/Edit/Delete controls, and a preview dialog showing key outputs. Explain each feature in plain language and state that feature availability is board/firmware dependent.

- [ ] **Step 4: Verify full test suite and hardware read-only status**

Run: `python -m unittest discover -s tests -v`

Expected: PASS.

Run: `python app.py`

Expected: Advanced panel displays only board-supported capabilities and preview completes without a write.

- [ ] **Step 5: Commit**

```bash
git add app.py README.md docs/advanced-keys.md tests/test_advanced_keys.py
git commit -m "feat: add capability-gated advanced key editor"
```
