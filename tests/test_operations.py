"""Profile previews and writes share one verified operations boundary."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from operations import VerificationError, apply_profile, preview
from profiles import Profile


class FakeTransport:
    def close(self):
        pass


class FakeKeyboard:
    def __init__(self, readback_matches):
        self.readback_matches = readback_matches
        self.transport = FakeTransport()

    def identify(self):
        return {"model": "HE75 V2"}

    def set_light(self, mode, *, rgb, brightness, speed, side):
        return {"mode": mode if self.readback_matches else "wave", "rgb": rgb if self.readback_matches else 0,
                "brightness": brightness, "speed": speed}


class OperationsTests(unittest.TestCase):
    def setUp(self):
        self.profile = Profile("apex", "Apex", "game", lighting={
            "keys": {"mode": "ripple", "rgb": 0xFF0090, "brightness": 4, "speed": 3},
        })

    def test_preview_lists_only_changed_lighting_section(self):
        """A preview that lists an unchanged section would make users approve misleading writes."""
        current = {"lighting": {"keys": {"mode": "wave", "rgb": 1, "brightness": 4, "speed": 3}}}

        self.assertEqual(preview(self.profile, current), [{
            "section": "lighting.keys", "from": current["lighting"]["keys"], "to": self.profile.lighting["keys"],
        }])

    def test_apply_rejects_mismatched_lighting_readback(self):
        """A device reply different from the requested profile must surface rather than claim an apply succeeded."""
        with self.assertRaises(VerificationError):
            apply_profile(self.profile, open_keyboard=lambda: FakeKeyboard(readback_matches=False))

    def test_apply_uses_saved_hall_preset_before_lighting(self):
        """Game profiles without their Hall preset would only change cosmetics when selected."""
        profile = Profile("apex", "Apex", "game", hall={"preset": "apex"})

        result = apply_profile(
            profile,
            open_keyboard=lambda: FakeKeyboard(readback_matches=True),
            apply_hall=lambda keyboard, preset: f"{preset} Hall-effect preset verified",
        )

        self.assertEqual(result.details, ["apex Hall-effect preset verified"])


if __name__ == "__main__":
    unittest.main()
