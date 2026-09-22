"""HE75 Toolkit: a small window for the EPOMAKER HE75 V2 (no driver app needed).

  python app.py          (pythonw app.py  = no console window)

Game presets (actuation + Rapid Trigger), lighting for the keys and the top light bar, and an
"auto-switch when a game starts" toggle. Close the official EPOMAKER driver app first.
"""
import os, queue, sys, threading, tkinter as tk
from pathlib import Path
from tkinter import colorchooser, filedialog, messagebox, simpledialog, ttk

import autogame, hall, operations, winhid
from epomaker_driver import codec
from local_api import ApiTokenStore, LocalApi
from profiles import Profile, ProfileStore, normalize_exe
from switcher import running_executables

KEY_MODES = [m for m in codec.LIGHT_MODES if m not in ("off", "picture", "screen", "music")]
BAR_MODES = ["off", "solid", "neon", "wave"]
GAME_BUTTONS = [("Apex Legends", "apex"), ("Marvel Rivals", "rivals"), ("Valorant", "valorant"),
                ("Generic FPS", "gaming"), ("Reset to stock", "reset")]
LOOKS = {   # one-click lighting looks: (key mode, key colour, key speed, bar mode, bar colour, bar speed)
    "Cyberpunk": ("ripple", "#FF0090", 3, "wave", "#00F0FF", 2),
    "Dark purple": ("ripple", "#4B0082", 3, "solid", "#4B0082", 0),
}


def profile_library_path():
    root = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "HE75 Toolkit"
    return root / "profiles.json"


def api_settings_path():
    return profile_library_path().with_name("local-api.json")


class LogWriter:
    """Replaces sys.stdout so prints from any worker thread land in the log box."""
    def __init__(self, q): self.q = q
    def write(self, s): self.q.put(s)
    def flush(self): pass


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HE75 Toolkit")
        self.geometry("760x640")
        self.minsize(640, 540)
        self.q = queue.Queue()
        sys.stdout = LogWriter(self.q)
        self.buttons, self.stop, self.watcher = [], threading.Event(), None
        self.colors = {"keys": "#8A2BE2", "bar": "#00F0FF"}
        self.light = {}   # side -> dict of tk vars
        self.status = tk.StringVar(value="Looking for the keyboard...")
        self.busy_text = tk.StringVar()
        self.store = ProfileStore(profile_library_path())
        self.profiles = self.store.load()
        self.selected_profile_id = self.profiles[0].id
        self.active_profile = tk.StringVar(value="Desktop profile ready")
        self.monitor = None
        self.api_state = {"active_profile": "desktop", "keyboard": "unknown"}
        self.api_token_store = ApiTokenStore(api_settings_path())
        self.api_token = self.api_token_store.load_or_create()
        self.api = LocalApi(self.store, status=self.api_status, preview=self.api_preview, apply=self.apply_saved_profile)

        ttk.Label(self, textvariable=self.status, font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(10, 0))
        ttk.Label(self, textvariable=self.busy_text, foreground="#b45309").pack(anchor="w", padx=12)

        dashboard = ttk.LabelFrame(self, text="Profiles")
        dashboard.pack(fill="x", padx=12, pady=8)
        header = ttk.Frame(dashboard)
        header.pack(fill="x", padx=8, pady=(6, 0))
        ttk.Label(header, textvariable=self.active_profile, font=("Segoe UI", 10, "bold")).pack(side="left")
        ttk.Button(header, text="+ Add profile", command=self.add_profile).pack(side="right")
        self.profile_cards = ttk.Frame(dashboard)
        self.profile_cards.pack(fill="x", padx=8, pady=8)
        self.render_profiles()

        games = ttk.LabelFrame(self, text="Quick apply (applied to the active onboard profile, ~2 min each)")
        games.pack(fill="x", padx=12, pady=8)
        for label, preset in GAME_BUTTONS:
            b = ttk.Button(games, text=label, command=lambda p=preset: self.apply_profile_id("desktop" if p == "reset" else p))
            b.pack(side="left", padx=6, pady=8)
            self.buttons.append(b)
        b = ttk.Button(games, text="Show key settings", command=lambda: self.bg(self.show_keys, "Reading..."))
        b.pack(side="right", padx=6)
        self.buttons.append(b)

        lighting = ttk.LabelFrame(self, text="Lighting")
        lighting.pack(fill="x", padx=12, pady=4)
        for i, (title, side, modes, mode, speed) in enumerate([("Keys", False, KEY_MODES, "ripple", 3),
                                                              ("Light bar", True, BAR_MODES, "wave", 2)]):
            self.light_row(lighting, i, title, side, modes, mode, speed)
        looks = ttk.Frame(lighting)
        looks.grid(row=2, column=0, columnspan=8, sticky="w", padx=6, pady=(0, 8))
        ttk.Label(looks, text="One-click looks:").pack(side="left")
        for name, look in LOOKS.items():
            b = ttk.Button(looks, text=name, command=lambda l=look: self.apply_look(l))
            b.pack(side="left", padx=6)
            self.buttons.append(b)

        auto = ttk.LabelFrame(self, text="Per-game auto-switch")
        auto.pack(fill="x", padx=12, pady=8)
        self.auto = tk.BooleanVar()
        self.idle = tk.StringVar(value="reset")
        ttk.Checkbutton(auto, text="Switch settings when a game starts, restore when it closes", variable=self.auto,
                        command=self.toggle_auto).pack(side="left", padx=6, pady=8)
        ttk.Label(auto, text="when idle:").pack(side="left", padx=(12, 2))
        ttk.Combobox(auto, textvariable=self.idle, values=["reset", "gaming"], width=8, state="readonly").pack(side="left")
        ttk.Label(auto, text="watching: " + ", ".join(sorted(set(autogame.GAMES.values()))), foreground="#666").pack(side="right", padx=8)

        integration = ttk.LabelFrame(self, text="Local AI / debug integration")
        integration.pack(fill="x", padx=12, pady=(0, 8))
        self.api_enabled = tk.BooleanVar()
        self.api_endpoint = tk.StringVar(value="Disabled — listens on this PC only")
        ttk.Checkbutton(integration, text="Enable local API", variable=self.api_enabled,
                        command=self.toggle_api).pack(side="left", padx=6, pady=8)
        ttk.Label(integration, textvariable=self.api_endpoint, foreground="#666").pack(side="left", padx=8)
        ttk.Button(integration, text="Copy token", command=self.copy_api_token).pack(side="right", padx=(2, 6))
        ttk.Button(integration, text="Regenerate token", command=self.regenerate_api_token).pack(side="right", padx=4)

        self.log = tk.Text(self, height=12, state="disabled", wrap="word", font=("Consolas", 9))
        self.log.pack(fill="both", expand=True, padx=12, pady=(4, 12))
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.after(100, self.pump)
        self.bg(self.identify, "Connecting...")

    # ---- profile dashboard
    def selected_profile(self):
        return next(profile for profile in self.profiles if profile.id == self.selected_profile_id)

    def render_profiles(self):
        for child in self.profile_cards.winfo_children():
            child.destroy()
        for index, profile in enumerate(self.profiles):
            card = ttk.LabelFrame(self.profile_cards, text=profile.name)
            card.grid(row=0, column=index, padx=(0, 8), pady=2, sticky="nsew")
            linked = ", ".join(profile.executables) if profile.executables else "No linked apps"
            ttk.Label(card, text=linked, foreground="#666", wraplength=145).pack(anchor="w", padx=8, pady=(5, 2))
            preset = profile.hall.get("preset", "custom")
            ttk.Label(card, text=f"Keys: {preset}").pack(anchor="w", padx=8)
            actions = ttk.Frame(card)
            actions.pack(fill="x", padx=8, pady=6)
            ttk.Button(actions, text="Select", command=lambda p=profile: self.select_profile(p.id)).pack(side="left")
            ttk.Button(actions, text="Apply", command=lambda p=profile: self.apply_profile_id(p.id)).pack(side="left", padx=4)
            if profile.kind == "game":
                ttk.Button(actions, text="+ App", command=lambda p=profile: self.add_app(p.id)).pack(side="left")

    def select_profile(self, profile_id):
        self.selected_profile_id = profile_id
        profile = self.selected_profile()
        self.active_profile.set(f"Selected: {profile.name}")

    def add_profile(self):
        name = simpledialog.askstring("Add profile", "Profile name:", parent=self)
        if not name:
            return
        profile = Profile.new(name.strip(), "game")
        self.profiles.append(profile)
        self.store.save(self.profiles)
        self.select_profile(profile.id)
        self.render_profiles()

    def add_app(self, profile_id):
        profile = next(profile for profile in self.profiles if profile.id == profile_id)
        dialog = tk.Toplevel(self)
        dialog.title(f"Link app to {profile.name}")
        dialog.transient(self)
        dialog.grab_set()
        ttk.Label(dialog, text="Running apps").pack(anchor="w", padx=12, pady=(12, 2))
        apps = tk.Listbox(dialog, width=52, height=12)
        apps.pack(fill="both", expand=True, padx=12, pady=4)
        for executable in sorted(running_executables()):
            apps.insert("end", executable)

        def save_executable(value):
            if not value:
                return
            executable = normalize_exe(value)
            if executable not in profile.executables:
                profile.executables.append(executable)
                self.store.save(self.profiles)
                self.render_profiles()
            dialog.destroy()

        actions = ttk.Frame(dialog)
        actions.pack(fill="x", padx=12, pady=(2, 12))
        ttk.Button(actions, text="Link selected", command=lambda: save_executable(
            apps.get(apps.curselection()[0]) if apps.curselection() else None
        )).pack(side="left")
        ttk.Button(actions, text="Browse for .exe", command=lambda: save_executable(
            filedialog.askopenfilename(parent=dialog, title="Choose a game executable", filetypes=[("Programs", "*.exe")])
        )).pack(side="left", padx=6)
        ttk.Button(actions, text="Cancel", command=dialog.destroy).pack(side="right")

    def apply_profile_id(self, profile_id):
        profile = next(profile for profile in self.profiles if profile.id == profile_id)
        self.bg(lambda: self.apply_saved_profile(profile), f"Applying {profile.name}...")

    def apply_saved_profile(self, profile):
        result = operations.apply_profile(profile)
        self.api_state["active_profile"] = profile.id
        self.q.put(("status", f"{profile.name} applied and verified"))
        self.q.put(("active", profile.name))
        print("; ".join(result.details) or f"{profile.name}: no board changes")

    def api_status(self):
        return dict(self.api_state)

    def api_preview(self, profile):
        changes = []
        if profile.hall:
            changes.append({"section": "hall", "to": profile.hall})
        return changes + operations.preview(profile, {"lighting": {}})

    def toggle_api(self):
        if self.api_enabled.get():
            port = self.api.start(self.api_token)
            self.api_endpoint.set(f"http://127.0.0.1:{port}/v1")
            print("local API enabled (loopback only; token not logged)")
        else:
            self.api.stop()
            self.api_endpoint.set("Disabled — listens on this PC only")
            print("local API disabled")

    def copy_api_token(self):
        self.clipboard_clear()
        self.clipboard_append(self.api_token)
        self.status.set("Local API token copied to clipboard")

    def regenerate_api_token(self):
        if not messagebox.askyesno("Regenerate local API token", "Existing local integrations will stop working. Continue?", parent=self):
            return
        running = self.api_enabled.get()
        if running:
            self.api.stop()
        self.api_token = self.api_token_store.regenerate()
        if running:
            port = self.api.start(self.api_token)
            self.api_endpoint.set(f"http://127.0.0.1:{port}/v1")
        self.status.set("Local API token regenerated")

    # ---- layout helpers
    def light_row(self, parent, row, title, side, modes, mode, speed):
        v = dict(mode=tk.StringVar(value=mode), bri=tk.IntVar(value=4), speed=tk.IntVar(value=speed))
        self.light[side] = v
        ttk.Label(parent, text=title, width=9).grid(row=row, column=0, padx=6, pady=6, sticky="w")
        ttk.Combobox(parent, textvariable=v["mode"], values=modes, width=12, state="readonly").grid(row=row, column=1, padx=4)
        key = "bar" if side else "keys"
        v["swatch"] = tk.Button(parent, width=4, bg=self.colors[key], relief="flat", command=lambda: self.pick(key, v["swatch"]))
        v["swatch"].grid(row=row, column=2, padx=6)
        for col, (label, name) in enumerate([("Brightness", "bri"), ("Speed", "speed")]):
            ttk.Label(parent, text=label).grid(row=row, column=3 + col * 2, padx=(10, 2))
            ttk.Scale(parent, from_=0, to=4, variable=v[name], length=90,
                      command=lambda x, var=v[name]: var.set(round(float(x)))).grid(row=row, column=4 + col * 2)
        b = ttk.Button(parent, text="Apply", command=lambda: self.bg(lambda: self.set_light(side), "Setting lights..."))
        b.grid(row=row, column=7, padx=8)
        self.buttons.append(b)

    def pick(self, key, swatch):
        c = colorchooser.askcolor(color=self.colors[key], title="Pick a colour")[1]
        if c:
            self.colors[key] = c
            swatch.configure(bg=c)

    # ---- device actions (run on worker threads; one HID handle at a time)
    def set_light(self, side, mode=None, color=None, speed=None):
        v = self.light[side]
        mode = mode or v["mode"].get()
        rgb = int((color or self.colors["bar" if side else "keys"]).lstrip("#"), 16)
        speed = v["speed"].get() if speed is None else speed
        if mode == "neon":
            rgb = 0xFFFFFF   # firmware fixes neon's colours
        if mode in ("off", "solid"):
            speed = 0
        bri = 4 if mode == "off" else v["bri"].get()
        with operations.DEVICE_LOCK:
            kb = winhid.open_keyboard()
            try:
                kb.identify()
                r = kb.set_light(mode, rgb=rgb, brightness=bri, speed=speed, side=side)
            finally:
                kb.transport.close()
        profile = self.selected_profile()
        profile.lighting["bar" if side else "keys"] = {
            "mode": r["mode"], "rgb": r["rgb"], "brightness": r["brightness"], "speed": r["speed"],
        }
        self.store.save(self.profiles)
        self.q.put(("profiles", ""))
        print(f"{'light bar' if side else 'keys'}: {r['mode']} #{r['rgb']:06X} speed {r['speed']} brightness {r['brightness']} (verified)")

    def apply_look(self, look):
        km, kc, ks, bm, bc, bs = look
        for side, mode, color, speed in ((False, km, kc, ks), (True, bm, bc, bs)):
            v = self.light[side]
            v["mode"].set(mode); v["speed"].set(speed)
            key = "bar" if side else "keys"
            self.colors[key] = color; v["swatch"].configure(bg=color)
        self.bg(lambda: (self.set_light(False, km, kc, ks), self.set_light(True, bm, bc, bs)), "Setting lights...")

    def identify(self):
        try:
            with autogame.DEVICE_LOCK:
                kb = winhid.open_keyboard()
                try:
                    info = kb.identify()
                finally:
                    kb.transport.close()
            self.api_state["keyboard"] = "connected"
            self.q.put(("status", f"{info['model']} connected (firmware {info['usb_version']:#06x})"))
        except Exception as e:
            self.api_state["keyboard"] = "not found"
            self.q.put(("status", "Keyboard not found. Plug it in by USB and close the EPOMAKER driver app."))
            print(f"{type(e).__name__}: {e}")

    def show_keys(self):
        with autogame.DEVICE_LOCK:
            kb = winhid.open_keyboard()
            try:
                kb.identify()
                hall.show(kb)
            finally:
                kb.transport.close()

    # ---- plumbing
    def bg(self, fn, label):
        def run():
            self.q.put(("busy", label))   # workers never touch Tk directly; the main thread's pump() applies these
            try:
                fn()
            except Exception as e:
                print(f"ERROR: {type(e).__name__}: {e}")
            finally:
                self.q.put(("busy", ""))
        threading.Thread(target=run, daemon=True).start()

    def set_busy(self, text):
        self.busy_text.set(text)
        for b in self.buttons:
            b.configure(state="disabled" if text else "normal")

    def toggle_auto(self):
        if self.auto.get():
            self.stop = threading.Event()
            self.monitor = autogame.ProfileMonitor(self.profiles, apply=self.apply_saved_profile)
            self.watcher = threading.Thread(target=self.watch_profiles, daemon=True)
            self.watcher.start()
            print("auto-switch ON: watching linked profile apps")
        else:
            self.stop.set()
            print("auto-switch OFF")

    def watch_profiles(self):
        while not self.stop.is_set():
            try:
                self.monitor.tick()
            except Exception as error:
                print(f"AUTO-SWITCH ERROR: {type(error).__name__}: {error}")
            self.stop.wait(2)

    def pump(self):
        try:
            while True:
                s = self.q.get_nowait()
                if isinstance(s, tuple):
                    kind, text = s
                    if kind == "busy":
                        self.set_busy(text)
                    elif kind == "active":
                        self.active_profile.set(f"Active: {text}")
                    elif kind == "profiles":
                        self.render_profiles()
                    else:
                        self.status.set(text)
                    continue
                self.log.configure(state="normal")
                self.log.insert("end", s)
                self.log.see("end")
                self.log.configure(state="disabled")
        except queue.Empty:
            pass
        self.after(100, self.pump)

    def close(self):
        self.stop.set()
        self.api.stop()
        self.destroy()


if __name__ == "__main__":
    App().mainloop()
