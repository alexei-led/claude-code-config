#!/bin/bash
# Regenerates flat/ directory from plugin contents.
# flat/ provides a unified view of all plugin skills/agents/hooks/commands
# for tools that need flat directory access (chezmoi, Codex CLI, Gemini CLI).
set -euo pipefail
cd "$(dirname "$0")/.."

rm -rf flat
for component in skills agents hooks commands scripts; do
  mkdir -p "flat/$component"
  for src in plugins/*/"$component"; do
    [ -d "$src" ] || continue
    plugin_rel="../../$src"
    for item in "$src"/*; do
      [ -e "$item" ] || continue
      ln -s "$plugin_rel/$(basename "$item")" "flat/$component/$(basename "$item")"
    done
  done
done

# Link hook-config.json
ln -s ../plugins/dev-workflow/hook-config.json flat/hook-config.json

echo "flat/ generated:"
find flat -maxdepth 2 -type l | sort | wc -l
echo "symlinks total"
