"""Validated profile previews and the single serialized board-write boundary."""
from __future__ import annotations

from dataclasses import dataclass
import threading
from typing import Any, Callable

import winhid
import hall
from profiles import Profile


DEVICE_LOCK = threading.Lock()


class VerificationError(RuntimeError):
    """The keyboard's readback did not match a requested profile change."""


@dataclass(frozen=True)
class ApplyResult:
    profile_id: str
    changed: bool
    verified: bool
    details: list[str]


def preview(profile: Profile, current: dict[str, Any]) -> list[dict[str, Any]]:
    """Describe profile sections that differ, without opening the keyboard."""
    changes = []
    current_lighting = current.get("lighting", {})
    for zone, target in profile.lighting.items():
        before = current_lighting.get(zone)
        if before != target:
            changes.append({"section": f"lighting.{zone}", "from": before, "to": target})
    return changes


def _write_lighting(keyboard: Any, zone: str, target: dict[str, Any]) -> str:
    side = zone == "bar"
    result = keyboard.set_light(
        target["mode"], rgb=target["rgb"], brightness=target["brightness"], speed=target["speed"], side=side,
    )
    expected = {name: target[name] for name in ("mode", "rgb", "brightness", "speed")}
    actual = {name: result.get(name) for name in expected}
    if actual != expected:
        raise VerificationError(f"{zone} lighting readback differs: expected {expected}, got {actual}")
    return f"{zone} lighting verified"


def _apply_hall_preset(keyboard: Any, preset: str) -> str:
    if preset not in (*hall.PRESETS, "reset"):
        raise ValueError(f"unknown Hall-effect preset: {preset}")
    hall.apply_preset(keyboard, preset)
    return f"{preset} Hall-effect preset verified"


def apply_profile(
    profile: Profile, *, open_keyboard: Callable[[], Any] = winhid.open_keyboard,
    apply_hall: Callable[[Any, str], str] = _apply_hall_preset,
) -> ApplyResult:
    """Apply profile sections supported today and reject any failed readback."""
    details: list[str] = []
    with DEVICE_LOCK:
        keyboard = open_keyboard()
        try:
            keyboard.identify()
            preset = profile.hall.get("preset")
            if preset:
                details.append(apply_hall(keyboard, preset))
            for zone, target in profile.lighting.items():
                if zone not in ("keys", "bar"):
                    raise ValueError(f"unknown lighting zone: {zone}")
                details.append(_write_lighting(keyboard, zone, target))
        finally:
            keyboard.transport.close()
    return ApplyResult(profile.id, bool(details), True, details)
