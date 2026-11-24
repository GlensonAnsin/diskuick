"""Updater tests against a local fake of the GitHub API (no real network)."""
import hashlib
import http.server
import json
import os
import sys
import tempfile
import threading
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import updater

PAYLOAD = b"MZ" + os.urandom(2048)
GOOD = hashlib.sha256(PAYLOAD).hexdigest()
STATE = {"release": None, "sidecar": None}


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, body: bytes, ctype="application/octet-stream", code=200):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.endswith("/releases/latest"):
            if STATE["release"] is None:
                return self._send(b"{}", code=404)
            return self._send(json.dumps(STATE["release"]).encode(), "application/json")
        if self.path == "/dl/Diskuick-Setup-9.9.9.exe":
            return self._send(PAYLOAD)
        if self.path == "/dl/Diskuick-Setup-9.9.9.exe.sha256":
            return self._send((STATE["sidecar"] or "").encode())
        self._send(b"nope", code=404)


def release(base, tag="v9.9.9", digest=None, sidecar=False, name="Diskuick-Setup-9.9.9.exe", url=None):
    a = [{"name": name, "browser_download_url": url or f"{base}/dl/{name}", "size": len(PAYLOAD)}]
    if digest:
        a[0]["digest"] = digest
    if sidecar:
        a.append({"name": name + ".sha256", "browser_download_url": f"{base}/dl/{name}.sha256"})
    return {"tag_name": tag, "html_url": "https://github.com/o/r/releases/tag/" + tag, "assets": a}


class UpdaterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.base = f"http://127.0.0.1:{cls.srv.server_port}"
        threading.Thread(target=cls.srv.serve_forever, daemon=True).start()
        cls.old = updater.API_BASE
        updater.API_BASE = cls.base

    @classmethod
    def tearDownClass(cls):
        updater.API_BASE = cls.old
        cls.srv.shutdown()

    def setUp(self):
        STATE.update(release=None, sidecar=None)
        self.tmp = tempfile.mkdtemp()

    # ---- check
    def test_no_release(self):
        self.assertIsNone(updater.check("o/r", "1.0.0"))

    def test_not_newer(self):
        STATE["release"] = release(self.base, tag="v1.0.0", digest="sha256:" + GOOD)
        self.assertIsNone(updater.check("o/r", "1.0.0"))
        self.assertIsNone(updater.check("o/r", "2.0.0"))

    def test_newer_with_api_digest(self):
        STATE["release"] = release(self.base, digest="sha256:" + GOOD.upper())
        info = updater.check("o/r", "1.2.0")
        self.assertEqual(info["tag"], "v9.9.9")
        self.assertEqual(info["sha256"], GOOD)  # normalised to lower-case
        self.assertTrue(info["asset_url"].endswith("Diskuick-Setup-9.9.9.exe"))

    def test_newer_with_sha256_sidecar(self):
        STATE["release"] = release(self.base, sidecar=True)
        STATE["sidecar"] = f"{GOOD}  Diskuick-Setup-9.9.9.exe\n"
        self.assertEqual(updater.check("o/r", "1.2.0")["sha256"], GOOD)

    def test_no_checksum_means_no_sha(self):
        STATE["release"] = release(self.base)
        info = updater.check("o/r", "1.2.0")
        self.assertIsNone(info["sha256"])
        with self.assertRaises(updater.UpdateError):
            updater.download(info, self.tmp)

    def test_release_without_installer(self):
        STATE["release"] = {"tag_name": "v9.9.9", "html_url": "x", "assets": []}
        info = updater.check("o/r", "1.2.0")
        self.assertIsNone(info["asset_url"])
        self.assertFalse(updater.can_self_update(info))

    def test_disabled_without_repo(self):
        self.assertIsNone(updater.check("", "1.0.0"))
        self.assertIsNone(updater.check("noslash", "1.0.0"))

    # ---- download
    def test_download_verifies_and_reports_progress(self):
        STATE["release"] = release(self.base, digest="sha256:" + GOOD)
        info = updater.check("o/r", "1.2.0")
        seen = []
        path = updater.download(info, self.tmp, progress=seen.append)
        self.assertEqual(open(path, "rb").read(), PAYLOAD)
        self.assertEqual(seen[-1], 1.0)

    def test_bad_checksum_is_discarded(self):
        STATE["release"] = release(self.base, digest="sha256:" + "0" * 64)
        info = updater.check("o/r", "1.2.0")
        with self.assertRaises(updater.UpdateError):
            updater.download(info, self.tmp)
        self.assertEqual(os.listdir(self.tmp), [])  # nothing left behind

    def test_cancel(self):
        STATE["release"] = release(self.base, digest="sha256:" + GOOD)
        info = updater.check("o/r", "1.2.0")
        ev = threading.Event()
        ev.set()
        with self.assertRaises(updater.UpdateError):
            updater.download(info, self.tmp, cancel=ev)
        self.assertEqual(os.listdir(self.tmp), [])

    # ---- safety
    def test_refuses_foreign_hosts(self):
        info = {"asset_url": "https://evil.example.com/Diskuick-Setup-9.9.9.exe", "sha256": GOOD,
                "asset_name": "Diskuick-Setup-9.9.9.exe"}
        with self.assertRaises(updater.UpdateError):
            updater.download(info, self.tmp)
        info["asset_url"] = "http://github.com/o/r/Diskuick-Setup-9.9.9.exe"  # plain http
        with self.assertRaises(updater.UpdateError):
            updater.download(info, self.tmp)
        info["asset_url"] = "https://github.com.evil.example/x.exe"            # look-alike host
        with self.assertRaises(updater.UpdateError):
            updater.download(info, self.tmp)

    def test_allowed_hosts(self):
        a = updater._allowed
        self.assertTrue(a("https://github.com/o/r/releases/download/v1/x.exe"))
        self.assertTrue(a("https://objects.githubusercontent.com/abc"))
        self.assertFalse(a("https://notgithub.com/x"))
        self.assertFalse(a("ftp://github.com/x"))

    def test_rejects_odd_installer_names(self):
        info = {"asset_url": self.base + "/dl/x", "sha256": GOOD, "asset_name": r"..\..\evil.exe"}
        with self.assertRaises(updater.UpdateError):
            updater.download(info, self.tmp)

    def test_self_update_only_for_installed_copy(self):
        info = {"asset_url": "u", "sha256": GOOD}
        self.assertFalse(updater.can_self_update(info))  # running from source, not an installed exe

    def test_versions(self):
        self.assertTrue(updater.is_newer("v1.2.1", "1.2.0"))
        self.assertFalse(updater.is_newer("v1.2.0", "1.2.0"))
        self.assertTrue(updater.is_newer("v1.10.0", "1.9.9"))

    def test_installer_args(self):
        a = updater.installer_args(1234)
        for flag in ("/SILENT", "/NORESTART", "/RELAUNCH=1", "/WAITPID=1234"):
            self.assertIn(flag, a)
        self.assertIn(f"/WAITPID={os.getpid()}", updater.installer_args())


if __name__ == "__main__":
    unittest.main()
