"""Behavior checks for the local HE75 profile library."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from profiles import Profile, ProfileStore, default_library


class ProfileStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "profiles.json"

    def tearDown(self):
        self.temp.cleanup()

    def test_missing_library_exposes_desktop_profile(self):
        """First launch must offer the existing game presets plus a work/lounge fallback."""
        profiles = ProfileStore(self.path).load()

        self.assertEqual(
            [(profile.name, profile.kind) for profile in profiles],
            [("Desktop", "desktop"), ("Apex Legends", "game"), ("Marvel Rivals", "game"),
             ("Valorant", "game"), ("Generic FPS", "game")],
        )
        self.assertEqual(profiles[3].executables, ["valorant-win64-shipping.exe"])

    def test_round_trip_normalizes_executable_names(self):
        """Process matching would break if saved executable case survived a reload."""
        store = ProfileStore(self.path)
        apex = Profile.new("Apex", "game", executables=["R5APEX.EXE"])

        store.save([Profile.desktop(), apex])

        loaded = store.load()
        self.assertEqual(loaded[1].executables, ["r5apex.exe"])

    def test_builtin_game_lighting_is_independent_per_profile(self):
        """Editing Apex lighting must not silently rewrite the default Valorant profile."""
        profiles = default_library()
        apex = next(profile for profile in profiles if profile.id == "apex")
        valorant = next(profile for profile in profiles if profile.id == "valorant")

        apex.lighting["keys"]["brightness"] = 1

        self.assertEqual(valorant.lighting["keys"]["brightness"], 4)


if __name__ == "__main__":
    unittest.main()
