#!/bin/sh
set -eu

command -v patch >/dev/null
if ! command -v apply_patch >/dev/null; then
    printf '%s\n' \
        "error: run this test from a Codex tool execution context that exposes apply_patch" \
        >&2
    exit 2
fi
test "${CODEX_HOME:-}" = "/data/codex"
test -d /data/codex
test ! -L /root/.codex

test_dir=$(mktemp -d /root/codex-tooling-integration.XXXXXX)
trap 'rm -rf "$test_dir"' EXIT HUP INT TERM
cd "$test_dir"

printf '%s\n' before > apply-patch.txt
apply_patch <<'PATCH'
*** Begin Patch
*** Update File: apply-patch.txt
@@
-before
+after-apply-patch
*** End Patch
PATCH
test "$(cat apply-patch.txt)" = "after-apply-patch"

printf '%s\n' before > unified-diff.txt
cat > unified.diff <<'DIFF'
--- unified-diff.txt
+++ unified-diff.txt
@@ -1 +1 @@
-before
+after-patch
DIFF
patch -p0 < unified.diff
test "$(cat unified-diff.txt)" = "after-patch"

printf '%s\n' "tooling_integration=ok"
