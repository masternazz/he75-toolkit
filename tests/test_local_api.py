import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from local_api import LocalApi
from profiles import Profile, ProfileStore


def request(port, method, path, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return urlopen(Request(f"http://127.0.0.1:{port}{path}", method=method, headers=headers), timeout=1)


class LocalApiReadTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.store = ProfileStore(Path(self.temp.name) / "profiles.json")
        self.store.save([Profile.desktop(), Profile("apex", "Apex", "game", ["r5apex.exe"])])
        self.api = LocalApi(self.store, status=lambda: {"connected": True})
        self.port = self.api.start("test-token")

    def tearDown(self):
        self.api.stop()
        self.temp.cleanup()

    def test_server_binds_loopback_and_rejects_missing_bearer_token(self):
        """A missing token must not expose local profile data to another local process."""
        with self.assertRaises(HTTPError) as raised:
            request(self.port, "GET", "/v1/status")

        self.assertEqual(raised.exception.code, 401)
        raised.exception.close()
        self.assertEqual(self.api.server.server_address[0], "127.0.0.1")

    def test_authorized_profile_routes_return_saved_library(self):
        """An authorized integration should receive profile data without device access."""
        with request(self.port, "GET", "/v1/profiles", "test-token") as response:
            library = json.load(response)
        with request(self.port, "GET", "/v1/profiles/apex", "test-token") as response:
            apex = json.load(response)

        self.assertEqual([profile["id"] for profile in library["profiles"]], ["desktop", "apex"])
        self.assertEqual(apex["name"], "Apex")


if __name__ == "__main__":
    unittest.main()
