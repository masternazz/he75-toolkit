import queue
import unittest

from app import App


class Value:
    def __init__(self):
        self.value = None

    def set(self, value):
        self.value = value


class ProfileRefreshEventsTests(unittest.TestCase):
    def test_profile_refresh_event_is_rendered_on_ui_pump(self):
        """Changing lights must request card rendering through the UI event loop, not a HID worker."""
        class FakeApp:
            def __init__(self):
                self.q = queue.Queue()
                self.q.put(("profiles", ""))
                self.active_profile = Value()
                self.status = Value()
                self.rendered = 0

            def render_profiles(self):
                self.rendered += 1

            def pump(self):
                pass

            def after(self, _delay, _callback):
                pass

        fake = FakeApp()
        App.pump(fake)
        self.assertEqual(fake.rendered, 1)


if __name__ == "__main__":
    unittest.main()
