#!/bin/sh
set -eu

command -v patch >/dev/null
command -v tmux >/dev/null
command -v ttyd >/dev/null
command -v codex-cleanup >/dev/null
test "${CODEX_HOME:-}" = "/data/codex"
test -d /data/codex
test -d /config
test ! -L /root/.codex

printf '%s\n' "container_smoke=ok"
