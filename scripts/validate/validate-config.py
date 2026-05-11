#!/usr/bin/env python3
"""Validate the root marketplace and extension manifests.

After the unified compiler migration, all per-plugin manifests live under
``dist/`` and are generated from ``src/plugins/<plugin>/plugin.yaml``. This
validator only checks the three root manifests the compiler writes, plus
the AGENTS.md cross-target memory file. Source-side genericity is enforced
by ``validate_genericity.py``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


def _find_root(start: Path) -> Path:
    for parent in [start, *start.parents]:
        if (parent / "pyproject.toml").is_file():
            return parent
    raise RuntimeError(f"no pyproject.toml found above {start}")


ROOT = _find_root(Path(__file__).resolve())

CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
GEMINI_EXTENSION = ROOT / "gemini-extension.json"

MARKETPLACE_REQUIRED = ("name", "owner", "plugins")
MARKETPLACE_OWNER_REQUIRED = ("name",)
MARKETPLACE_PLUGIN_REQUIRED = ("name", "source")
CODEX_MARKETPLACE_REQUIRED = ("name", "plugins")
GEMINI_EXTENSION_REQUIRED = ("name", "version", "description")


def _load_json(path: Path) -> tuple[dict, str | None]:
    try:
        return json.loads(path.read_text()), None
    except FileNotFoundError:
        return {}, f"missing file {path.relative_to(ROOT)}"
    except json.JSONDecodeError as exc:
        return {}, f"invalid JSON in {path.relative_to(ROOT)}: {exc}"


def validate_claude_marketplace() -> list[str]:
    data, err = _load_json(CLAUDE_MARKETPLACE)
    if err:
        return [f"ERROR: {err}"]
    errors: list[str] = []
    rel = CLAUDE_MARKETPLACE.relative_to(ROOT)
    for field in MARKETPLACE_REQUIRED:
        if field not in data:
            errors.append(f"ERROR: {rel}: missing required field '{field}'")
    owner = data.get("owner", {})
    if isinstance(owner, dict):
        for field in MARKETPLACE_OWNER_REQUIRED:
            if field not in owner:
                errors.append(f"ERROR: {rel}: owner missing '{field}'")
    for plugin in data.get("plugins", []) or []:
        name = plugin.get("name", "<anon>")
        for field in MARKETPLACE_PLUGIN_REQUIRED:
            if field not in plugin:
                errors.append(f"ERROR: {rel}: plugin '{name}' missing '{field}'")
        source = plugin.get("source")
        if isinstance(source, str) and not source.startswith("./dist/claude/"):
            errors.append(
                f"ERROR: {rel}: plugin '{name}' source must point under "
                f"./dist/claude/, got '{source}'"
            )
    return errors


def validate_codex_marketplace() -> list[str]:
    data, err = _load_json(CODEX_MARKETPLACE)
    if err:
        return [f"ERROR: {err}"]
    errors: list[str] = []
    rel = CODEX_MARKETPLACE.relative_to(ROOT)
    for field in CODEX_MARKETPLACE_REQUIRED:
        if field not in data:
            errors.append(f"ERROR: {rel}: missing required field '{field}'")
    for plugin in data.get("plugins", []) or []:
        name = plugin.get("name", "<anon>")
        source = plugin.get("source", {})
        if isinstance(source, dict):
            path = source.get("path", "")
            if not path.startswith("./dist/codex/"):
                errors.append(
                    f"ERROR: {rel}: plugin '{name}' source.path must point "
                    f"under ./dist/codex/, got '{path}'"
                )
        else:
            errors.append(f"ERROR: {rel}: plugin '{name}' source must be an object")
    return errors


def validate_gemini_extension() -> list[str]:
    data, err = _load_json(GEMINI_EXTENSION)
    if err:
        return [f"ERROR: {err}"]
    errors: list[str] = []
    rel = GEMINI_EXTENSION.relative_to(ROOT)
    for field in GEMINI_EXTENSION_REQUIRED:
        if field not in data:
            errors.append(f"ERROR: {rel}: missing required field '{field}'")
    return errors


def validate_agents_md() -> list[str]:
    if not (ROOT / "AGENTS.md").exists():
        return ["WARNING: AGENTS.md not found at repo root (run: make build)"]
    return []


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(validate_claude_marketplace())
    errors.extend(validate_codex_marketplace())
    errors.extend(validate_gemini_extension())
    warnings.extend(validate_agents_md())

    for w in warnings:
        print(w)
    if errors:
        for e in errors:
            print(e)
        print(f"\n{len(errors)} error(s), {len(warnings)} warning(s)")
        return 1
    print(f"All checks passed ({len(warnings)} warning(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
