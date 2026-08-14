#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


CLEANUP = Path(
    os.environ.get(
        "CODEX_CLEANUP_BIN",
        Path(__file__).resolve().parents[1] / "codex-cleanup",
    )
)
SESSION_ID = "019fde4d-847c-7b01-a877-b7492a186629"
SESSION_NAME = f"rollout-2026-08-07T22-17-29-{SESSION_ID}.jsonl"


class CodexCleanupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.codex_home = Path(self.temporary.name) / "codex"
        self.archived = self.codex_home / "archived_sessions"
        self.active = self.codex_home / "sessions"
        self.images = self.codex_home / "generated_images" / SESSION_ID
        self.archived.mkdir(parents=True)
        self.active.mkdir()
        self.images.mkdir(parents=True)
        (self.archived / SESSION_NAME).write_text("archived\n", encoding="utf-8")
        (self.archived / "keep.txt").write_text("keep\n", encoding="utf-8")
        (self.active / "active.jsonl").write_text("active\n", encoding="utf-8")
        (self.images / "image.png").write_bytes(b"image")
        (self.codex_home / "auth.json").write_text("{}\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_cleanup(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["CODEX_HOME"] = str(self.codex_home)
        return subprocess.run(
            [sys.executable, str(CLEANUP), *arguments],
            check=True,
            capture_output=True,
            text=True,
            env=environment,
        )

    def test_status_does_not_modify_data(self) -> None:
        result = self.run_cleanup("status")
        self.assertIn("Archived Codex sessions: 1 files", result.stdout)
        self.assertTrue((self.archived / SESSION_NAME).exists())

    def test_archived_is_dry_run_without_yes(self) -> None:
        result = self.run_cleanup("archived", "--all")
        self.assertIn("Dry run only", result.stdout)
        self.assertTrue((self.archived / SESSION_NAME).exists())

    def test_delete_preserves_unrelated_and_active_data(self) -> None:
        self.run_cleanup("archived", "--all", "--yes")
        self.assertFalse((self.archived / SESSION_NAME).exists())
        self.assertTrue((self.archived / "keep.txt").exists())
        self.assertTrue((self.active / "active.jsonl").exists())
        self.assertTrue((self.codex_home / "auth.json").exists())
        self.assertTrue(self.images.exists())

    def test_generated_images_require_explicit_option(self) -> None:
        self.run_cleanup(
            "archived",
            "--all",
            "--include-generated-images",
            "--yes",
        )
        self.assertFalse(self.images.exists())

    def test_symlink_named_like_session_is_never_followed(self) -> None:
        external = Path(self.temporary.name) / "external.jsonl"
        external.write_text("external\n", encoding="utf-8")
        linked_name = (
            "rollout-2026-08-01T00-00-00-"
            "019f0000-0000-7000-8000-000000000000.jsonl"
        )
        (self.archived / linked_name).symlink_to(external)

        self.run_cleanup("archived", "--all", "--yes")

        self.assertTrue(external.exists())
        self.assertTrue((self.archived / linked_name).is_symlink())


if __name__ == "__main__":
    unittest.main()
