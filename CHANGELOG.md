# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Home Assistant app icon and logo.
- Standalone local-development repository layout.
- Safe local installation helper for `/addons/codex_cli`.

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

