"""Pure profile-selection rules plus a Windows process/window snapshot."""
from __future__ import annotations

from dataclasses import dataclass
import csv
import ctypes
import io
from pathlib import Path
import subprocess
from typing import Sequence

from profiles import Profile, normalize_exe


@dataclass(frozen=True)
class ProcessSnapshot:
    running: frozenset[str]
    foreground: str | None

    def __init__(self, running: set[str] | frozenset[str], foreground: str | None):
        object.__setattr__(self, "running", frozenset(normalize_exe(name) for name in running))
        object.__setattr__(self, "foreground", normalize_exe(foreground) if foreground else None)


@dataclass(frozen=True)
class SwitchState:
    active_id: str
    last_game_id: str | None


def resolve(snapshot: ProcessSnapshot, profiles: Sequence[Profile], state: SwitchState) -> SwitchState:
    """Choose the focused mapped game, preserve a running game, or restore Desktop."""
    desktop = next((profile for profile in profiles if profile.kind == "desktop"), None)
    if desktop is None:
        raise ValueError("profile library needs a desktop profile")
    games = [profile for profile in profiles if profile.kind == "game"]
    by_executable = {exe: profile for profile in games for exe in profile.executables}

    foreground = by_executable.get(snapshot.foreground)
    if foreground:
        return SwitchState(foreground.id, foreground.id)

    prior = next((profile for profile in games if profile.id == state.last_game_id), None)
    if prior and set(prior.executables) & snapshot.running:
        return state

    running_game = next((profile for profile in games if set(profile.executables) & snapshot.running), None)
    if running_game:
        return SwitchState(running_game.id, running_game.id)
    return SwitchState(desktop.id, None)


def running_executables() -> set[str]:
    """Return the current Windows process image names without injecting into any process."""
    output = subprocess.run(
        ["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0), check=False,
    ).stdout
    return {normalize_exe(row[0]) for row in csv.reader(io.StringIO(output)) if row}


def foreground_executable() -> str | None:
    """Resolve the foreground window's executable name, returning None when unavailable."""
    user32, kernel32 = ctypes.windll.user32, ctypes.windll.kernel32
    window = user32.GetForegroundWindow()
    if not window:
        return None
    process_id = ctypes.c_ulong()
    user32.GetWindowThreadProcessId(window, ctypes.byref(process_id))
    handle = kernel32.OpenProcess(0x1000, False, process_id.value)  # PROCESS_QUERY_LIMITED_INFORMATION
    if not handle:
        return None
    try:
        size = ctypes.c_ulong(32768)
        buffer = ctypes.create_unicode_buffer(size.value)
        if not kernel32.QueryFullProcessImageNameW(handle, 0, buffer, ctypes.byref(size)):
            return None
        return Path(buffer.value).name
    finally:
        kernel32.CloseHandle(handle)


def snapshot_windows() -> ProcessSnapshot:
    return ProcessSnapshot(running_executables(), foreground_executable())
