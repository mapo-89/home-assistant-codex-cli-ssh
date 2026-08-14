# Codex CLI SSH

A privileged local Home Assistant add-on that provides a dedicated Codex CLI environment over SSH.

## Features

- Codex CLI with the `codex-ha` launcher
- Persistent Codex state in `/data/codex`
- File-based authentication storage for headless sessions
- Automatic discovery and configuration of the Home Assistant MCP Server
- Persistent Alpine `patch` command for unified diffs
- Sandbox-compatible internal Codex `apply_patch` support
- Persistent SSH host keys in `/data`
- Writable Home Assistant configuration at `/config`
- Writable access to local add-ons, add-on configuration, backups, share, SSL, and media
- Supervisor, Home Assistant, Docker, hardware, and full add-on access

See [DOCS.md](DOCS.md) for installation, configuration, verification, and troubleshooting.

## Security model

This add-on is intentionally highly privileged. Anyone who has a configured private SSH key can modify or destroy the Home Assistant installation and its data. Protection mode must be disabled for the advertised functionality.

Use dedicated SSH keys, protect their private halves, and remove keys that are no longer needed.

## Root access boundary

The add-on runs as `root` inside its own container and can access the Home Assistant directories explicitly mapped in `config.yaml`. Home Assistant does not allow an add-on to map the actual HAOS host root filesystem to `/`.

For direct root access to the HAOS host, configure Home Assistant's official debug SSH access on port `22222`. This is separate from this add-on's SSH service, which defaults to host port `2222`.
