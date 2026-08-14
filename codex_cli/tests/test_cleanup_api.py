#!/usr/bin/env python3
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
import urllib.error
import urllib.request


API = Path(os.environ.get("CLEANUP_API_BIN", Path(__file__).resolve().parents[1] / "cleanup-api"))
CLEANUP = Path(os.environ.get("CODEX_CLEANUP_BIN", Path(__file__).resolve().parents[1] / "codex-cleanup"))
PORT = 18101
SESSION_ID = "019fde4d-847c-7b01-a877-b7492a186629"
SESSION_NAME = f"rollout-2026-08-07T22-17-29-{SESSION_ID}.jsonl"


class CleanupApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temporary = tempfile.TemporaryDirectory()
        cls.codex_home = Path(cls.temporary.name) / "codex"
        archived = cls.codex_home / "archived_sessions"
        active = cls.codex_home / "sessions"
        archived.mkdir(parents=True)
        active.mkdir()
        (archived / SESSION_NAME).write_text("archived\n", encoding="utf-8")
        (active / "active.jsonl").write_text("active\n", encoding="utf-8")
        (cls.codex_home / "auth.json").write_text("{}\n", encoding="utf-8")
        environment = os.environ.copy()
        environment.update({"CODEX_HOME": str(cls.codex_home), "CODEX_CLEANUP_BIN": str(CLEANUP), "CLEANUP_API_PORT": str(PORT)})
        cls.process = subprocess.Popen([sys.executable, str(API)], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, text=True, env=environment)
        for _ in range(50):
            try:
                cls.status = cls.request("GET", "/api/status")
                break
            except (OSError, urllib.error.URLError):
                time.sleep(0.05)
        else:
            raise RuntimeError("cleanup API did not start")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.process.terminate()
        cls.process.wait(timeout=5)
        cls.temporary.cleanup()

    @classmethod
    def request(cls, method: str, path: str, payload: dict | None = None, token: str | None = None) -> dict:
        data = json.dumps(payload).encode() if payload is not None else None
        headers = {"Content-Type": "application/json"}
        if token is not None:
            headers["X-Codex-Cleanup-Token"] = token
        request = urllib.request.Request(f"http://127.0.0.1:{PORT}{path}", data=data, headers=headers, method=method)
        with urllib.request.urlopen(request, timeout=2) as response:
            return json.load(response)

    def test_status_has_request_token(self) -> None:
        self.assertEqual(self.status["archived_sessions"]["count"], 1)
        self.assertTrue(self.status["request_token"])

    def test_mutation_requires_token_and_confirmation(self) -> None:
        payload = {"mode": "all", "include_generated_images": False}
        with self.assertRaises(urllib.error.HTTPError) as missing_token:
            self.request("POST", "/api/preview", payload)
        self.assertEqual(missing_token.exception.code, 403)
        missing_token.exception.close()
        preview = self.request("POST", "/api/preview", payload, self.status["request_token"])
        self.assertEqual(preview["selected_sessions"], 1)
        self.assertTrue((self.codex_home / "archived_sessions" / SESSION_NAME).exists())
        with self.assertRaises(urllib.error.HTTPError) as no_confirmation:
            self.request("POST", "/api/cleanup", payload, self.status["request_token"])
        self.assertEqual(no_confirmation.exception.code, 403)
        no_confirmation.exception.close()
        deleted = self.request("POST", "/api/cleanup", {**payload, "confirmation": "DELETE"}, self.status["request_token"])
        self.assertTrue(deleted["deleted"])
        self.assertFalse((self.codex_home / "archived_sessions" / SESSION_NAME).exists())
        self.assertTrue((self.codex_home / "sessions" / "active.jsonl").exists())
        self.assertTrue((self.codex_home / "auth.json").exists())


if __name__ == "__main__":
    unittest.main()
