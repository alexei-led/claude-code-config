#!/usr/bin/env python3
"""Generate AGENTS.md from flat/skills-codex/ skill overlays.

Walks flat/skills-codex/*/SKILL.md, reads frontmatter (name, description),
resolves symlinks to determine plugin grouping, and emits a categorized
AGENTS.md at the repository root.

Usage:
  scripts/generate-agents-md.py          # sync (build/update AGENTS.md)
  scripts/generate-agents-md.py --check  # exit 1 if AGENTS.md is stale
  scripts/generate-agents-md.py --hook   # sync + git add
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

try:
    import frontmatter
except ImportError:
    print("ERROR: pip install python-frontmatter", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
FLAT_SKILLS = ROOT / "flat" / "skills-codex"
OUTPUT = ROOT / "AGENTS.md"

# Plugin directory name → display title (ordered)
PLUGIN_TITLES: dict[str, str] = {
    "dev-workflow": "Development Workflow",
    "go-dev": "Go Development",
    "python-dev": "Python Development",
    "typescript-dev": "TypeScript Development",
    "web-dev": "Web Development",
    "infra-ops": "Infrastructure & Operations",
    "dev-tools": "Developer Tools",
    "spec-system": "Spec-Driven Development",
    "testing-e2e": "End-to-End Testing",
}


def resolve_plugin(skill_link: Path) -> str:
    """Resolve a flat/skills-codex/<skill> symlink to its plugin name.

    Symlink targets look like: ../../plugins/<plugin>/skills-codex/<skill>
    """
    target = skill_link.resolve()
    parts = target.parts
    try:
        idx = parts.index("plugins")
        return parts[idx + 1]
    except (ValueError, IndexError):
        return "unknown"


def first_sentence(text: str) -> str:
    """Extract concise description from a skill's description field."""
    result = text
    # Cut at common continuation patterns
    for sep in [
        ". Use ",
        ". Triggers ",
        ". Auto-detects ",
        ". Not for ",
        ". Includes ",
        ". Supports ",
        ". Covers ",
        ". Emphasizes ",
    ]:
        idx = result.find(sep)
        if idx != -1:
            result = result[:idx]
            break
    else:
        # First period-space boundary
        idx = result.find(". ")
        if idx != -1:
            result = result[: idx + 1]
    result = result.rstrip(".")
    # Cap long descriptions at first em-dash clause
    if len(result) > 100 and " — " in result:
        result = result[: result.index(" — ")]
    # Hard cap: truncate at last word boundary
    if len(result) > 100:
        result = result[:97].rsplit(" ", 1)[0] + "..."
    return result


def collect_skills() -> dict[str, list[tuple[str, str]]]:
    """Collect skills grouped by plugin.

    Returns: {plugin_name: [(skill_name, description), ...]}
    """
    if not FLAT_SKILLS.is_dir():
        return {}

    groups: dict[str, list[tuple[str, str]]] = {}

    for skill_dir in sorted(FLAT_SKILLS.iterdir()):
        if not skill_dir.is_symlink() and not skill_dir.is_dir():
            continue

        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue

        plugin = resolve_plugin(skill_dir)
        try:
            post = frontmatter.load(str(skill_md))
        except Exception:
            continue

        name = str(post.get("name", skill_dir.name))
        desc = first_sentence(str(post.get("description", "")))

        groups.setdefault(plugin, []).append((name, desc))

    return groups


def build_content(groups: dict[str, list[tuple[str, str]]]) -> str:
    """Build AGENTS.md content from grouped skills."""
    total = sum(len(skills) for skills in groups.values())
    plugin_count = len(groups)

    lines: list[str] = []
    lines.append("# cc-thingz Skills")
    lines.append("")
    lines.append(
        "A Claude Code plugin suite with portable skill export for Codex CLI, "
        "Gemini CLI, and AGENTS.md-compatible tools."
    )
    lines.append("")
    lines.append(
        f"{total} skills across {plugin_count} plugins — code review, "
        "language tooling, infrastructure, testing, and developer utilities."
    )
    lines.append("")

    for plugin_key, title in PLUGIN_TITLES.items():
        skills = groups.get(plugin_key, [])
        if not skills:
            continue

        lines.append(f"## {title}")
        lines.append("")
        lines.append("| Skill | Description |")
        lines.append("|-------|-------------|")
        for name, desc in sorted(skills, key=lambda s: s[0]):
            lines.append(f"| {name} | {desc} |")
        lines.append("")

    return "\n".join(lines)


def compute_desired_content() -> str:
    """Compute the desired AGENTS.md content."""
    groups = collect_skills()
    return build_content(groups)


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "sync"
    content = compute_desired_content()

    if mode == "--check":
        if not OUTPUT.exists():
            print("AGENTS.md missing")
            print("Run: uv run python scripts/generate-agents-md.py")
            return 1
        current = OUTPUT.read_text()
        if current != content:
            print("AGENTS.md out of sync")
            print("Run: uv run python scripts/generate-agents-md.py")
            return 1
        print("AGENTS.md in sync")
        return 0

    OUTPUT.write_text(content)

    if mode == "--hook":
        subprocess.run(["git", "add", str(OUTPUT)], cwd=ROOT, check=False)
        print("AGENTS.md synced (staged)")
    else:
        print("AGENTS.md synced")

    return 0


if __name__ == "__main__":
    sys.exit(main())
