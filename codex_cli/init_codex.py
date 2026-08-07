#!/usr/bin/env python3
"""Initialize persistent Codex state without printing credentials."""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import shutil
import sys
import urllib.error
import urllib.request

CODEX_HOME = Path(os.environ.get("CODEX_HOME", "/data/codex"))
CONFIG = CODEX_HOME / "config.toml"
S6_ENVIRONMENT = Path("/run/s6/container_environment")

def log(level: str, message: str) -> None:
    print(f"[{level}] {message}", file=sys.stderr if level == "warning" else sys.stdout)

def migrate_legacy_state() -> None:
    if any(CODEX_HOME.iterdir()):
        return
    for legacy in (Path("/homeassistant/.codex"), Path("/config/.codex")):
        if not legacy.is_dir() or legacy.resolve() == CODEX_HOME.resolve():
            continue
        for item in legacy.iterdir():
            target = CODEX_HOME / item.name
            if target.exists():
                continue
            if item.is_dir():
                shutil.copytree(item, target, symlinks=True)
            else:
                shutil.copy2(item, target, follow_symlinks=False)
        log("info", f"Migrated legacy Codex state from {legacy}")
        return

def supervisor_token() -> str:
    for name in ("SUPERVISOR_TOKEN", "HASSIO_TOKEN"):
        token = os.environ.get(name)
        if token:
            return token
    for name in ("SUPERVISOR_TOKEN", "HASSIO_TOKEN"):
        try:
            token = (S6_ENVIRONMENT / name).read_text(encoding="utf-8").strip()
        except OSError:
            continue
        if token:
            return token
    raise RuntimeError("Home Assistant Supervisor token is unavailable")

def supervisor_json(path: str) -> dict:
    token = supervisor_token()
    request = urllib.request.Request(
        f"http://supervisor{path}",
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(request, timeout=10) as response:
        payload = json.load(response)
    if payload.get("result") != "ok":
        raise RuntimeError(payload.get("message") or f"Supervisor request failed: {path}")
    return payload.get("data") or {}

def discover_mcp_url() -> str | None:
    addons = supervisor_json("/addons").get("addons", [])
    matches = [
        addon for addon in addons
        if addon.get("slug") == "81f33d0f_ha_mcp"
        or addon.get("name") == "Home Assistant MCP Server"
    ]
    if not matches:
        return None
    slug = matches[0]["slug"]
    details = supervisor_json(f"/addons/{slug}/info")
    secret_path = (details.get("options") or {}).get("secret_path")
    if not isinstance(secret_path, str) or not secret_path.startswith("/"):
        return None
    hostname = details.get("hostname") or slug.replace("_", "-")
    return f"http://{hostname}:9583{secret_path}"

def ensure_top_level_setting(text: str) -> str:
    if re.search(r"(?m)^\s*cli_auth_credentials_store\s*=", text):
        return text
    return 'cli_auth_credentials_store = "file"\n' + text

def ensure_mcp(text: str, url: str) -> str:
    if re.search(r"(?m)^\s*\[mcp_servers\.home_assistant\]\s*$", text):
        return text
    encoded = json.dumps(url)
    suffix = "" if not text or text.endswith("\n") else "\n"
    return text + suffix + f"\n[mcp_servers.home_assistant]\nurl = {encoded}\nenabled = true\n"

def main() -> int:
    options = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    CODEX_HOME.mkdir(parents=True, exist_ok=True)
    os.chmod(CODEX_HOME, 0o700)
    migrate_legacy_state()
    text = CONFIG.read_text(encoding="utf-8") if CONFIG.exists() else ""
    text = ensure_top_level_setting(text)
    if options.get("auto_configure_home_assistant_mcp", True):
        try:
            mcp_url = discover_mcp_url()
            if mcp_url:
                text = ensure_mcp(text, mcp_url)
                log("info", "Home Assistant MCP configuration is present")
            else:
                log("warning", "Home Assistant MCP add-on or secret path was not found")
        except (RuntimeError, OSError, urllib.error.URLError, ValueError) as exc:
            log("warning", f"Home Assistant MCP auto-configuration skipped: {exc}")
    temporary = CONFIG.with_suffix(".toml.tmp")
    temporary.write_text(text, encoding="utf-8")
    os.chmod(temporary, 0o600)
    temporary.replace(CONFIG)
    auth = CODEX_HOME / "auth.json"
    if auth.exists():
        os.chmod(auth, 0o600)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
