#!/usr/bin/env python3
"""Rewrite plugin manifests for private mirror repos.

Usage: python scripts/rewrite-mirror.py <owner>/<repo>

Runs in CI on mirror repos (condition-gated in workflow). Safe to run
on the source repo — exits immediately when repo matches SOURCE_REPO.
"""

import glob
import json
import os
import sys

SOURCE_REPO = "alexei-led/cc-thingz"
SOURCE_URL = f"https://github.com/{SOURCE_REPO}"

# Per-mirror plugin rename maps: dir-name → new plugin name
MIRROR_NAMES: dict[str, dict[str, str]] = {
    "cc-forge": {
        "dev-workflow": "review-lint-commit",
        "testing-e2e": "playwright-e2e",
        "python-dev": "python-3-dev",
        "dev-tools": "cli-research-tools",
        "spec-system": "spec-driven-planning",
        "web-dev": "vanilla-web-htmx",
        "infra-ops": "k8s-terraform-ops",
        "typescript-dev": "typescript-react-dev",
    },
}


def main() -> None:
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <owner>/<repo>", file=sys.stderr)
        sys.exit(1)

    repo = sys.argv[1]
    if repo == SOURCE_REPO:
        print("Source repo — nothing to rewrite.")
        return

    repo_name = repo.split("/")[-1]
    mirror_url = f"https://github.com/{repo}"
    name_map = MIRROR_NAMES.get(repo_name, {})

    # plugin.json files
    for path in sorted(glob.glob("plugins/*/.claude-plugin/plugin.json")):
        plugin_dir = os.path.basename(os.path.dirname(os.path.dirname(path)))
        with open(path) as f:
            data = json.load(f)
        if plugin_dir in name_map:
            data["name"] = name_map[plugin_dir]
        data["repository"] = mirror_url
        data["homepage"] = data["homepage"].replace(SOURCE_URL, mirror_url)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
            f.write("\n")
        print(f"  {path}")

    # marketplace.json
    mp_path = ".claude-plugin/marketplace.json"
    with open(mp_path) as f:
        data = json.load(f)
    data["metadata"]["homepage"] = mirror_url
    data["metadata"]["repository"] = mirror_url
    for plugin in data["plugins"]:
        orig_name = plugin["name"]
        if orig_name in name_map:
            plugin["name"] = name_map[orig_name]
        plugin["repository"] = mirror_url
        if "homepage" in plugin:
            plugin["homepage"] = plugin["homepage"].replace(SOURCE_URL, mirror_url)
    with open(mp_path, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"  {mp_path}")

    print(f"✓ Rewrote manifests for {repo}")


if __name__ == "__main__":
    main()
