# Codex CLI SSH

[![Version](https://img.shields.io/badge/version-2.4.0-03a9f4.svg)](https://github.com/mapo-89/home-assistant-codex-cli-ssh/blob/main/CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/mapo-89/home-assistant-codex-cli-ssh/blob/main/LICENSE)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Add--on-41BDF5.svg?logo=homeassistant&logoColor=white)](https://www.home-assistant.io/)
[![Architectures](https://img.shields.io/badge/arch-amd64%20%7C%20aarch64-6f42c1.svg)](https://github.com/mapo-89/home-assistant-codex-cli-ssh)

<a href="https://buymeacoffee.com/mapo"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me a Coffee" height="60"></a>

A privileged local Home Assistant add-on that provides a dedicated Codex CLI
environment through SSH and an integrated Ingress dashboard.

## Features

- Storage dashboard with previewed, confirmation-protected session cleanup
- Home Assistant Ingress terminal with a persistent `tmux` session
- Codex CLI with the `codex-ha` launcher
- Persistent Codex state in `/data/codex`
- Automatic Home Assistant MCP configuration
- Alpine `patch` and sandbox-compatible internal Codex `apply_patch`
- Safe `codex-cleanup` command for scripted retention
- Persistent SSH host keys and writable Home Assistant directories

See [DOCS.md](DOCS.md) for installation, configuration, cleanup, verification,
security and troubleshooting.

## Security model

This add-on is intentionally highly privileged. Anyone who can open its Ingress
dashboard or authenticate with a configured SSH key can modify or destroy Home
Assistant data. Use dedicated SSH keys and restrict app access to trusted Home
Assistant administrators.

The cleanup API binds only to container loopback behind Ingress, requires a
per-start request token, previews selections, and requires an explicit
`DELETE` confirmation before removing direct non-symlink archived-session
files. It never selects active sessions, authentication or configuration.

## Support

If this project is useful to you, the optional Buy Me a Coffee link is
available at the top. Donations do not change access to features or support.

## Root access boundary

The add-on runs as `root` inside its container and can access the Home Assistant
directories explicitly mapped in `config.yaml`. It does not map the HAOS host
root filesystem. Official HAOS debug SSH on port `22222` remains a separate
facility.
