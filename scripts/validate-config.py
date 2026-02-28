#!/usr/bin/env python3
"""Validate Claude Code configuration structure.

Checks:
- Skills, agents, commands have valid YAML frontmatter with required fields
- Every skill folder has a SKILL.md
- User-invocable skills appear in skill-enforcer.sh (warning)
- Config files (JSON, TOML) are valid
- allowed-tools in commands uses list format
"""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

try:
    import frontmatter
except ImportError:
    print("ERROR: pip install python-frontmatter", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FIELDS: dict[str, dict[str, list[str]]] = {
    "skill": {
        "glob": "skills/*/SKILL.md",
        "required": ["name", "description"],
    },
    "agent": {
        "glob": "agents/**/*.md",
        "required": ["name", "description", "tools"],
    },
    "command": {
        "glob": "commands/**/*.md",
        "required": ["description"],
    },
}

EXPECTED_JSON_KEYS = {
    "hook-config.json": ["file-protector", "smart-lint"],
}


def validate_frontmatter(config_type: str, spec: dict) -> list[str]:
    """Validate YAML frontmatter in markdown files."""
    errors = []
    pattern = spec["glob"]
    required = spec["required"]

    files = sorted(ROOT.glob(pattern))
    if not files:
        errors.append(f"WARNING: no {config_type} files found matching {pattern}")
        return errors

    for path in files:
        rel = path.relative_to(ROOT)

        # Skip .system/ skills (third-party)
        if ".system" in str(rel):
            continue

        try:
            post = frontmatter.load(path)
        except Exception as e:
            errors.append(f"ERROR: {rel}: invalid frontmatter: {e}")
            continue

        if not post.metadata:
            errors.append(f"ERROR: {rel}: no YAML frontmatter found")
            continue

        for field in required:
            if field not in post.metadata:
                errors.append(f"ERROR: {rel}: missing required field '{field}'")

    return errors


def validate_skill_folders() -> list[str]:
    """Check every skill folder has a SKILL.md."""
    errors = []
    skills_dir = ROOT / "skills"
    if not skills_dir.is_dir():
        return errors

    for d in sorted(skills_dir.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        skill_md = d / "SKILL.md"
        if not skill_md.exists():
            errors.append(f"ERROR: skills/{d.name}/ missing SKILL.md")

    return errors


def validate_enforcer_coverage() -> list[str]:
    """Warn if user-invocable skills aren't in skill-enforcer.sh."""
    warnings = []
    enforcer = ROOT / "hooks" / "skill-enforcer.sh"
    if not enforcer.exists():
        return warnings

    enforcer_text = enforcer.read_text()
    skills_dir = ROOT / "skills"
    if not skills_dir.is_dir():
        return warnings

    for d in sorted(skills_dir.iterdir()):
        if not d.is_dir() or d.name.startswith("."):
            continue
        skill_md = d / "SKILL.md"
        if not skill_md.exists():
            continue

        try:
            post = frontmatter.load(skill_md)
        except Exception:
            continue

        if post.metadata.get("user-invocable", False):
            # Check if skill name appears in enforcer
            skill_name = d.name
            if skill_name not in enforcer_text:
                warnings.append(
                    f"WARNING: user-invocable skill '{skill_name}' "
                    f"not found in skill-enforcer.sh"
                )

    return warnings


def validate_command_tools_format() -> list[str]:
    """Check allowed-tools in commands uses list format."""
    errors = []
    commands_dir = ROOT / "commands"
    if not commands_dir.is_dir():
        return errors

    for path in sorted(commands_dir.rglob("*.md")):
        rel = path.relative_to(ROOT)
        try:
            post = frontmatter.load(path)
        except Exception:
            continue

        tools = post.metadata.get("allowed-tools")
        if tools is not None and isinstance(tools, str):
            errors.append(
                f"ERROR: {rel}: allowed-tools should be a list, got string"
            )

    return errors


def validate_json_files() -> list[str]:
    """Validate JSON config files."""
    errors = []
    for filename, expected_keys in EXPECTED_JSON_KEYS.items():
        path = ROOT / filename
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            errors.append(f"ERROR: {filename}: invalid JSON: {e}")
            continue

        for key in expected_keys:
            if key not in data:
                errors.append(f"WARNING: {filename}: missing expected key '{key}'")

    return errors


def validate_toml_files() -> list[str]:
    """Validate all TOML files."""
    errors = []
    for path in sorted(ROOT.glob("**/*.toml")):
        rel = path.relative_to(ROOT)
        # Skip .git directory
        if ".git" in str(rel):
            continue
        try:
            tomllib.load(path.open("rb"))
        except Exception as e:
            errors.append(f"ERROR: {rel}: invalid TOML: {e}")

    return errors


def main() -> int:
    all_errors: list[str] = []
    all_warnings: list[str] = []

    # Frontmatter validation
    for config_type, spec in REQUIRED_FIELDS.items():
        results = validate_frontmatter(config_type, spec)
        for r in results:
            if r.startswith("WARNING"):
                all_warnings.append(r)
            else:
                all_errors.append(r)

    # Skill folder checks
    all_errors.extend(validate_skill_folders())

    # Enforcer coverage (warnings only)
    all_warnings.extend(validate_enforcer_coverage())

    # Command tools format
    all_errors.extend(validate_command_tools_format())

    # JSON validation
    results = validate_json_files()
    for r in results:
        if r.startswith("WARNING"):
            all_warnings.append(r)
        else:
            all_errors.append(r)

    # TOML validation
    all_errors.extend(validate_toml_files())

    # Report
    if all_warnings:
        for w in all_warnings:
            print(w)
        print()

    if all_errors:
        for e in all_errors:
            print(e)
        print(f"\n{len(all_errors)} error(s), {len(all_warnings)} warning(s)")
        return 1

    print(f"All checks passed ({len(all_warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
