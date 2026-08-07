#!/bin/sh
set -eu

repository_dir=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
source_dir="$repository_dir/codex_cli"
target_dir=${1:-/addons/codex_cli}

case "$target_dir" in
    /addons/*) ;;
    *)
        echo "Refusing target outside /addons: $target_dir" >&2
        exit 2
        ;;
esac

if [ ! -f "$source_dir/config.yaml" ] || [ ! -f "$source_dir/Dockerfile" ]; then
    echo "App source is incomplete: $source_dir" >&2
    exit 2
fi

mkdir -p "$target_dir"

for file in DOCS.md Dockerfile README.md config.yaml icon.png logo.png; do
    install -m 0644 "$source_dir/$file" "$target_dir/$file"
done

for file in run.sh init_codex.py codex-ha; do
    install -m 0755 "$source_dir/$file" "$target_dir/$file"
done

echo "Installed Codex CLI SSH source in $target_dir"
echo "Reload the Home Assistant app store, then rebuild the local app."
