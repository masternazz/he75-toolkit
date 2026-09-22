"""Packet checks against bytes captured from the official app. No keyboard needed."""
import os, sys, unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "vendor"))
from epomaker_driver import codec


class Packets(unittest.TestCase):
    def test_ripple_purple_matches_captured_packet(self):
        # captured from EPOMAKER Driver v4 while selecting Ripple, colour #8A2BE2, speed 4, brightness 4
        pkt = codec.light("ripple", rgb=0x8A2BE2, brightness=4, speed=4)
        self.assertEqual(pkt[:9].hex(), "0705000407" "8a2be2" "51")
        self.assertEqual(len(pkt), 64)
        self.assertEqual(pkt[9:], bytes(55))

    def test_light_checksum_is_ff_minus_sum_at_byte_8(self):
        for mode in ("wave", "reactive", "meteor"):
            pkt = codec.light(mode, rgb=0x123456, brightness=3, speed=2)
            self.assertEqual(pkt[8], 0xFF - (sum(pkt[:8]) & 0xFF))

    def test_query_checksum_is_at_byte_7(self):
        pkt = codec.packet([0x87])
        self.assertEqual(pkt[7], 0x78)   # 0xFF - 0x87
        self.assertEqual(pkt[8], 0)

    def test_side_light_speed_is_not_inverted_but_key_speed_is(self):
        key = codec.light("wave", rgb=0x00F0FF, brightness=4, speed=2)
        bar = codec.light("wave", rgb=0x00F0FF, brightness=4, speed=2, side=True, side_speed_max=4)
        self.assertEqual((key[0], key[2]), (0x07, 4 - 2))
        self.assertEqual((bar[0], bar[2]), (0x08, 2))

    def test_pure_white_is_sent_as_faffa(self):
        self.assertEqual(codec.light("solid", rgb=0xFFFFFF)[5:8].hex(), "fafffa")


if __name__ == "__main__":
    unittest.main()
