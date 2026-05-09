#!/bin/bash
# Link generated cc-thingz Pi exports into a Pi agent config directory.
# Dry-run by default. Pass --apply to modify files.
set -euo pipefail

usage() {
	cat <<'EOF'
Usage: scripts/install-pi-exports.sh [--apply] [--build] [--target-dir DIR]

Links:
  DIR/skills -> <repo>/flat/skills-pi
  DIR/agents -> <repo>/flat/agents-pi

Defaults:
  DIR = ${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}
  mode = dry-run

Options:
  --apply          Make changes. Without this, only prints the plan.
  --build          Run make pi-overlays pi-agents flat before linking.
  --target-dir DIR Override the Pi agent directory.
  -h, --help       Show this help.

Existing skills/agents paths are moved to timestamped backups before symlinking.
EOF
}

apply=0
build=0
target_dir="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"

while [[ $# -gt 0 ]]; do
	case "$1" in
	--apply)
		apply=1
		shift
		;;
	--build)
		build=1
		shift
		;;
	--target-dir)
		if [[ $# -lt 2 ]]; then
			echo "ERROR: --target-dir needs a value" >&2
			exit 2
		fi
		target_dir="$2"
		shift 2
		;;
	-h | --help)
		usage
		exit 0
		;;
	*)
		echo "ERROR: unknown argument: $1" >&2
		usage >&2
		exit 2
		;;
	esac
done

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
skills_src="$repo_root/flat/skills-pi"
agents_src="$repo_root/flat/agents-pi"
timestamp="$(date +%Y%m%d%H%M%S)"

if [[ "$build" -eq 1 ]]; then
	if [[ "$apply" -eq 1 ]]; then
		make -C "$repo_root" pi-overlays pi-agents flat
	else
		echo "DRY-RUN build: make -C $repo_root pi-overlays pi-agents flat"
	fi
fi

for required in "$skills_src" "$agents_src"; do
	if [[ ! -d "$required" ]]; then
		echo "ERROR: missing generated export: $required" >&2
		echo "Run: make -C '$repo_root' pi-overlays pi-agents flat" >&2
		exit 1
	fi
done

if command -v pi >/dev/null 2>&1; then
	if ! pi list 2>/dev/null | grep -Eq 'pi-subagents|@tintinweb/pi-subagents'; then
		echo "WARNING: pi-subagents not found in 'pi list'. Agents need pi-subagents installed." >&2
		echo "Install one of:" >&2
		echo "  pi install npm:@tintinweb/pi-subagents" >&2
		echo "  pi install git:github.com/alexei-led/pi-subagents@fix/pi-skill-discovery" >&2
	fi
fi

link_export() {
	local name="$1"
	local source="$2"
	local target="$target_dir/$name"

	if [[ -L "$target" && "$(readlink "$target")" == "$source" ]]; then
		echo "OK: $target -> $source"
		return
	fi

	if [[ "$apply" -eq 0 ]]; then
		if [[ -e "$target" || -L "$target" ]]; then
			echo "DRY-RUN: mv '$target' '$target.backup.$timestamp'"
		fi
		echo "DRY-RUN: ln -s '$source' '$target'"
		return
	fi

	mkdir -p "$target_dir"
	if [[ -e "$target" || -L "$target" ]]; then
		mv "$target" "$target.backup.$timestamp"
	fi
	ln -s "$source" "$target"
	echo "LINKED: $target -> $source"
}

link_export skills "$skills_src"
link_export agents "$agents_src"

if [[ "$apply" -eq 0 ]]; then
	echo "No changes made. Re-run with --apply to link Pi exports."
else
	echo "Done. Restart Pi or run /reload in the TUI."
fi
