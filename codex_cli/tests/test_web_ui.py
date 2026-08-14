#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import unittest


ADDON_DIR = Path(__file__).resolve().parents[1]
CONFIG_PATH = Path(os.environ.get("CODEX_WEB_TEST_CONFIG", ADDON_DIR / "config.yaml"))
NGINX_PATH = Path(os.environ.get("CODEX_WEB_TEST_NGINX", ADDON_DIR / "nginx.conf"))
TTYD_PATH = Path(os.environ.get("CODEX_WEB_TEST_TTYD", ADDON_DIR / "ttyd-run"))
PAGE_PATH = Path(os.environ.get("CODEX_WEB_TEST_PAGE", ADDON_DIR / "web" / "index.html"))


class WebUiTests(unittest.TestCase):
    def test_ingress_frontend_and_backends_stay_internal(self) -> None:
        config = CONFIG_PATH.read_text(encoding="utf-8")
        nginx = NGINX_PATH.read_text(encoding="utf-8")
        ttyd = TTYD_PATH.read_text(encoding="utf-8")

        self.assertIn('version: "2.4.0"', config)
        self.assertIn("ingress: true", config)
        self.assertIn("ingress_port: 8099", config)
        self.assertIn("listen 8099", nginx)
        self.assertIn("proxy_pass http://127.0.0.1:8100", nginx)
        self.assertIn("proxy_pass http://127.0.0.1:8101", nginx)
        self.assertIn("--interface 127.0.0.1", ttyd)
        self.assertIn("--base-path /terminal", ttyd)

    def test_dashboard_has_preview_and_confirmed_delete(self) -> None:
        page = PAGE_PATH.read_text(encoding="utf-8")

        self.assertIn('api("api/status")', page)
        self.assertIn('api("api/preview"', page)
        self.assertIn('api("api/cleanup"', page)
        self.assertIn('confirmation: "DELETE"', page)
        self.assertIn('src = "terminal/"', page)
        self.assertNotIn("https://", page)
        self.assertNotIn("http://", page)


if __name__ == "__main__":
    unittest.main()
