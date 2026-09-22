import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from local_api import ApiTokenStore, LocalApi
from profiles import Profile, ProfileStore


def request(port, method, path, token=None, body=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    data = json.dumps(body).encode("utf-8") if body is not None else None
    if data:
        headers["Content-Type"] = "application/json"
    return urlopen(Request(f"http://127.0.0.1:{port}{path}", data=data, method=method, headers=headers), timeout=1)


class LocalApiReadTests(unittest.TestCase):
    def setUp(self):
        self.temp = TemporaryDirectory()
        self.store = ProfileStore(Path(self.temp.name) / "profiles.json")
        self.store.save([Profile.desktop(), Profile("apex", "Apex", "game", ["r5apex.exe"])])
        self.calls = []
        self.api = LocalApi(
            self.store,
            status=lambda: {"connected": True},
            preview=lambda profile: [{"profile": profile.id, "changes": ["lighting"]}],
            apply=lambda profile: self.calls.append(profile.id),
        )
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

    def test_apply_without_confirm_is_rejected_without_writer_call(self):
        """A local client must explicitly confirm before it can change the keyboard."""
        with self.assertRaises(HTTPError) as raised:
            request(self.port, "POST", "/v1/apply/apex", "test-token", {"confirm": False})

        self.assertEqual(raised.exception.code, 400)
        raised.exception.close()
        self.assertEqual(self.calls, [])

    def test_preview_never_calls_writer(self):
        """Previewing a profile must remain read-only even with valid credentials."""
        with request(self.port, "POST", "/v1/preview", "test-token", {"profile_id": "apex"}) as response:
            preview = json.load(response)

        self.assertEqual(preview["preview"], [{"profile": "apex", "changes": ["lighting"]}])
        self.assertEqual(self.calls, [])


class ApiTokenStoreTests(unittest.TestCase):
    def test_token_is_persistent_until_explicitly_regenerated(self):
        """Restarting the app must not strand a local integration with a surprise new token."""
        with TemporaryDirectory() as folder:
            tokens = ApiTokenStore(Path(folder) / "api.json")
            first = tokens.load_or_create()
            same = tokens.load_or_create()
            replacement = tokens.regenerate()

        self.assertEqual(first, same)
        self.assertNotEqual(first, replacement)
        self.assertGreaterEqual(len(first), 32)

if __name__ == "__main__":
    unittest.main()
