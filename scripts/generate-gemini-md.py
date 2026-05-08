#!/usr/bin/env python3
"""Generate GEMINI.md from flat/skills-codex skill overlays."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FLAT_SKILLS = ROOT / "flat" / "skills-codex"
OUTPUT = ROOT / "GEMINI.md"

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
    target = skill_link.resolve()
    parts = target.parts
    try:
        idx = parts.index("plugins")
        return parts[idx + 1]
    except (ValueError, IndexError):
        return "unknown"


def collect_skills() -> dict[str, list[str]]:
    if not FLAT_SKILLS.is_dir():
        return {}

    groups: dict[str, list[str]] = {}
    for skill_dir in sorted(FLAT_SKILLS.iterdir()):
        if not skill_dir.is_symlink() and not skill_dir.is_dir():
            continue
        if not (skill_dir / "SKILL.md").exists():
            continue
        plugin = resolve_plugin(skill_dir)
        groups.setdefault(plugin, []).append(skill_dir.name)
    return groups


def build_content(groups: dict[str, list[str]]) -> str:
    total = sum(len(skills) for skills in groups.values())
    lines = [
        "# cc-thingz Skills",
        "",
        "These skills provide domain-specific knowledge and workflows. They are "
        "optimized for non-Claude models and generated from `flat/skills-codex/`.",
        "",
        f"Total skills: {total}",
        "",
    ]

    for plugin_key, title in PLUGIN_TITLES.items():
        skills = groups.get(plugin_key, [])
        if not skills:
            continue
        lines.append(f"## {title}")
        lines.append("")
        for skill in sorted(skills):
            lines.append(f"@flat/skills-codex/{skill}/SKILL.md")
        lines.append("")

    return "\n".join(lines)


def compute_desired_content() -> str:
    return build_content(collect_skills())


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "sync"
    content = compute_desired_content()

    if mode == "--check":
        if not OUTPUT.exists():
            print("GEMINI.md missing")
            print("Run: uv run python scripts/generate-gemini-md.py")
            return 1
        if OUTPUT.read_text() != content:
            print("GEMINI.md out of sync")
            print("Run: uv run python scripts/generate-gemini-md.py")
            return 1
        print("GEMINI.md in sync")
        return 0

    OUTPUT.write_text(content)

    if mode == "--hook":
        subprocess.run(["git", "add", str(OUTPUT)], cwd=ROOT, check=False)
        print("GEMINI.md synced (staged)")
    else:
        print("GEMINI.md synced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
