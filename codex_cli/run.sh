#!/usr/bin/env bash
source /usr/lib/bashio/bashio.sh
set -euo pipefail

readonly OPTIONS_FILE="/data/options.json"
readonly AUTHORIZED_KEYS="/root/.ssh/authorized_keys"
export CODEX_HOME="/data/codex"
export HOME="/root"

mkdir -p /root/.ssh /run/sshd "${CODEX_HOME}"
chmod 700 /root/.ssh "${CODEX_HOME}"

python3 - "$OPTIONS_FILE" "$AUTHORIZED_KEYS" <<'PY'
import json
import os
import sys
options_path, keys_path = sys.argv[1:]
with open(options_path, "r", encoding="utf-8") as handle:
    options = json.load(handle)
keys = options.get("authorized_keys") or []
keys = [item.strip() for item in keys if isinstance(item, str) and item.strip()]
if not keys:
    print("[error] Configure at least one SSH public key in authorized_keys.", file=sys.stderr)
    raise SystemExit(2)
with open(keys_path, "w", encoding="utf-8", newline="\n") as handle:
    handle.write("\n".join(keys) + "\n")
os.chmod(keys_path, 0o600)
PY

python3 /usr/local/libexec/init_codex.py "${OPTIONS_FILE}"

if [[ -e /root/.codex || -L /root/.codex ]]; then
    bashio::log.error "/root/.codex must not exist; CODEX_HOME is ${CODEX_HOME}"
    exit 1
fi

for type in rsa ecdsa ed25519; do
    persistent="/data/ssh_host_${type}_key"
    target="/etc/ssh/ssh_host_${type}_key"
    if [[ ! -f "${persistent}" ]]; then
        ssh-keygen -q -N "" -t "${type}" -f "${persistent}"
    fi
    cp "${persistent}" "${target}"
    cp "${persistent}.pub" "${target}.pub"
done

cat > /etc/ssh/sshd_config <<'SSHD'
Port 22
ListenAddress 0.0.0.0
Protocol 2
HostKey /etc/ssh/ssh_host_rsa_key
HostKey /etc/ssh/ssh_host_ecdsa_key
HostKey /etc/ssh/ssh_host_ed25519_key
PermitRootLogin prohibit-password
PubkeyAuthentication yes
PasswordAuthentication no
KbdInteractiveAuthentication no
ChallengeResponseAuthentication no
PermitEmptyPasswords no
AuthorizedKeysFile .ssh/authorized_keys
AllowTcpForwarding yes
AllowAgentForwarding no
GatewayPorts no
X11Forwarding no
PermitTunnel no
PermitUserEnvironment no
ClientAliveInterval 30
ClientAliveCountMax 3
TCPKeepAlive yes
UseDNS no
PrintMotd no
LogLevel INFO
Subsystem sftp internal-sftp
SSHD

workspace="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("workspace") or "/config")' "${OPTIONS_FILE}")"
if [[ ! -d "${workspace}" ]]; then
    bashio::log.warning "Configured workspace ${workspace} does not exist; using /config"
    workspace="/config"
fi
printf '%s\n' \
    'export CODEX_HOME=/data/codex' \
    'export HOME=/root' \
    'export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin' \
    "cd $(printf '%q' "${workspace}") 2>/dev/null || cd /config 2>/dev/null || true" \
    > /root/.profile
cp /root/.profile /root/.bash_profile

bashio::log.info "Codex: $(codex --version)"
bashio::log.info "Node.js: $(node --version)"
bashio::log.info "SSH server ready on container port 22"
bashio::log.info "Workspace: ${workspace}"
bashio::log.info "Persistent Codex home: ${CODEX_HOME}"
bashio::log.info "Sandbox-safe Codex home: /root/.codex is intentionally absent"
bashio::log.warning "This app has privileged Supervisor, Docker, hardware, and writable data-directory access."

exec /usr/sbin/sshd -D -e
