"""Switching rules that do not need a keyboard or a real Windows window."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from profiles import Profile
from switcher import ProcessSnapshot, SwitchState, resolve


class SwitcherTests(unittest.TestCase):
    def setUp(self):
        self.profiles = [
            Profile.desktop(),
            Profile("apex", "Apex", "game", ["r5apex.exe"]),
            Profile("valorant", "Valorant", "game", ["valorant-win64-shipping.exe"]),
        ]

    def test_foreground_mapped_game_wins_between_running_games(self):
        """A foreground-game priority regression would select the wrong profile while both games run."""
        result = resolve(
            ProcessSnapshot({"r5apex.exe", "valorant-win64-shipping.exe"}, "valorant-win64-shipping.exe"),
            self.profiles,
            SwitchState("desktop", None),
        )

        self.assertEqual(result.active_id, "valorant")
        self.assertEqual(result.last_game_id, "valorant")

    def test_alt_tab_to_unmapped_window_retains_running_game(self):
        """An unmapped foreground app must not switch a running game back to Desktop."""
        result = resolve(
            ProcessSnapshot({"r5apex.exe", "discord.exe"}, "discord.exe"),
            self.profiles,
            SwitchState("apex", "apex"),
        )

        self.assertEqual(result, SwitchState("apex", "apex"))

    def test_no_linked_processes_restores_desktop(self):
        """Leaving a game profile active after every linked game closes would break the work/lounge fallback."""
        result = resolve(
            ProcessSnapshot({"discord.exe"}, "discord.exe"),
            self.profiles,
            SwitchState("apex", "apex"),
        )

        self.assertEqual(result, SwitchState("desktop", None))


if __name__ == "__main__":
    unittest.main()
