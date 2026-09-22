"""Profile monitor behavior over deterministic process snapshots."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from autogame import ProfileMonitor
from profiles import Profile
from switcher import ProcessSnapshot


class ProfileMonitorTests(unittest.TestCase):
    def setUp(self):
        self.profiles = [Profile.desktop(), Profile("apex", "Apex", "game", ["r5apex.exe"])]
        self.applied = []
        self.monitor = ProfileMonitor(self.profiles, apply=self.applied.append)

    def test_monitor_applies_only_when_resolved_profile_changes(self):
        """Repeated polling or an alt-tab to Discord must not rewrite the board."""
        self.monitor.tick(ProcessSnapshot({"r5apex.exe"}, "r5apex.exe"))
        self.monitor.tick(ProcessSnapshot({"r5apex.exe", "discord.exe"}, "discord.exe"))

        self.assertEqual([profile.id for profile in self.applied], ["apex"])

    def test_monitor_applies_desktop_when_started_without_a_linked_game(self):
        """Turning on auto-switch must restore the work/lounge profile if no game is running."""
        self.monitor.tick(ProcessSnapshot({"discord.exe"}, "discord.exe"))

        self.assertEqual([profile.id for profile in self.applied], ["desktop"])


if __name__ == "__main__":
    unittest.main()
