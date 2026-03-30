#!/usr/bin/env python3
"""Validate Claude Code plugin marketplace structure.

Checks:
- marketplace.json: required fields, valid structure, source paths exist
- plugin.json: required fields, kebab-case names, valid JSON
- Skills, agents, commands have valid YAML frontmatter with required fields
- Every skill folder has a SKILL.md
- User-invocable skills appear in skill-enforcer.sh (warning)
- Config files (JSON, TOML) are valid
- allowed-tools in commands uses list format
"""

from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path

try:
    import frontmatter
except ImportError:
    print("ERROR: pip install python-frontmatter", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent

KEBAB_CASE_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

MARKETPLACE_REQUIRED_FIELDS = ["name", "owner", "plugins"]
MARKETPLACE_OWNER_REQUIRED = ["name"]
MARKETPLACE_PLUGIN_REQUIRED = ["name", "source"]

PLUGIN_JSON_REQUIRED = ["name", "description", "version"]

# Glob patterns relative to each plugin directory
REQUIRED_FIELDS: dict[str, dict[str, str | list[str]]] = {
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


def validate_marketplace_json() -> tuple[list[str], list[str]]:
    """Validate .claude-plugin/marketplace.json structure."""
    errors = []
    warnings = []
    mp_path = ROOT / ".claude-plugin" / "marketplace.json"

    if not mp_path.exists():
        errors.append("ERROR: .claude-plugin/marketplace.json not found")
        return errors, warnings

    try:
        data = json.loads(mp_path.read_text())
    except json.JSONDecodeError as e:
        errors.append(f"ERROR: marketplace.json: invalid JSON: {e}")
        return errors, warnings

    for field in MARKETPLACE_REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"ERROR: marketplace.json: missing required field '{field}'")

    # Owner validation
    owner = data.get("owner", {})
    for field in MARKETPLACE_OWNER_REQUIRED:
        if field not in owner:
            errors.append(f"ERROR: marketplace.json: owner missing '{field}'")

    # Name validation
    name = data.get("name", "")
    if name and not KEBAB_CASE_RE.match(name):
        errors.append(f"ERROR: marketplace.json: name '{name}' is not kebab-case")

    # Metadata warnings
    metadata = data.get("metadata", {})
    if not metadata.get("description"):
        warnings.append("WARNING: marketplace.json: no metadata.description")
    if not metadata.get("version"):
        warnings.append("WARNING: marketplace.json: no metadata.version")

    # Plugin entries
    plugins = data.get("plugins", [])
    if not plugins:
        warnings.append("WARNING: marketplace.json: no plugins defined")

    seen_names: set[str] = set()
    for i, plugin in enumerate(plugins):
        prefix = f"marketplace.json: plugins[{i}]"

        for field in MARKETPLACE_PLUGIN_REQUIRED:
            if field not in plugin:
                errors.append(f"ERROR: {prefix}: missing required field '{field}'")

        pname = plugin.get("name", "")
        if pname:
            if not KEBAB_CASE_RE.match(pname):
                errors.append(f"ERROR: {prefix}: name '{pname}' is not kebab-case")
            if pname in seen_names:
                errors.append(f"ERROR: {prefix}: duplicate name '{pname}'")
            seen_names.add(pname)

        # Validate source path exists for relative paths
        source = plugin.get("source", "")
        if isinstance(source, str) and source.startswith("./"):
            source_path = ROOT / source
            if not source_path.is_dir():
                errors.append(f"ERROR: {prefix}: source path '{source}' does not exist")

        if not plugin.get("description"):
            warnings.append(f"WARNING: {prefix}: no description")

    return errors, warnings


def validate_plugin_jsons() -> tuple[list[str], list[str]]:
    """Validate all plugin.json files under plugins/."""
    errors = []
    warnings = []
    plugins_dir = ROOT / "plugins"

    if not plugins_dir.is_dir():
        errors.append("ERROR: plugins/ directory not found")
        return errors, warnings

    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir() or plugin_dir.name.startswith("."):
            continue

        pj = plugin_dir / ".claude-plugin" / "plugin.json"
        rel = pj.relative_to(ROOT)

        if not pj.exists():
            warnings.append(f"WARNING: {rel}: plugin.json not found")
            continue

        try:
            data = json.loads(pj.read_text())
        except json.JSONDecodeError as e:
            errors.append(f"ERROR: {rel}: invalid JSON: {e}")
            continue

        for field in PLUGIN_JSON_REQUIRED:
            if field not in data:
                errors.append(f"ERROR: {rel}: missing required field '{field}'")

        pname = data.get("name", "")
        if pname and not KEBAB_CASE_RE.match(pname):
            errors.append(f"ERROR: {rel}: name '{pname}' is not kebab-case")

        # Name should match directory name
        if pname and pname != plugin_dir.name:
            dirname = plugin_dir.name
            warnings.append(
                f"WARNING: {rel}: name '{pname}' doesn't match directory '{dirname}'"
            )

    return errors, warnings


def validate_frontmatter(config_type: str, spec: dict) -> list[str]:
    """Validate YAML frontmatter in markdown files across all plugins."""
    errors = []
    pattern = spec["glob"]
    required = spec["required"]

    # Search in plugins/*/<pattern> and at root level
    search_patterns = [
        f"plugins/*/{pattern}",
        pattern,
    ]

    files = []
    for sp in search_patterns:
        files.extend(sorted(ROOT.glob(sp)))

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
    """Check every skill folder has a SKILL.md across all plugins."""
    errors = []

    # Check plugins/*/skills/
    plugins_dir = ROOT / "plugins"
    if plugins_dir.is_dir():
        for plugin_dir in sorted(plugins_dir.iterdir()):
            if not plugin_dir.is_dir() or plugin_dir.name.startswith("."):
                continue
            skills_dir = plugin_dir / "skills"
            if not skills_dir.is_dir():
                continue
            for d in sorted(skills_dir.iterdir()):
                if not d.is_dir() or d.name.startswith("."):
                    continue
                skill_md = d / "SKILL.md"
                if not skill_md.exists():
                    rel = d.relative_to(ROOT)
                    errors.append(f"ERROR: {rel}/ missing SKILL.md")

    # Also check root-level skills/ if it exists
    skills_dir = ROOT / "skills"
    if skills_dir.is_dir():
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

    # Find skill-enforcer.sh in plugins/dev-workflow/hooks/ or hooks/
    enforcer = ROOT / "plugins" / "dev-workflow" / "hooks" / "skill-enforcer.sh"
    if not enforcer.exists():
        enforcer = ROOT / "hooks" / "skill-enforcer.sh"
    if not enforcer.exists():
        return warnings

    enforcer_text = enforcer.read_text()

    # Scan all skill directories across plugins
    plugins_dir = ROOT / "plugins"
    if not plugins_dir.is_dir():
        return warnings

    for plugin_dir in sorted(plugins_dir.iterdir()):
        if not plugin_dir.is_dir() or plugin_dir.name.startswith("."):
            continue
        skills_dir = plugin_dir / "skills"
        if not skills_dir.is_dir():
            continue
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

    # Search plugins/*/commands/ and root commands/
    search_dirs = [ROOT / "commands"]
    plugins_dir = ROOT / "plugins"
    if plugins_dir.is_dir():
        for plugin_dir in sorted(plugins_dir.iterdir()):
            if plugin_dir.is_dir() and not plugin_dir.name.startswith("."):
                cmd_dir = plugin_dir / "commands"
                if cmd_dir.is_dir():
                    search_dirs.append(cmd_dir)

    for commands_dir in search_dirs:
        if not commands_dir.is_dir():
            continue
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

    # Check expected keys in root-level configs
    for filename, expected_keys in EXPECTED_JSON_KEYS.items():
        # Search root and plugins/*/
        paths_to_check = [ROOT / filename]
        plugins_dir = ROOT / "plugins"
        if plugins_dir.is_dir():
            for plugin_dir in sorted(plugins_dir.iterdir()):
                if plugin_dir.is_dir() and not plugin_dir.name.startswith("."):
                    paths_to_check.append(plugin_dir / filename)

        for path in paths_to_check:
            if not path.exists():
                continue
            rel = path.relative_to(ROOT)
            try:
                data = json.loads(path.read_text())
            except json.JSONDecodeError as e:
                errors.append(f"ERROR: {rel}: invalid JSON: {e}")
                continue

            for key in expected_keys:
                if key not in data:
                    errors.append(f"WARNING: {rel}: missing expected key '{key}'")

    return errors


def validate_toml_files() -> list[str]:
    """Validate all TOML files."""
    errors = []
    for path in sorted(ROOT.glob("**/*.toml")):
        rel = path.relative_to(ROOT)
        # Skip .git and .venv directories
        if ".git" in str(rel) or ".venv" in str(rel):
            continue
        try:
            tomllib.load(path.open("rb"))
        except Exception as e:
            errors.append(f"ERROR: {rel}: invalid TOML: {e}")

    return errors


def main() -> int:
    all_errors: list[str] = []
    all_warnings: list[str] = []

    # Marketplace validation
    mp_errors, mp_warnings = validate_marketplace_json()
    all_errors.extend(mp_errors)
    all_warnings.extend(mp_warnings)

    # Plugin.json validation
    pj_errors, pj_warnings = validate_plugin_jsons()
    all_errors.extend(pj_errors)
    all_warnings.extend(pj_warnings)

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
