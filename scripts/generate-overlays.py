#!/usr/bin/env python3
"""Build platform-optimized skill overlays for Codex CLI and Gemini CLI.

For each skill in plugins/*/skills/:
- RED (SKILL.codex.md exists): copy overlay verbatim to skills-codex/
- YELLOW (has CC-ONLY markers): strip CC frontmatter + CC-ONLY body blocks
- GREEN (neither): strip CC frontmatter only (body unchanged)

All non-RED skills get a platform preamble injected (agentic anchors for
o3/codex-1 and Gemini models). The output serves both Codex and Gemini —
XML is neutral-to-beneficial on all target models.

Usage:
  scripts/generate-overlays.py          # sync (build/update skills-codex/)
  scripts/generate-overlays.py --check  # exit 1 if outputs are stale
  scripts/generate-overlays.py --hook   # sync + git add
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

try:
    import frontmatter
except ImportError:
    print("ERROR: pip install python-frontmatter", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent

# CC-specific frontmatter keys to strip (entire key removed)
CC_ONLY_FM_KEYS = {
    "context",
    "model",
    "agent",
    "memory",
    "disable-model-invocation",
    "user-invocable",
}

# CC-specific tool patterns to remove from allowed-tools lists
CC_ONLY_TOOL_PATTERNS = [
    re.compile(r"^Task$"),
    re.compile(r"^TaskOutput$"),
    re.compile(r"^TaskCreate$"),
    re.compile(r"^TaskUpdate$"),
    re.compile(r"^TaskList$"),
    re.compile(r"^TodoWrite$"),
    re.compile(r"^AskUserQuestion$"),
    re.compile(r"^Agent$"),
    re.compile(r"^mcp__plugin_claude-mem"),
    re.compile(r"^mcp__morphllm"),
]

CC_ONLY_BEGIN = "<!-- CC-ONLY: begin -->"
CC_ONLY_END = "<!-- CC-ONLY: end -->"

# Platform preamble injected at the top of skill body
PREAMBLE_PATH = ROOT / "scripts" / "preambles" / "platform.md"


def strip_cc_frontmatter(metadata: dict) -> dict:
    """Remove CC-specific keys and tool entries from frontmatter."""
    out = {}
    for key, value in metadata.items():
        if key in CC_ONLY_FM_KEYS:
            continue
        if key == "allowed-tools" and isinstance(value, list):
            filtered = [
                t for t in value if not any(p.match(t) for p in CC_ONLY_TOOL_PATTERNS)
            ]
            if filtered:
                out[key] = filtered
            continue
        out[key] = value
    return out


def strip_cc_body(body: str) -> str:
    """Remove <!-- CC-ONLY: begin --> ... <!-- CC-ONLY: end --> blocks."""
    lines = body.split("\n")
    result: list[str] = []
    inside_cc_only = False
    for line in lines:
        if CC_ONLY_BEGIN in line:
            inside_cc_only = True
            continue
        if CC_ONLY_END in line:
            inside_cc_only = False
            continue
        if not inside_cc_only:
            result.append(line)
    return "\n".join(result)


def has_cc_only_markers(body: str) -> bool:
    """Check if body contains CC-ONLY markers."""
    return CC_ONLY_BEGIN in body


def load_preamble() -> str:
    """Load platform preamble text."""
    if PREAMBLE_PATH.exists():
        return PREAMBLE_PATH.read_text().strip()
    return ""


def build_stripped_content(source_path: Path, preamble: str = "") -> str:
    """Build stripped SKILL.md content from a CC source."""
    post = frontmatter.load(str(source_path))
    metadata = strip_cc_frontmatter(dict(post.metadata))
    body = strip_cc_body(post.content)
    if preamble:
        body = preamble + "\n\n" + body
    out = frontmatter.Post(body, **metadata)
    return frontmatter.dumps(out) + "\n"


def compute_desired_state() -> dict[Path, str]:
    """Compute desired state for all skills-codex/ outputs.

    Returns dict mapping output path -> content string.
    All outputs are files (no symlinks) to ensure CC-specific
    frontmatter is always stripped.
    """
    desired: dict[Path, str] = {}
    preamble = load_preamble()
    plugins_dir = ROOT / "plugins"
    if not plugins_dir.is_dir():
        return desired

    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir() or plugin_dir.name.startswith("."):
            continue
        skills_dir = plugin_dir / "skills"
        if not skills_dir.is_dir():
            continue

        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir() or skill_dir.name.startswith("."):
                continue

            source = skill_dir / "SKILL.md"
            if not source.exists():
                continue

            out_dir = plugin_dir / "skills-codex" / skill_dir.name
            out_file = out_dir / "SKILL.md"

            overlay = skill_dir / "SKILL.codex.md"
            if overlay.exists():
                # RED: copy overlay verbatim (already optimized)
                desired[out_file] = overlay.read_text()
            else:
                # GREEN + YELLOW: strip CC frontmatter + body,
                # inject platform preamble
                desired[out_file] = build_stripped_content(source, preamble)

    return desired


def sync(desired: dict[Path, str]) -> int:
    """Apply desired state. Returns count of changes."""
    changes = 0

    # Remove stale files in skills-codex/ dirs
    plugins_dir = ROOT / "plugins"
    if plugins_dir.is_dir():
        for plugin_dir in sorted(plugins_dir.iterdir()):
            if not plugin_dir.is_dir() or plugin_dir.name.startswith("."):
                continue
            codex_dir = plugin_dir / "skills-codex"
            if not codex_dir.is_dir():
                continue
            for skill_out_dir in sorted(codex_dir.iterdir()):
                skill_md = skill_out_dir / "SKILL.md"
                if skill_md.exists() and skill_md not in desired:
                    skill_md.unlink()
                    changes += 1
                if skill_out_dir.is_dir() and not any(skill_out_dir.iterdir()):
                    skill_out_dir.rmdir()

    # Create/update outputs
    for out_path, content in sorted(desired.items()):
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Remove stale symlinks (from previous GREEN strategy)
        if out_path.is_symlink():
            out_path.unlink()

        if out_path.exists() and out_path.read_text() == content:
            continue
        out_path.write_text(content)
        changes += 1

    return changes


def check(desired: dict[Path, str]) -> int:
    """Check if outputs match desired state. Returns count of mismatches."""
    mismatches = 0

    for out_path, content in sorted(desired.items()):
        if out_path.is_symlink():
            print(f"  stale symlink: {out_path.relative_to(ROOT)}")
            mismatches += 1
        elif not out_path.exists():
            print(f"  missing: {out_path.relative_to(ROOT)}")
            mismatches += 1
        elif out_path.read_text() != content:
            print(f"  stale: {out_path.relative_to(ROOT)}")
            mismatches += 1

    # Check for stale files not in desired
    plugins_dir = ROOT / "plugins"
    if plugins_dir.is_dir():
        for plugin_dir in sorted(plugins_dir.iterdir()):
            if not plugin_dir.is_dir() or plugin_dir.name.startswith("."):
                continue
            codex_dir = plugin_dir / "skills-codex"
            if not codex_dir.is_dir():
                continue
            for skill_out_dir in sorted(codex_dir.iterdir()):
                skill_md = skill_out_dir / "SKILL.md"
                if skill_md.exists() and skill_md not in desired:
                    print(f"  stale: {skill_md.relative_to(ROOT)}")
                    mismatches += 1

    return mismatches


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "sync"
    desired = compute_desired_state()

    if mode == "--check":
        mismatches = check(desired)
        if mismatches:
            print(f"skills-codex/ out of sync: {mismatches} issue(s)")
            print("Run: uv run python scripts/generate-overlays.py")
            return 1
        print(f"skills-codex/ in sync ({len(desired)} skills)")
        return 0

    changes = sync(desired)

    if mode == "--hook" and changes > 0:
        # Stage all skills-codex/ directories
        for plugin_dir in sorted((ROOT / "plugins").iterdir()):
            if not plugin_dir.is_dir() or plugin_dir.name.startswith("."):
                continue
            codex_dir = plugin_dir / "skills-codex"
            if codex_dir.is_dir():
                subprocess.run(
                    ["git", "add", str(codex_dir)],
                    cwd=ROOT,
                    check=False,
                )
        print(f"skills-codex/ synced: {changes} change(s) (staged)")
    elif changes > 0:
        print(f"skills-codex/ synced: {changes} change(s)")
    else:
        print(f"skills-codex/ already in sync ({len(desired)} skills)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
