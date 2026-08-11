#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / "init_codex.py"
SPEC = importlib.util.spec_from_file_location("init_codex", MODULE_PATH)
assert SPEC and SPEC.loader
init_codex = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(init_codex)


class RootCodexAliasTests(unittest.TestCase):
    def test_expected_symlink_is_removed_without_touching_data(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_home = root / "data" / "codex"
            alias = root / "root" / ".codex"
            codex_home.mkdir(parents=True)
            alias.parent.mkdir(parents=True)
            (codex_home / "config.toml").write_text("model = 'test'\n", encoding="utf-8")
            alias.symlink_to(codex_home)

            init_codex.prepare_root_codex_alias(alias, codex_home)

            self.assertFalse(alias.exists())
            self.assertFalse(alias.is_symlink())
            self.assertEqual(
                (codex_home / "config.toml").read_text(encoding="utf-8"),
                "model = 'test'\n",
            )

    def test_unexpected_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_home = root / "data" / "codex"
            unexpected = root / "other"
            alias = root / "root" / ".codex"
            codex_home.mkdir(parents=True)
            unexpected.mkdir()
            alias.parent.mkdir(parents=True)
            alias.symlink_to(unexpected)

            with self.assertRaisesRegex(RuntimeError, "unexpected Codex symlink"):
                init_codex.prepare_root_codex_alias(alias, codex_home)

            self.assertTrue(alias.is_symlink())

    def test_real_directory_is_merged_and_backed_up(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            codex_home = root / "data" / "codex"
            alias = root / "root" / ".codex"
            codex_home.mkdir(parents=True)
            alias.mkdir(parents=True)
            (codex_home / "config.toml").write_text("persistent\n", encoding="utf-8")
            (alias / "config.toml").write_text("legacy\n", encoding="utf-8")
            (alias / "legacy.json").write_text("{}\n", encoding="utf-8")

            init_codex.prepare_root_codex_alias(alias, codex_home)

            self.assertFalse(alias.exists())
            self.assertEqual(
                (codex_home / "config.toml").read_text(encoding="utf-8"),
                "persistent\n",
            )
            self.assertEqual(
                (codex_home / "legacy.json").read_text(encoding="utf-8"),
                "{}\n",
            )
            self.assertEqual(
                (codex_home / "legacy-root-dot-codex" / "config.toml").read_text(
                    encoding="utf-8"
                ),
                "legacy\n",
            )


if __name__ == "__main__":
    unittest.main()
