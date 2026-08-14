# Home Assistant Codex CLI SSH

[![Version](https://img.shields.io/badge/version-2.4.0-03a9f4.svg)](CHANGELOG.md)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Add--on-41BDF5.svg?logo=homeassistant&logoColor=white)](https://www.home-assistant.io/)
[![Architectures](https://img.shields.io/badge/arch-amd64%20%7C%20aarch64-6f42c1.svg)](codex_cli/config.yaml)
[![GitHub issues](https://img.shields.io/github/issues/mapo-89/home-assistant-codex-cli-ssh.svg)](https://github.com/mapo-89/home-assistant-codex-cli-ssh/issues)
[![GitHub stars](https://img.shields.io/github/stars/mapo-89/home-assistant-codex-cli-ssh.svg?style=flat)](https://github.com/mapo-89/home-assistant-codex-cli-ssh/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/mapo-89/home-assistant-codex-cli-ssh.svg)](https://github.com/mapo-89/home-assistant-codex-cli-ssh/commits/main)

[![Open your Home Assistant instance and show the add add-on repository dialog with a specific repository URL pre-filled.](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2Fmapo-89%2Fhome-assistant-codex-cli-ssh)

<a href="https://buymeacoffee.com/mapo"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me a Coffee" height="60"></a>

An unofficial, privileged Home Assistant app that provides a persistent Codex
CLI environment over SSH and Home Assistant Ingress, automatically connects to
the Home Assistant MCP Server, and includes safe archived-session management.

> [!WARNING]
> This app intentionally enables full access, the Docker API, the Supervisor
> API, and writable Home Assistant directories. Anyone with access to its SSH
> or Ingress terminal can make destructive changes to the installation.

## Highlights

- Integrated Ingress dashboard with storage overview and confirmed cleanup
- Browser terminal backed by `ttyd` and a persistent `tmux` session
- SSH access for Codex Desktop and other clients
- Persistent Codex authentication, configuration, sessions, skills and plugins
- Automatic Home Assistant MCP discovery
- Writable Home Assistant configuration at `/config`
- Safe `codex-cleanup` CLI with dry-run behavior

The app itself lives in [`codex_cli/`](codex_cli/). Detailed installation,
configuration, security, cleanup and troubleshooting documentation is in
[`codex_cli/DOCS.md`](codex_cli/DOCS.md).

## Local development

This repository is the editable source of truth. The installed test copy under
`/addons/codex_cli` is generated deployment output.

### Install the development copy

```sh
./scripts/install-local.sh
```

After installation, reload the Home Assistant app store and update the local
app. Dockerfile or runtime changes require a build; documentation and artwork
only require a catalog reload.

### Validate locally

```sh
bash -n codex_cli/run.sh codex_cli/ttyd-run codex_cli/cleanup-api-run codex_cli/nginx-run
sh -n scripts/install-local.sh
python3 -c 'compile(open("codex_cli/init_codex.py", encoding="utf-8").read(), "codex_cli/init_codex.py", "exec")'
python3 codex_cli/tests/test_init_codex.py
python3 codex_cli/tests/test_codex_cleanup.py
python3 codex_cli/tests/test_cleanup_api.py
python3 codex_cli/tests/test_web_ui.py
```

After rebuilding, the internal Codex tool integration test can be run from a
Codex tool execution context whose workspace is `/root`:

```sh
/usr/local/libexec/codex-tooling-integration.sh
```

## Repository structure

```text
.
├── CHANGELOG.md
├── LICENSE
├── README.md
├── codex_cli/
│   ├── config.yaml
│   ├── Dockerfile
│   ├── DOCS.md
│   ├── README.md
│   ├── icon.png
│   ├── logo.png
│   ├── run.sh
│   ├── init_codex.py
│   ├── codex-ha
│   ├── codex-cleanup
│   ├── cleanup-api
│   ├── nginx.conf
│   ├── ttyd-run
│   ├── cleanup-api-run
│   ├── nginx-run
│   ├── web/
│   │   └── index.html
│   └── tests/
│       ├── container-smoke.sh
│       ├── tooling-integration.sh
│       ├── test_init_codex.py
│       ├── test_codex_cleanup.py
│       ├── test_cleanup_api.py
│       └── test_web_ui.py
└── scripts/
    └── install-local.sh
```

## Support the project

If this community project saves you time, you can support its continued
maintenance through Buy Me a Coffee using the banner at the top.
Support is optional and does not change access to features or support.

## License

MIT. See [`LICENSE`](LICENSE).

## Trademark notice

This is an unofficial community project. It is not affiliated with or endorsed
by OpenAI or the Home Assistant project. OpenAI, Codex, and Home Assistant may
be trademarks of their respective owners.
