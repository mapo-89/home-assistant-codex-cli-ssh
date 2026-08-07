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
workspace: "/homeassistant"
```

6. Install or update the local add-on, then start it. The default host port is `2222`.

Connect with:

```sh
ssh -p 2222 root@HOME_ASSISTANT_IP
```

## Persistence

`CODEX_HOME` is fixed to `/data/codex` for all processes. The Supervisor stores this directory persistently and includes it in add-on backups.

On the first start, an existing `/homeassistant/.codex` or legacy `/config/.codex` directory is migrated to `/data/codex` if the new destination is still empty. `/root/.codex` is then linked to the same directory.

The add-on ensures that `config.toml` contains:

```toml
cli_auth_credentials_store = "file"
```

This keeps ChatGPT or API authentication and refreshed credentials in `/data/codex/auth.json`.

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
| `/homeassistant` | Writable Home Assistant configuration |
| `/addons` | Writable local add-on sources |
| `/addon_configs` | Writable configuration for all add-ons |
| `/backup` | Writable backups |
| `/share` | Writable shared files |
| `/ssl` | Writable TLS files |
| `/media` | Writable media files |
| `/data` | Persistent private storage for this add-on |

Supervisor and Home Assistant Core APIs, the Docker API, hardware access, and full add-on access are also enabled.

## Root access boundary

`full_access: true` grants privileged hardware and container access, but it does not mount the real Home Assistant OS root filesystem at `/`. Home Assistant only permits the managed directory mappings listed above; `/` is not a valid map target.

For direct root access to the HAOS host, configure the separate official debug SSH service on port `22222`.

## Verification

```sh
ssh -p 2222 root@HOME_ASSISTANT_IP 'printf "CODEX_HOME=%s\n" "$CODEX_HOME"; codex --version'
ssh -p 2222 root@HOME_ASSISTANT_IP 'codex login status; codex mcp list'
```

Restart the add-on once, repeat the second command, and confirm that the MCP server remains configured.

The successful startup message is:

```text
Home Assistant MCP configuration is present
```

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

The configured `workspace` must be an existing directory. If it is unavailable, the add-on falls back to `/homeassistant`.

## Security recommendations

- Use a dedicated SSH key for this add-on.
- Keep private keys off the Home Assistant host.
- Remove obsolete public keys from `authorized_keys`.
- Do not expose port `2222` directly to the internet.
- Back up Home Assistant before making broad configuration changes.
