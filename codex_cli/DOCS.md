# Installation and operation

## Installation

1. Copy the complete add-on directory to `/addons/codex_cli`.
2. In Home Assistant, open **Settings → Apps → App Store → ⋮ → Check for updates**.
3. Install or update **Codex CLI SSH**.
4. Open the add-on page, disable **Protection mode**, and acknowledge the warning.
5. Configure at least one public SSH key:

```yaml
authorized_keys:
  - "ssh-ed25519 AAAA... codex-homeassistant"
auto_configure_home_assistant_mcp: true
workspace: "/config"
```

6. Install or update the local add-on, then start it. The default host port is `2222`.

Click **Open Web UI** on the app page to use the built-in terminal. Enable
**Show in sidebar** if you want a permanent **Codex CLI** navigation entry.

Connect with:

```sh
ssh -p 2222 root@HOME_ASSISTANT_IP
```

## Web terminal

The app runs `ttyd` directly on the internal Home Assistant Ingress port
`8099`. That port is not mapped to the host network. Browser authentication and
proxying are handled by Home Assistant, while the existing SSH port remains
available for desktop clients.

The web terminal attaches to a `tmux` session named `codex-cli` and starts in
`/config`. Closing the browser does not stop processes in that terminal. A
later browser connection reattaches to the same session. Multiple browser
connections share that root shell, so only trusted Home Assistant users should
be granted access to this privileged app.

Start Codex from the web terminal with either:

```sh
codex
codex-ha
```

## Persistence

`CODEX_HOME` is fixed to `/data/codex` for all processes. The Supervisor stores this directory persistently and includes it in add-on backups.

On the first start, an existing `/config/.codex` or legacy
`/homeassistant/.codex` directory is migrated to `/data/codex` if the new
destination is still empty.

Starting with version `2.2.0`, `/root/.codex` is intentionally absent. Older
versions created `/root/.codex -> /data/codex`; that writable symlink crossed a
path which Codex protects as read-only inside its Linux Bubblewrap sandbox and
could prevent the internal `apply_patch` tool from starting.

At startup, version `2.2.0` handles legacy paths as follows:

- An expected `/root/.codex -> /data/codex` symlink is removed. The target and
  all persistent data remain untouched.
- A real legacy `/root/.codex` directory is copied to a uniquely named
  `/data/codex/legacy-root-dot-codex*` backup, missing files are merged into
  `/data/codex`, and the legacy directory is removed.
- A symlink pointing anywhere other than `/data/codex` is rejected instead of
  being removed automatically.

No bind mount or additional Linux capability is required. `CODEX_HOME` is an
official Codex environment variable and directs config, authentication, logs,
sessions, skills, and state to `/data/codex` directly.

The add-on ensures that `config.toml` contains:

```toml
cli_auth_credentials_store = "file"
```

This keeps ChatGPT or API authentication and refreshed credentials in `/data/codex/auth.json`.

## Sandbox and writable paths

The app does not disable Codex sandboxing and does not add `CAP_SYS_ADMIN` or
other mount privileges. The host-side `/root/.codex` alias is absent. Inside a
tool sandbox, Bubblewrap may synthesize a protected read-only directory at that
path; critically, it is no longer a symlink. The Codex parent process keeps
using persistent `/data/codex` directly.

Home Assistant configuration is mounted at `/config` in this app. Set
`workspace: "/config"` to make it the primary writable workspace. Other
mapped directories such as `/addons`, `/addon_configs`, and `/share` remain
subject to the active Codex permission profile; add them as writable roots only
when the task requires them. Starting with version `2.2.1`, `/config` is the
canonical path inside this app. The former `/homeassistant` mount is no longer
created; update saved workspace settings or scripts that still reference it.

## Home Assistant MCP

When `auto_configure_home_assistant_mcp` is enabled, the add-on performs the following steps at startup:

1. Resolve the Supervisor credential from `SUPERVISOR_TOKEN`, `HASSIO_TOKEN`, or the corresponding S6 environment files.
2. Find the installed **Home Assistant MCP Server** through the Supervisor API.
3. Read its internal hostname and secret path.
4. Add `mcp_servers.home_assistant` to Codex's persistent `config.toml`.

The secret path is never written to the add-on log. An existing `home_assistant` MCP configuration is preserved.

Verify the registration:

```sh
ssh -p 2222 root@HOME_ASSISTANT_IP 'codex mcp list'
```

The server should be listed as `enabled`. An `Unsupported` value in the `Auth` column is expected for this secret-path endpoint; it means that OAuth or a bearer-token environment variable is not being used.

After changing the MCP configuration, restart this add-on so the Codex app server reloads it.

## Codex authentication

```sh
ssh -p 2222 root@HOME_ASSISTANT_IP
codex login --device-auth
codex login status
```

Start Codex directly with `codex`, or use the Home Assistant workspace launcher:

```sh
codex-ha
```

## Available paths

| Path | Contents |
|---|---|
| `/config` | Writable Home Assistant configuration |
| `/addons` | Writable local add-on sources |
| `/addon_configs` | Writable configuration for all add-ons |
| `/backup` | Writable backups |
| `/share` | Writable shared files |
| `/ssl` | Writable TLS files |
| `/media` | Writable media files |
| `/data` | Persistent private storage for this add-on |

Supervisor and Home Assistant Core APIs, the Docker API, hardware access, and full add-on access are also enabled.

## Archived-session cleanup

`codex-cleanup` reports persistent storage use without changing anything:

```sh
codex-cleanup status
```

Preview deletion of all archived sessions:

```sh
codex-cleanup archived --all
```

Preview archived sessions whose file modification time is at least 30 days
old:

```sh
codex-cleanup archived --older-than 30
```

Every cleanup command is a dry run unless `--yes` is supplied. After reviewing
the preview, perform the selected deletion with:

```sh
codex-cleanup archived --older-than 30 --yes
```

Generated images are retained by default. To remove only image directories
whose session ID matches a selected archived session, add the explicit option:

```sh
codex-cleanup archived --all --include-generated-images --yes
```

The command only considers direct, non-symlink `rollout-*.jsonl` files in
`/data/codex/archived_sessions`. It never selects active sessions,
`auth.json`, `config.toml`, plugins, skills, attachments, or unrelated files.

## Root access boundary

`full_access: true` grants privileged hardware and container access, but it does not mount the real Home Assistant OS root filesystem at `/`. Home Assistant only permits the managed directory mappings listed above; `/` is not a valid map target.

For direct root access to the HAOS host, configure the separate official debug SSH service on port `22222`.

## Verification

```sh
ssh -p 2222 root@HOME_ASSISTANT_IP 'printf "CODEX_HOME=%s\n" "$CODEX_HOME"; codex --version'
ssh -p 2222 root@HOME_ASSISTANT_IP 'codex login status; codex mcp list'
ssh -p 2222 root@HOME_ASSISTANT_IP 'command -v patch; test ! -e /root/.codex'
```

Restart the add-on once, repeat the second command, and confirm that the MCP server remains configured.

The successful startup message is:

```text
Home Assistant MCP configuration is present
```

### Tooling integration test

The image build runs `/usr/local/libexec/container-smoke.sh`, which verifies
that `patch`, `ttyd`, `tmux`, and `codex-cleanup` are installed,
`CODEX_HOME=/data/codex`, and `/root/.codex` is not a symlink. The build also
runs the cleanup CLI safety tests.

The internal `apply_patch` helper exists only inside a Codex tool execution
context. From a Codex session whose workspace is `/root`, ask Codex to run:

```sh
/usr/local/libexec/codex-tooling-integration.sh
```

This creates a temporary file under `/root`, modifies it through the internal
`apply_patch`, applies a second unified diff with the Alpine `patch` command,
verifies both results, and removes the temporary directory.

## Troubleshooting

### MCP auto-configuration is skipped

Confirm that:

- **Home Assistant MCP Server** is installed and running.
- `auto_configure_home_assistant_mcp` is enabled.
- Codex CLI SSH is version `2.1.1` or newer.
- The add-on was restarted after Home Assistant MCP became available.

Version `2.1.0` could report `SUPERVISOR_TOKEN is unavailable` because it only checked the process environment. Version `2.1.1` also supports `HASSIO_TOKEN` and the S6 environment files.

### MCP is configured but tools are not visible

Restart Codex CLI SSH so its app server reloads `/data/codex/config.toml`. Then open a new Codex session and run `codex mcp list` again.

### Workspace does not exist

The configured `workspace` must be an existing directory. If it is unavailable, the add-on falls back to `/config`.

### Web UI returns 502

Check the app log for `Starting Codex Ingress web terminal`. If the message is
missing, rebuild version `2.3.0` rather than only restarting an older image.

### `apply_patch` reports a writable symlink error

Confirm that the app is version `2.2.0` or newer and restart it. Then verify:

```sh
printf 'CODEX_HOME=%s\n' "$CODEX_HOME"
test ! -e /root/.codex && echo sandbox-safe
```

Do not recreate `/root/.codex` as a symlink. Persistent state remains available
through `CODEX_HOME=/data/codex`.

## Security recommendations

- Use a dedicated SSH key for this add-on.
- Keep private keys off the Home Assistant host.
- Remove obsolete public keys from `authorized_keys`.
- Do not expose port `2222` directly to the internet.
- Back up Home Assistant before making broad configuration changes.
