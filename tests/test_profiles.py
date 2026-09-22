"""Behavior checks for the local HE75 profile library."""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from profiles import Profile, ProfileStore


class ProfileStoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "profiles.json"

    def tearDown(self):
        self.temp.cleanup()

    def test_missing_library_exposes_desktop_profile(self):
        """Removing the library must not leave the app without its work/lounge fallback."""
        profiles = ProfileStore(self.path).load()

        self.assertEqual([(profile.name, profile.kind) for profile in profiles], [("Desktop", "desktop")])

    def test_round_trip_normalizes_executable_names(self):
        """Process matching would break if saved executable case survived a reload."""
        store = ProfileStore(self.path)
        apex = Profile.new("Apex", "game", executables=["R5APEX.EXE"])

        store.save([Profile.desktop(), apex])

        loaded = store.load()
        self.assertEqual(loaded[1].executables, ["r5apex.exe"])


if __name__ == "__main__":
    unittest.main()
