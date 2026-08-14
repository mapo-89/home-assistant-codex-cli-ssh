# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.3.1] - 2026-08-14

### Added

- One-click My Home Assistant button that opens the add-on repository dialog
  with this repository's URL pre-filled.
- Root-level Home Assistant repository metadata so the repository is
  recognized as a valid app repository.

## [2.3.0] - 2026-08-14

### Added

- Home Assistant Ingress web terminal powered by `ttyd`, with a persistent
  `tmux` session rooted at `/config`.
- Sidebar metadata for the **Codex CLI** web terminal.
- `codex-cleanup` storage report and explicit archived-session cleanup with
  dry-run behavior, age selection, optional matching-image removal, and
  symlink protection.
- Build tests for web-terminal dependencies and cleanup safety.

### Security

- Keep the web-terminal port internal to Home Assistant Ingress; no additional
  host port is published.
- Require `--yes` before cleanup deletes anything and leave active sessions,
  authentication, configuration, and unrelated files untouched.

## [2.2.1] - 2026-08-14

### Changed

- Mount Home Assistant configuration at the conventional `/config` path.
- Use `/config` as the default Docker working directory, SSH workspace, and
  `codex-ha` workspace.
- Keep `/homeassistant/.codex` as a legacy migration source only.

### Migration

- Update custom `workspace` options and scripts from `/homeassistant` to
  `/config`. The former `/homeassistant` mount is no longer created.

## [2.2.0] - 2026-08-11

### Added

- Home Assistant app icon and logo.
- Standalone local-development repository layout.
- Safe local installation helper for `/addons/codex_cli`.
- Alpine `patch` package in the app image.
- Build and runtime integration tests for `patch`, the internal Codex
  `apply_patch` helper, and the Codex home layout.

### Changed

- Keep `/data/codex` as the only Codex state path and stop creating the
  `/root/.codex` symlink that conflicted with Bubblewrap path protection.
- Migrate an expected legacy symlink safely; preserve and merge a legacy real
  `/root/.codex` directory before removing it.

### Security

- Restore `apply_patch` compatibility without adding mount capabilities,
  disabling Bubblewrap, or widening the configured writable roots.

## [2.1.1] - 2026-08-04

### Fixed

- Resolve the Home Assistant Supervisor credential from `SUPERVISOR_TOKEN`,
  `HASSIO_TOKEN`, or their S6 environment files.
- Automatically configure Home Assistant MCP when the Supervisor token is not
  exported into the startup process environment.

### Changed

- Rewrote the app documentation in English.

## [2.1.0] - 2026-08-04

### Added

- Persistent Codex state under `/data/codex`.
- SSH access using configured public keys.
- Automatic Home Assistant MCP discovery.
- Writable Home Assistant managed-directory mappings and privileged APIs.
