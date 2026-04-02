#!/bin/bash
# Sync flat/ symlinks with plugin contents.
#
# flat/ provides a unified view of all plugin skills/agents/hooks/commands/scripts
# for tools that need flat directory access (chezmoi, Codex CLI, Gemini CLI).
#
# Usage:
#   scripts/generate-flat.sh          # sync flat/ (add/remove/update links)
#   scripts/generate-flat.sh --check  # exit 1 if flat/ is out of sync (for CI)
#   scripts/generate-flat.sh --hook   # sync + git add flat/ (for pre-commit)
set -euo pipefail
cd "$(dirname "$0")/.."

MODE="${1:-sync}"

# Build desired symlink map: flat_path -> target
declare -A desired

for component in skills skills-codex agents hooks commands scripts; do
	for src in plugins/*/"$component"; do
		[ -d "$src" ] || continue
		plugin_rel="../../$src"
		for item in "$src"/*; do
			[ -e "$item" ] || continue
			name="$(basename "$item")"
			desired["flat/$component/$name"]="$plugin_rel/$name"
		done
	done
done

desired["flat/hook-config.json"]="../plugins/dev-workflow/hook-config.json"

# Detect differences
stale=()
while IFS= read -r link; do
	if [[ -z "${desired[$link]+x}" ]]; then
		stale+=("$link")
	fi
done < <(find flat -type l 2>/dev/null | sort)

missing=()
wrong=()
for flat_path in "${!desired[@]}"; do
	target="${desired[$flat_path]}"
	if [ -L "$flat_path" ]; then
		current="$(readlink "$flat_path")"
		if [ "$current" != "$target" ]; then
			wrong+=("$flat_path")
		fi
	else
		missing+=("$flat_path")
	fi
done

total=$((${#stale[@]} + ${#missing[@]} + ${#wrong[@]}))

# Check mode: report only, no modifications
if [ "$MODE" = "--check" ]; then
	if [ "$total" -gt 0 ]; then
		echo "flat/ is out of sync: +${#missing[@]} -${#stale[@]} ~${#wrong[@]}"
		echo "Run: scripts/generate-flat.sh"
		exit 1
	fi
	echo "flat/ is in sync"
	exit 0
fi

# Apply changes
for link in "${stale[@]}"; do
	rm "$link"
done
find flat -type d -empty -delete 2>/dev/null || true

for flat_path in "${wrong[@]}"; do
	rm "$flat_path"
	ln -s "${desired[$flat_path]}" "$flat_path"
done

for flat_path in "${missing[@]}"; do
	mkdir -p "$(dirname "$flat_path")"
	ln -s "${desired[$flat_path]}" "$flat_path"
done

case "$MODE" in
--hook)
	if [ "$total" -gt 0 ]; then
		git add flat/
		echo "flat/ synced: +${#missing[@]} -${#stale[@]} ~${#wrong[@]} (staged)"
	fi
	;;
*)
	if [ "$total" -gt 0 ]; then
		echo "flat/ synced: +${#missing[@]} -${#stale[@]} ~${#wrong[@]}"
	else
		echo "flat/ already in sync"
	fi
	count=$(find flat -type l 2>/dev/null | wc -l | tr -d ' ')
	echo "$count symlinks total"
	;;
esac
