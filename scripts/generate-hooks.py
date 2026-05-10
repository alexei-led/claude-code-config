#!/usr/bin/env python3
"""Generate platform-specific hook configs from hooks.source.yaml.

Reads plugins/<plugin>/hooks/hooks.source.yaml and emits:
  - hooks/hooks.json              CC format, aggregated across all plugins
  - plugins/<plugin>/hooks/codex.hooks.json   Codex format, per plugin

Source event names and their platform mappings:

  sessionstart  → CC: SessionStart                 Codex: SessionStart
  preedit       → CC: BeforeTool(write_file|replace)  Codex: (skip)
  prebash       → CC: BeforeTool(run_shell_command) Codex: PreToolUse(^Bash$)
  postedit      → CC: AfterTool(write_file|replace) Codex: PostToolUse(^apply_patch$)
  posttool      → CC: AfterTool                    Codex: PostToolUse
  userpromptsubmit → CC: UserPromptSubmit           Codex: (skip)

Each entry requires: script, timeout (seconds).
Optional: name (defaults to script without .sh), status_message.

Usage:
  scripts/generate-hooks.py           # sync configs

Drift detection lives in `make check` (build + git diff --exit-code).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent

# (cc_event, cc_matcher, codex_event, codex_matcher)
# None matcher → no matcher field. None codex_event → CC-only, skip for Codex.
_EVENT_MAP: dict[str, tuple[str, str | None, str | None, str | None]] = {
    "sessionstart": ("SessionStart", None, "SessionStart", None),
    "preedit": ("BeforeTool", "write_file|replace", None, None),
    "prebash": ("BeforeTool", "run_shell_command", "PreToolUse", "^Bash$"),
    "postedit": ("AfterTool", "write_file|replace", "PostToolUse", "^apply_patch$"),
    "posttool": ("AfterTool", None, "PostToolUse", None),
    "userpromptsubmit": ("UserPromptSubmit", None, None, None),
}

_CC_SEQUENTIAL = {"BeforeTool", "AfterTool"}
_CC_EVENT_ORDER = ["BeforeTool", "AfterTool", "SessionStart", "UserPromptSubmit"]
_CODEX_EVENT_ORDER = ["PreToolUse", "PostToolUse", "SessionStart"]


def _iter_plugin_dirs() -> list[tuple[str, Path]]:
    return sorted(
        (d.name, d)
        for d in (ROOT / "plugins").iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )


def _load_source(plugin_dir: Path) -> dict | None:
    path = plugin_dir / "hooks" / "hooks.source.yaml"
    if not path.exists():
        return None
    with open(path) as f:
        return yaml.safe_load(f) or {}


def validate_source(source: dict, plugin_name: str, plugin_dir: Path) -> None:
    """Raise ValueError on unknown keys or missing required fields."""
    for key in source:
        if key not in _EVENT_MAP:
            raise ValueError(
                f"Plugin {plugin_name!r}: unknown event {key!r}. "
                f"Valid: {sorted(_EVENT_MAP)}"
            )
    for event, entries in source.items():
        if not isinstance(entries, list):
            raise ValueError(f"Plugin {plugin_name!r}: {event!r} must be a list")
        for i, entry in enumerate(entries):
            missing = {"script", "timeout"} - set(entry)
            if missing:
                raise ValueError(
                    f"Plugin {plugin_name!r}: {event}[{i}] missing: {missing}"
                )
            script_path = plugin_dir / "hooks" / entry["script"]
            if not script_path.is_file():
                raise ValueError(
                    f"Plugin {plugin_name!r}: {event}[{i}] "
                    f"script not found: {script_path}"
                )


def _cc_entry(plugin_name: str, entry: dict) -> dict:
    return {
        "type": "command",
        "name": entry.get("name", entry["script"].removesuffix(".sh")),
        "command": f"${{extensionPath}}/plugins/{plugin_name}/hooks/{entry['script']}",
        "timeout": entry["timeout"] * 1000,
    }


def _codex_entry(entry: dict) -> dict:
    hook: dict = {
        "type": "command",
        "command": f'"$PLUGIN_ROOT/hooks/{entry["script"]}"',
        "timeout": entry["timeout"],
    }
    if "status_message" in entry:
        hook["statusMessage"] = entry["status_message"]
    return hook


def build_cc(plugins: list[tuple[str, dict]]) -> dict:
    """Build aggregated CC hooks.json structure."""
    # Ordered by first insertion, preserving source YAML order within each event
    groups: dict[tuple[str, str | None], list[dict]] = {}
    for plugin_name, source in plugins:
        for event_name, entries in source.items():
            cc_event, cc_matcher, _, _ = _EVENT_MAP[event_name]
            key = (cc_event, cc_matcher)
            groups.setdefault(key, [])
            for entry in entries:
                groups[key].append(_cc_entry(plugin_name, entry))

    events: dict[str, list] = {}
    for cc_event in _CC_EVENT_ORDER:
        event_groups = []
        for (ev, matcher), hooks in groups.items():
            if ev != cc_event:
                continue
            group: dict = {}
            if matcher is not None:
                group["matcher"] = matcher
            if ev in _CC_SEQUENTIAL:
                group["sequential"] = True
            group["hooks"] = hooks
            event_groups.append(group)
        if event_groups:
            events[cc_event] = event_groups

    return {"hooks": events}


def build_codex(source: dict) -> dict:
    """Build per-plugin Codex codex.hooks.json structure."""
    groups: dict[tuple[str, str | None], list[dict]] = {}
    for event_name, entries in source.items():
        _, _, codex_event, codex_matcher = _EVENT_MAP[event_name]
        if codex_event is None:
            continue
        key = (codex_event, codex_matcher)
        groups.setdefault(key, [])
        for entry in entries:
            groups[key].append(_codex_entry(entry))

    events: dict[str, list] = {}
    for codex_event in _CODEX_EVENT_ORDER:
        event_groups = []
        for (ev, matcher), hooks in groups.items():
            if ev != codex_event:
                continue
            group: dict = {}
            if matcher is not None:
                group["matcher"] = matcher
            group["hooks"] = hooks
            event_groups.append(group)
        if event_groups:
            events[codex_event] = event_groups

    return {"hooks": events}


def _to_bytes(data: dict) -> bytes:
    return (json.dumps(data, indent=2) + "\n").encode()


def compute_desired() -> dict[Path, bytes]:
    desired: dict[Path, bytes] = {}
    cc_plugins: list[tuple[str, dict]] = []

    for plugin_name, plugin_dir in _iter_plugin_dirs():
        source = _load_source(plugin_dir)
        if source is None:
            continue
        validate_source(source, plugin_name, plugin_dir)
        cc_plugins.append((plugin_name, source))

        codex = build_codex(source)
        if codex["hooks"]:
            desired[plugin_dir / "hooks" / "codex.hooks.json"] = _to_bytes(codex)

    if cc_plugins:
        cc = build_cc(cc_plugins)
        if cc["hooks"]:
            desired[ROOT / "hooks" / "hooks.json"] = _to_bytes(cc)

    return desired


def _all_generated_paths() -> list[Path]:
    """All hook output files that currently exist on disk."""
    paths: list[Path] = []
    for _, plugin_dir in _iter_plugin_dirs():
        p = plugin_dir / "hooks" / "codex.hooks.json"
        if p.exists():
            paths.append(p)
    cc_hooks = ROOT / "hooks" / "hooks.json"
    if cc_hooks.exists():
        paths.append(cc_hooks)
    return paths


def sync(desired: dict[Path, bytes]) -> int:
    changes = 0
    for path in _all_generated_paths():
        if path not in desired:
            path.unlink()
            changes += 1
    for path, data in desired.items():
        if not path.exists() or path.read_bytes() != data:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            changes += 1
    return changes


def main(argv: list[str] | None = None) -> int:
    del argv  # no flags; drift detection lives in `make check`
    desired = compute_desired()
    changes = sync(desired)
    if changes:
        print(f"hooks synced: {changes} change(s)")
    else:
        print("hooks already in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
