"""
Loopback OAuth callback capture (RFC 8252 native-application authorisation).

FreeAgent delivers the authorisation redirect to the browser, which would
leave the ``code`` stranded in the address bar for the user to copy and paste
back into the terminal.  This module instead runs a throwaway HTTP server on
127.0.0.1 before the authorisation URL is opened, so the redirect arrives
directly in the running process.  The ``state`` parameter is still verified
to prevent token substitution.

The app must be registered with the exact ``http://localhost:8080/callback``
redirect URI (the RFC 8252 loopback pattern; no certificates required).
Set ``OAUTH_PORT`` to override the port and register the matching URI.
"""

from __future__ import annotations

import errno
import http.server
import os
import threading
import urllib.parse

LOOPBACK_HOST = "127.0.0.1"
DEFAULT_PORT = 8080
DEFAULT_CALLBACK_PATH = "/callback"
DEFAULT_TIMEOUT = 300

_SUCCESS_PAGE = b"""<!doctype html><html><head><meta charset="utf-8">
<title>Authorization complete</title></head><body>
<p>Authorization complete. You can close this tab and return to the terminal.</p>
</body></html>"""

_ERROR_PAGE = b"""<!doctype html><html><head><meta charset="utf-8">
<title>Authorization failed</title></head><body>
<p>The authorization callback was rejected (missing code or state mismatch).
Try again.</p>
</body></html>"""


class _OAuthCallbackHandler(http.server.BaseHTTPRequestHandler):
    """Handle a single GET hit from the provider's browser redirect.

    The expected ``state`` and captured ``code`` live on the class so they
    survive per-request instantiation without extra server plumbing.
    """

    expected_state: str = ""
    code: str | None = None

    def do_GET(self) -> None:  # pylint: disable=invalid-name
        """Capture code/state query parameters and validate the state."""
        query = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code_parts = query.get("code")
        state_parts = query.get("state")
        code = code_parts[0] if code_parts else None
        state = state_parts[0] if state_parts else None
        if code and state == self.expected_state:
            self.__class__.code = code
            self._respond(200, _SUCCESS_PAGE)
            threading.Thread(
                target=self.server.shutdown, name="oauth-shutdown", daemon=True
            ).start()
        else:
            self._respond(400, _ERROR_PAGE)

    def _respond(self, status: int, body: bytes) -> None:
        """Send a minimal self-contained HTML response."""
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    # pylint: disable=redefined-builtin
    def log_message(self, format: str, *args: object) -> None:
        """Keep the console quiet; the calling code reports the outcome."""
        return


class _OAuthCallbackServer(http.server.HTTPServer):
    """Single-shot loopback server bound to 127.0.0.1 only."""

    def __init__(self, server_address: tuple[str, int], expected_state: str) -> None:
        super().__init__(server_address, _OAuthCallbackHandler)
        _OAuthCallbackHandler.expected_state = expected_state
        _OAuthCallbackHandler.code = None


def redirect_uri(port: int = DEFAULT_PORT, callback_path: str = "") -> str:
    """Return the redirect URI the provider must send the browser to.

    ``callback_path`` is appended to the root URL and, if it does not start
    with a slash, one is added (e.g. ``callback`` -> ``/callback``).
    """
    root = f"http://localhost:{port}"
    if not callback_path:
        return root
    if not callback_path.startswith("/"):
        callback_path = f"/{callback_path}"
    return f"{root}{callback_path}"


def receive_oauth_code(
    state: str,
    *,
    port: int | None = None,
    timeout: int = DEFAULT_TIMEOUT,
) -> str | None:
    """Wait for the OAuth redirect to arrive on the loopback server.

    Runs the callback server in a background thread and blocks until the
    provider's browser redirect delivers a ``code`` whose ``state`` matches.
    Returns the authorisation code, or ``None`` if nothing arrived within
    ``timeout`` seconds (or the loopback port was already in use).

    :raises RuntimeError: if the loopback port is already bound.
    """
    port = port or int(os.environ.get("OAUTH_PORT", str(DEFAULT_PORT)))
    try:
        server = _OAuthCallbackServer((LOOPBACK_HOST, port), state)
    except OSError as exc:
        if exc.errno == errno.EADDRINUSE:
            raise RuntimeError(
                f"Port {port} is already in use on 127.0.0.1 - stop the "
                "other listener, or set OAUTH_PORT to a free port."
            ) from exc
        raise
    thread = threading.Thread(
        target=server.serve_forever, name="oauth-callback", daemon=True
    )
    thread.start()
    try:
        thread.join(timeout)
    finally:
        server.shutdown()
        server.server_close()
    return _OAuthCallbackHandler.code
