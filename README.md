# Home Assistant Codex CLI SSH

An unofficial, privileged Home Assistant app that provides a persistent Codex
CLI environment over SSH and automatically connects to the Home Assistant MCP
Server.

> [!WARNING]
> This app intentionally enables full access, the Docker API, the Supervisor
> API, and writable Home Assistant directories. Anyone with an authorized SSH
> key can make destructive changes to the Home Assistant installation.

The app itself lives in [`codex_cli/`](codex_cli/). Its detailed installation,
configuration, security, and troubleshooting documentation is available in
[`codex_cli/DOCS.md`](codex_cli/DOCS.md).

## Local development

This repository is the editable source of truth. The installed test copy under
`/addons/codex_cli` should be treated as generated deployment output.

### Install the development copy

Run from the repository root:

```sh
./scripts/install-local.sh
```

The script copies only the known app source files and does not delete other
files. After installation, reload the Home Assistant app store. Rebuild the
local app when Dockerfile or runtime files change; a catalog reload is enough
for README, documentation, icon, and logo changes.

### Validate locally

```sh
sh -n codex_cli/run.sh scripts/install-local.sh
python3 -c 'compile(open("codex_cli/init_codex.py", encoding="utf-8").read(), "codex_cli/init_codex.py", "exec")'
python3 codex_cli/tests/test_init_codex.py
```

After rebuilding and restarting the app, ask Codex to run the runtime test from
a `/root` workspace:

```sh
/usr/local/libexec/codex-tooling-integration.sh
```

The runtime test intentionally requires a Codex tool execution context because
the internal `apply_patch` helper is injected into that context rather than
installed as a global shell command.

### Development workflow

1. Edit files in `codex_cli/`.
2. Increment `version` in `codex_cli/config.yaml` for a testable app release.
3. Update `CHANGELOG.md`.
4. Run the validation commands.
5. Run `./scripts/install-local.sh`.
6. Reload the local app catalog and rebuild the app.

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
│   └── tests/
│       ├── container-smoke.sh
│       ├── tooling-integration.sh
│       └── test_init_codex.py
└── scripts/
    └── install-local.sh
```

## License

MIT. See [`LICENSE`](LICENSE).

## Trademark notice

This is an unofficial community project. It is not affiliated with or endorsed
by OpenAI or the Home Assistant project. OpenAI, Codex, and Home Assistant may
be trademarks of their respective owners.
