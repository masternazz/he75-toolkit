"""Hall-effect (magnetic) key settings for the EPOMAKER HE75 V2: actuation point + Rapid Trigger, per key.

Runs the vendored epomaker-driver-linux codec over Windows hid.dll (winhid.py). No driver app needed
(and it must be closed: it holds the device). Applies to the ACTIVE onboard profile.

  python hall.py show                        # keys that differ from stock
  python hall.py apex | rivals | valorant    # per-game presets (docs/game-settings.md)
  python hall.py gaming [--move 0.1 ...]     # generic FPS preset
  python hall.py reset                       # every key back to stock (2.0 mm, Rapid Trigger off)
"""
import argparse, json, time
from pathlib import Path
from types import SimpleNamespace

import winhid
from epomaker_driver import actions
from epomaker_driver.errors import ProtocolError

HERE = Path(__file__).parent
HID = {**{chr(97 + i): 4 + i for i in range(26)}, **{str(i): 29 + i for i in range(1, 10)}, "0": 39,
       "space": 44, "lshift": 225, "lctrl": 224, "lalt": 226, "tab": 43, "caps": 57, "esc": 41}
NAME = {v: k for k, v in HID.items()}
FIELDS = ("travel", "lift", "rapid_press", "rapid_lift", "deadzone", "top_deadzone", "fire")
# "Stock" = 2.0 mm and Rapid Trigger off. Rapid step values are ignored while it's off (and the planner
# rejects them for a key with fire=False), so a reset never writes them.
RESET = dict(travel=2.0, lift=2.0, fire=False)
DEFAULTS = SimpleNamespace(move=0.2, action=0.3, ability=1.2, rt=0.1)

# preset -> [(keys, actuation mm, rapid-trigger step mm or None = off)]. Sources: docs/game-settings.md.
PRESETS = {
    "gaming": lambda a: [("wasd", a.move, a.rt), (["space", "lshift", "lctrl", "c"], a.action, a.rt),
                         (list("qerfgvzx12345"), a.ability, None)],
    # A/D hair-trigger for tap-strafe, W a bit deeper, fast jump + crouch for superglide, heals/abilities deep
    "apex": lambda a: [(["a", "d"], 0.2, 0.1), (["w", "s"], 0.4, 0.1), (["space"], 0.2, 0.1),
                       (["lshift"], 0.3, 0.1), (["lctrl", "c"], 0.4, 0.1), (list("123456qzr"), 2.0, None)],
    # NetEase's own Marvel Rivals guidance (relayed by Razer)
    "rivals": lambda a: [("wasd", 1.0, 0.2), (["space", "lctrl", "lshift"], 2.0, None)],
    # Wooting's current Valorant starting ranges: responsive movement, deliberate utility/jump keys.
    "valorant": lambda a: [("wasd", 0.3, 0.3), (["lshift"], 1.0, None), (["lctrl"], 0.7, None),
                           (["space"], 2.0, None), (list("cqe"), 1.5, None), (["x"], 2.2, None)],
}


def slots_for(kb, profile, names):
    """(slot, key name) for every physical key bound to one of `names` in this profile's keymap."""
    mat = kb.read_matrix(profile)
    want = {HID[n] for n in names}
    out = []
    for slot in range(len(mat) // 4):
        raw = bytes(mat[slot * 4:slot * 4 + 4])
        if raw != bytes(4):
            d = actions.decode(raw)
            if d.get("type") == "keyboard" and d.get("key") in want:
                out.append((slot, NAME[d["key"]]))
    return out


def apply(kb, profile, names, **patch):
    for slot, name in slots_for(kb, profile, names):
        for attempt in range(4):
            try:
                r = kb.set_magnetic(slot, dict(patch))   # re-plans from a fresh read, so a retry after a stale-read false alarm is a no-op
                break
            except ProtocolError as e:
                if "readback differs" not in str(e) or attempt == 3:
                    raise
                time.sleep(0.3)
        s = r["slot"]
        print(f"  {name:7} slot {slot:3}  travel {s['travel']}  rapid {'ON ' if s['fire'] else 'off'} "
              f"press {s['rapid_press']} lift {s['rapid_lift']}  {'(changed)' if r['changed'] else '(already)'}")


def dirty_keys(kb, state):
    """Key names whose travel/rapid-trigger differ from stock."""
    profile = state["profile"]
    return [nm for sl, nm in slots_for(kb, profile, list(HID))
            if state["slots"][sl]["mode"] is not None and any(state["slots"][sl][k] != v for k, v in RESET.items())]


def apply_preset(kb, name, a=DEFAULTS):
    """Reset keys the previous preset touched, then apply `name` ('reset' = just reset). Saves a backup first."""
    state = kb.get_magnetic()
    profile = state["profile"]
    print(f"active profile index {profile} (Profile {profile + 1} in the driver app)")
    backups = HERE / "backups"
    backups.mkdir(exist_ok=True)
    path = backups / f"profile{profile + 1}-{time.strftime('%Y%m%d-%H%M%S')}.json"
    path.write_text(json.dumps(state, indent=1), encoding="utf-8")
    print("backed up current magnetic state ->", path.name)
    dirty = dirty_keys(kb, state)
    if dirty:
        print("resetting", " ".join(dirty), "to stock first")
        apply(kb, profile, dirty, **RESET)
    if name == "reset":
        return
    for keys, act, rt in PRESETS[name](a):
        print(f"{act} mm, rapid trigger {'%.2f mm' % rt if rt else 'off'}:")
        patch = dict(travel=act, lift=act, fire=bool(rt))
        if rt:
            patch |= dict(rapid_press=rt, rapid_lift=rt)
        apply(kb, profile, keys, **patch)


def show(kb):
    state = kb.get_magnetic()
    profile = state["profile"]
    print(f"active profile index {profile} (Profile {profile + 1} in the driver app)")
    names = dict(slots_for(kb, profile, list(HID)))
    for s in state["slots"]:
        if s["mode"] is not None and (any(s[k] != v for k, v in RESET.items()) or s["mode"] != "normal"):   # mode None = unused padding slot
            print(f"  slot {s['slot']:3} {names.get(s['slot'], '?'):7} {json.dumps({k: s[k] for k in FIELDS} | {'mode': s['mode']})}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["show", "reset", *PRESETS])
    ap.add_argument("--move", type=float, default=DEFAULTS.move, help="'gaming': WASD actuation mm")
    ap.add_argument("--action", type=float, default=DEFAULTS.action, help="'gaming': space/shift/ctrl/c actuation mm")
    ap.add_argument("--ability", type=float, default=DEFAULTS.ability, help="'gaming': ability keys actuation mm")
    ap.add_argument("--rt", type=float, default=DEFAULTS.rt, help="'gaming': rapid-trigger press/release step mm")
    a = ap.parse_args()
    kb = winhid.open_keyboard()
    try:
        kb.identify()
        show(kb) if a.cmd == "show" else apply_preset(kb, a.cmd, a)
    finally:
        kb.transport.close()


if __name__ == "__main__":
    main()
