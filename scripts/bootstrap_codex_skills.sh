#!/usr/bin/env bash

set -euo pipefail

DRY_RUN=0
INSTALL_LARK=1
INSTALL_PLUGINS=1

usage() {
  cat <<'EOF'
Usage: scripts/bootstrap_codex_skills.sh [options]

Install the AtomFlow skill catalog and the supported companion suites into Codex.

Options:
  --dry-run       Print commands without changing the machine.
  --skip-lark     Do not install the official Lark skill suite.
  --skip-plugins  Do not install optional Codex Marketplace plugins.
  -h, --help      Show this help.
EOF
}

while (($#)); do
  case "$1" in
    --dry-run) DRY_RUN=1 ;;
    --skip-lark) INSTALL_LARK=0 ;;
    --skip-plugins) INSTALL_PLUGINS=0 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
  shift
done

run() {
  printf ' +'
  printf ' %q' "$@"
  printf '\n'
  if ((DRY_RUN == 0)); then
    "$@"
  fi
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Missing required command: $1" >&2
    exit 1
  fi
}

plugin_is_installed() {
  codex plugin list --json 2>/dev/null | grep -Fq "\"pluginId\": \"$1\""
}

install_plugin() {
  local plugin_id="$1"
  if plugin_is_installed "$plugin_id"; then
    echo " = plugin already installed: $plugin_id"
  else
    run codex plugin add "$plugin_id"
  fi
}

require_command npx
require_command codex

echo "Installing the complete AtomFlow-AI/skills catalog for Codex..."
run npx --yes skills add AtomFlow-AI/skills \
  --global --agent codex --yes --full-depth

if ((INSTALL_LARK == 1)); then
  echo "Installing the official Lark skill suite..."
  run npx --yes skills add larksuite/cli \
    --global --agent codex --yes --full-depth
fi

if ((INSTALL_PLUGINS == 1)); then
  echo "Installing optional Codex Marketplace plugins..."
  plugins=(
    github@openai-curated
    gmail@openai-curated
    build-web-apps@openai-curated
    build-web-data-visualization@openai-curated
    zotero@openai-curated
  )
  for plugin in "${plugins[@]}"; do
    install_plugin "$plugin"
  done
fi

echo
echo "Bootstrap complete. Restart Codex so newly installed skills are discovered."
if ((INSTALL_LARK == 1)); then
  echo "For Lark operations, install lark-cli if needed, then run: lark-cli auth login"
fi
echo "System and primary-runtime skills are supplied by Codex and are not copied by this script."

