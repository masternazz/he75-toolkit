"""Opt-in, token-authenticated profile API bound exclusively to localhost."""
from __future__ import annotations

import hmac
import json
import threading
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable

from profiles import ProfileStore


class LocalApi:
    """Serve read-only profile information to a trusted local integration."""

    def __init__(
        self,
        store: ProfileStore,
        *,
        status: Callable[[], dict[str, Any]],
        logs: Callable[[], list[dict[str, Any]]] | None = None,
        preview: Callable[[Any], list[dict[str, Any]]] | None = None,
        apply: Callable[[Any], Any] | None = None,
    ):
        self.store = store
        self.status = status
        self.logs = logs or (lambda: [])
        self.preview = preview or (lambda _profile: [])
        self.apply = apply
        self.server: ThreadingHTTPServer | None = None
        self.thread: threading.Thread | None = None

    def start(self, token: str) -> int:
        if self.server:
            return self.server.server_address[1]
        if not isinstance(token, str) or len(token) < 1:
            raise ValueError("a non-empty API token is required")

        api = self

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, _format, *_args):
                return

            def send_json(self, status: HTTPStatus, body: dict[str, Any]):
                encoded = json.dumps(body).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                self.wfile.write(encoded)

            def authorized(self) -> bool:
                expected = f"Bearer {self.server.token}"
                received = self.headers.get("Authorization", "")
                return hmac.compare_digest(received, expected)

            def do_GET(self):
                if not self.authorized():
                    self.send_json(HTTPStatus.UNAUTHORIZED, {"error": "bearer token required"})
                    return
                if self.path == "/v1/status":
                    self.send_json(HTTPStatus.OK, {"status": api.status()})
                    return
                if self.path == "/v1/profiles":
                    self.send_json(HTTPStatus.OK, {"profiles": [profile.to_dict() for profile in api.store.load()]})
                    return
                if self.path == "/v1/logs":
                    self.send_json(HTTPStatus.OK, {"logs": api.logs()})
                    return
                prefix = "/v1/profiles/"
                if self.path.startswith(prefix):
                    profile_id = self.path[len(prefix):]
                    profile = next((item for item in api.store.load() if item.id == profile_id), None)
                    if profile:
                        self.send_json(HTTPStatus.OK, profile.to_dict())
                    else:
                        self.send_json(HTTPStatus.NOT_FOUND, {"error": "profile not found"})
                    return
                self.send_json(HTTPStatus.NOT_FOUND, {"error": "route not found"})

            def body(self):
                try:
                    length = int(self.headers.get("Content-Length", "0"))
                    value = json.loads(self.rfile.read(length))
                except (ValueError, json.JSONDecodeError):
                    self.send_json(HTTPStatus.BAD_REQUEST, {"error": "body must be JSON"})
                    return None
                if not isinstance(value, dict):
                    self.send_json(HTTPStatus.BAD_REQUEST, {"error": "body must be a JSON object"})
                    return None
                return value

            def profile(self, profile_id):
                return next((item for item in api.store.load() if item.id == profile_id), None)

            def do_POST(self):
                if not self.authorized():
                    self.send_json(HTTPStatus.UNAUTHORIZED, {"error": "bearer token required"})
                    return
                body = self.body()
                if body is None:
                    return
                if self.path == "/v1/preview":
                    if set(body) != {"profile_id"} or not isinstance(body["profile_id"], str):
                        self.send_json(HTTPStatus.BAD_REQUEST, {"error": "preview requires only profile_id"})
                        return
                    profile = self.profile(body["profile_id"])
                    if not profile:
                        self.send_json(HTTPStatus.NOT_FOUND, {"error": "profile not found"})
                        return
                    self.send_json(HTTPStatus.OK, {"preview": api.preview(profile)})
                    return
                prefix = "/v1/apply/"
                if self.path.startswith(prefix):
                    if body != {"confirm": True}:
                        self.send_json(HTTPStatus.BAD_REQUEST, {"error": "apply requires confirm: true"})
                        return
                    profile = self.profile(self.path[len(prefix):])
                    if not profile:
                        self.send_json(HTTPStatus.NOT_FOUND, {"error": "profile not found"})
                        return
                    if not api.apply:
                        self.send_json(HTTPStatus.SERVICE_UNAVAILABLE, {"error": "profile writing is unavailable"})
                        return
                    api.apply(profile)
                    self.send_json(HTTPStatus.OK, {"applied": profile.id})
                    return
                self.send_json(HTTPStatus.NOT_FOUND, {"error": "route not found"})

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server.token = token
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        return self.server.server_address[1]

    def stop(self) -> None:
        if not self.server:
            return
        self.server.shutdown()
        self.server.server_close()
        if self.thread:
            self.thread.join(timeout=1)
        self.server = None
        self.thread = None
