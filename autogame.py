"""Auto-apply a hall.py preset when a game starts, and restore an idle preset when it exits.

  python autogame.py                                   # watch until Ctrl+C
  python autogame.py --idle gaming                     # what to restore when no game runs (default: reset = stock)
  python autogame.py --map notepad.exe=apex --once     # test with a fake game: apply, wait for exit, restore

Polls the process list every few seconds (no hooks, no injection). The EPOMAKER driver app must stay closed.
Applying a preset takes ~2 minutes (every key is written then verified), so it happens while the game loads.
"""
import argparse, csv, io, subprocess, sys, threading, time

import hall, winhid

GAMES = {   # process name (lowercase) -> preset. Check Task Manager > Details for yours; add more with --map.
    "r5apex.exe": "apex", "r5apex_dx12.exe": "apex",
    "marvel-win64-shipping.exe": "rivals",
    "valorant-win64-shipping.exe": "valorant",
}
DEVICE_LOCK = threading.Lock()   # one HID handle at a time (the GUI shares this)


def running():
    out = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True,
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0)).stdout
    return {row[0].lower() for row in csv.reader(io.StringIO(out)) if row}


def apply_preset(preset):
    with DEVICE_LOCK:
        kb = winhid.open_keyboard()
        try:
            kb.identify()
            hall.apply_preset(kb, preset)
        finally:
            kb.transport.close()


def watch(idle="reset", games=GAMES, interval=5.0, stop=None, once=False, log=print):
    """Blocks; applies the preset for whichever game is running, `idle` otherwise. `stop` is a threading.Event."""
    current, had_game = idle, False   # assume the board starts idle; only act on changes
    stop = stop or threading.Event()
    while not stop.is_set():
        procs = running()
        want = next((games[p] for p in games if p in procs), idle)
        if want != current:
            log(f"{time.strftime('%H:%M:%S')} -> {want}")
            try:
                apply_preset(want)
                current = want
            except Exception as e:   # driver app open, cable out, ... keep watching and retry next tick
                log(f"  FAILED: {type(e).__name__}: {e}")
        had_game |= current != idle
        if once and had_game and current == idle:
            return
        stop.wait(interval)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--idle", default="reset", help="preset when no game is running (reset, gaming, ...)")
    ap.add_argument("--map", action="append", default=[], metavar="EXE=PRESET", help="extra process=preset")
    ap.add_argument("--interval", type=float, default=5)
    ap.add_argument("--once", action="store_true", help="exit after the first game closes (for testing)")
    a = ap.parse_args()
    games = GAMES | {k.lower(): v for k, v in (m.split("=") for m in a.map)}
    try:
        watch(a.idle, games, a.interval, once=a.once, log=lambda m: print(m, flush=True))
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
