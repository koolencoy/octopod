#!/usr/bin/env python3
"""Stub for the DX UIM probe config API described in dxuim-config/guide.md.

Emulates just enough of:
    PUT /uimapi/probes/{domain}/{hub}/{robot}/{probe}/config

...to let ansible/roles/dxuim_config_sync run against something real
instead of a live UAT/PROD UIM instance. Standard library only — no
pip install needed, matches ansible.roles.dxuim_config_sync/tasks/
post_to_dxuim.yml's actual request shape (basic auth, JSON array body).

Not a security boundary — the auth check exists only to catch wiring
mistakes (wrong username, missing header), not to protect anything.

Usage:
    python3 dxuim_stub_server.py [--host 127.0.0.1] [--port 8443] [--user accountsvcid] [--password devpass]

Then point the Ansible role at it, e.g.:
    ansible-playbook playbooks/sync-dxuim-config.yml --vault-password-file .vault_pass \\
      -e dxuim_api_base=http://127.0.0.1:8443 \\
      -e changed_file_path=dxuim-config/UAT/ulaeiapos0a/processes.json

Inspect what's been received without needing a real UIM console:
    curl http://127.0.0.1:8443/_stub/all
"""
import argparse
import base64
import json
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PROBE_PATH_RE = re.compile(r"^/uimapi/probes/(?P<domain>[^/]+)/(?P<hub>[^/]+)/(?P<robot>[^/]+)/(?P<probe>[^/]+)/config$")

# In-memory store: {(domain, hub, robot, probe): [ {key, value, encrypt}, ... ]}
_store: dict = {}
_store_lock = threading.Lock()


def make_handler(expected_user: str, expected_password: str):
    class Handler(BaseHTTPRequestHandler):
        server_version = "DXUIMStub/1.0"

        def log_message(self, fmt, *args):
            # Default log_message already writes to stderr with a timestamp —
            # just keep it, but tag it so it's obviously the stub talking.
            super().log_message("[dxuim-stub] " + fmt, *args)

        def _send_json(self, status: int, payload: dict):
            body = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _check_auth(self) -> bool:
            header = self.headers.get("Authorization", "")
            if not header.startswith("Basic "):
                return False
            try:
                decoded = base64.b64decode(header[len("Basic "):]).decode("utf-8")
                user, _, password = decoded.partition(":")
            except Exception:
                return False
            return user == expected_user and password == expected_password

        def _require_auth(self) -> bool:
            if self._check_auth():
                return True
            self._send_json(401, {"error": "unauthorized", "detail": "expected HTTP basic auth"})
            return False

        def do_PUT(self):
            if self.path == "/uimapi/probes" or self.path.startswith("/uimapi/probes/"):
                match = PROBE_PATH_RE.match(self.path)
                if not match:
                    self._send_json(400, {
                        "error": "bad_path",
                        "detail": f"expected /uimapi/probes/{{domain}}/{{hub}}/{{robot}}/{{probe}}/config, got {self.path}",
                    })
                    return
                if not self._require_auth():
                    return

                length = int(self.headers.get("Content-Length", 0))
                raw_body = self.rfile.read(length) if length else b""
                try:
                    payload = json.loads(raw_body or b"[]")
                except json.JSONDecodeError as e:
                    self._send_json(400, {"error": "invalid_json", "detail": str(e)})
                    return

                if not isinstance(payload, list):
                    self._send_json(400, {
                        "error": "invalid_shape",
                        "detail": "body must be a bare JSON array of {key, value, encrypt} — "
                                  "matches the guide.md sample, not the probeConfigKeys-wrapped file format",
                    })
                    return

                bad_entries = [e for e in payload if not isinstance(e, dict) or "key" not in e or "value" not in e]
                if bad_entries:
                    self._send_json(400, {
                        "error": "invalid_entry",
                        "detail": "every entry needs at least 'key' and 'value'",
                        "offending": bad_entries[:3],
                    })
                    return

                key = match.groups()
                with _store_lock:
                    _store[key] = payload

                domain, hub, robot, probe = key
                print(f"[dxuim-stub] PUT accepted: {domain}/{hub}/{robot}/{probe} "
                      f"({len(payload)} key(s))")
                self._send_json(200, {"result": "success", "keysApplied": len(payload)})
                return

            self._send_json(404, {"error": "not_found"})

        def do_GET(self):
            if self.path == "/_stub/all":
                with _store_lock:
                    dump = {"/".join(k): v for k, v in _store.items()}
                self._send_json(200, dump)
                return

            match = PROBE_PATH_RE.match(self.path)
            if match:
                if not self._require_auth():
                    return
                with _store_lock:
                    payload = _store.get(match.groups())
                if payload is None:
                    self._send_json(404, {"error": "no config stored for this probe yet"})
                else:
                    self._send_json(200, payload)
                return

            self._send_json(404, {"error": "not_found"})

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8443)
    parser.add_argument("--user", default="accountsvcid", help="expected basic-auth username (matches dxuim_auth_user)")
    parser.add_argument("--password", default="devpass", help="expected basic-auth password (matches vault_dxuim_password)")
    args = parser.parse_args()

    handler = make_handler(args.user, args.password)
    httpd = ThreadingHTTPServer((args.host, args.port), handler)
    print(f"[dxuim-stub] listening on http://{args.host}:{args.port}  (user={args.user!r})")
    print("[dxuim-stub] GET /_stub/all to inspect everything received")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
