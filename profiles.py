"""Persistent, hardware-independent profiles for the HE75 Toolkit."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
import copy
import json
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4


PROFILE_VERSION = 1


def normalize_exe(value: str) -> str:
    """Return the executable filename used for case-insensitive process matching."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError("executable name is required")
    return value.replace("\\", "/").rsplit("/", 1)[-1].casefold()


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

    @classmethod
    def new(cls, name: str, kind: Literal["desktop", "game"], *, executables: list[str] | None = None) -> "Profile":
        return cls(uuid4().hex, name, kind, executables or [])

    def __post_init__(self):
        if not isinstance(self.id, str) or not self.id:
            raise ValueError("profile id is required")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("profile name is required")
        if self.kind not in ("desktop", "game"):
            raise ValueError("profile kind must be desktop or game")
        if self.kind == "desktop" and self.executables:
            raise ValueError("desktop profile cannot have executable links")
        self.executables = list(dict.fromkeys(normalize_exe(value) for value in self.executables))

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> "Profile":
        expected = {"id", "name", "kind", "executables", "lighting", "hall", "advanced"}
        if set(value) != expected:
            raise ValueError("profile data has unexpected fields")
        return cls(**value)


def default_library() -> list[Profile]:
    desktop = Profile.desktop()
    desktop.hall = {"preset": "reset"}
    desktop.lighting = {
        "keys": {"mode": "solid", "rgb": 0x4B0082, "brightness": 2, "speed": 0},
        "bar": {"mode": "solid", "rgb": 0x4B0082, "brightness": 2, "speed": 0},
    }
    game_lighting = {
        "keys": {"mode": "ripple", "rgb": 0xFF0090, "brightness": 4, "speed": 3},
        "bar": {"mode": "wave", "rgb": 0x00F0FF, "brightness": 4, "speed": 2},
    }
    return [
        desktop,
        Profile("apex", "Apex Legends", "game", ["r5apex.exe", "r5apex_dx12.exe"], copy.deepcopy(game_lighting), {"preset": "apex"}),
        Profile("rivals", "Marvel Rivals", "game", ["marvel-win64-shipping.exe"], copy.deepcopy(game_lighting), {"preset": "rivals"}),
        Profile("valorant", "Valorant", "game", ["valorant-win64-shipping.exe"], copy.deepcopy(game_lighting), {"preset": "valorant"}),
        Profile("gaming", "Generic FPS", "game", [], copy.deepcopy(game_lighting), {"preset": "gaming"}),
    ]


class ProfileStore:
    """Load and atomically save a profile library at a caller-chosen path."""

    def __init__(self, path: Path | str):
        self.path = Path(path)

    def load(self) -> list[Profile]:
        if not self.path.exists():
            return default_library()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if set(raw) != {"version", "profiles"} or raw["version"] != PROFILE_VERSION:
                raise ValueError("unsupported profile library")
            profiles = [Profile.from_dict(value) for value in raw["profiles"]]
            if [profile.id for profile in profiles].count("desktop") != 1:
                raise ValueError("profile library must contain one desktop profile")
            return profiles
        except (OSError, ValueError, TypeError, json.JSONDecodeError):
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = self.path.with_name(f"{self.path.stem}.invalid-{stamp}{self.path.suffix}")
            self.path.replace(backup)
            return default_library()

    def save(self, profiles: list[Profile]) -> None:
        if [profile.id for profile in profiles].count("desktop") != 1:
            raise ValueError("profile library must contain one desktop profile")
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"version": PROFILE_VERSION, "profiles": [profile.to_dict() for profile in profiles]}
        temporary = self.path.with_name(f".{self.path.name}.tmp")
        temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        temporary.replace(self.path)
