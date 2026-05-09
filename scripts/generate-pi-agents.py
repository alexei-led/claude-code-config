#!/usr/bin/env python3
"""Build flat Pi subagent exports from plugin Claude agents.

The output uses pi-subagents flat files:

  plugins/<plugin>/agents-pi/<agent>.md

Source order for each Claude agent:
- plugins/<plugin>/agents/**/<agent>.pi.md when present
- transformed plugins/<plugin>/agents/**/<agent>.md when portable

Agents requiring unavailable tools are skipped unless a Pi override exists.
Duplicate flat filenames fail the run.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import frontmatter
except ImportError:
    print("ERROR: pip install python-frontmatter", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent

CC_ONLY_BEGIN = "<!-- CC-ONLY: begin -->"
CC_ONLY_END = "<!-- CC-ONLY: end -->"

CLAUDE_TO_PI_TOOLS = {
    "bash": "bash",
    "edit": "edit",
    "glob": "find",
    "grep": "grep",
    "ls": "ls",
    "multiedit": "edit",
    "read": "read",
    "write": "write",
}

PI_AGENT_FRONTMATTER_FIELDS = (
    "description",
    "display_name",
    "tools",
    "extensions",
    "skills",
    "memory",
    "disallowed_tools",
    "model",
    "thinking",
    "max_turns",
    "prompt_mode",
    "inherit_context",
    "run_in_background",
    "isolated",
    "isolation",
    "enabled",
)

PI_MEMORY_VALUES = {"local", "project", "user"}
PI_THINKING_VALUES = {"off", "minimal", "low", "medium", "high", "xhigh"}
PI_PROMPT_MODES = {"append", "replace"}
PI_ISOLATION_VALUES = {"worktree"}

EFFORT_TO_THINKING = {
    "low": "low",
    "medium": "medium",
    "high": "high",
    "xhigh": "xhigh",
}

UNAVAILABLE_BODY_PATTERN = re.compile(
    r"\b(?:Claude|WebFetch|WebSearch|mcp__[-A-Za-z0-9_]+)\b"
)


class AgentGenerationError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class DesiredFile:
    data: bytes
    mode: int = 0o644


@dataclass(frozen=True, slots=True)
class RejectedAgent:
    source: Path
    output: Path
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AgentDesiredState:
    files: dict[Path, DesiredFile]
    rejected: tuple[RejectedAgent, ...]


def strip_cc_body(body: str) -> str:
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


def iter_plugin_dirs() -> list[Path]:
    plugins_dir = ROOT / "plugins"
    if not plugins_dir.is_dir():
        return []
    return [
        plugin_dir
        for plugin_dir in sorted(plugins_dir.iterdir())
        if plugin_dir.is_dir() and not plugin_dir.name.startswith(".")
    ]


def agent_source_files(plugin_dir: Path) -> list[Path]:
    agents_dir = plugin_dir / "agents"
    if not agents_dir.is_dir():
        return []
    return [
        path
        for path in sorted(agents_dir.rglob("*.md"))
        if path.is_file() and not path.name.endswith(".pi.md")
    ]


def pi_override_for(source: Path) -> Path:
    return source.with_name(f"{source.stem}.pi.md")


def tool_base(tool: object) -> str:
    value = str(tool).strip()
    return value.split("(", 1)[0].strip()


def split_tool_string(value: str) -> list[str]:
    if value.strip().lower() == "none":
        return ["none"]
    return [part.strip() for part in value.split(",") if part.strip()]


def normalize_tool_values(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return split_tool_string(value)
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()]


def convert_tools(value: object) -> tuple[str | None, tuple[str, ...]]:
    source_tools = normalize_tool_values(value)
    if not source_tools:
        return None, ()
    if len(source_tools) == 1 and source_tools[0].lower() == "none":
        return "none", ()

    converted: list[str] = []
    unsupported: list[str] = []
    for tool in source_tools:
        base = tool_base(tool)
        if base.startswith("mcp__"):
            unsupported.append(tool)
            continue
        mapped = CLAUDE_TO_PI_TOOLS.get(base.lower())
        if mapped is None:
            unsupported.append(tool)
            continue
        if mapped not in converted:
            converted.append(mapped)

    if unsupported:
        return None, tuple(unsupported)
    if not converted:
        return None, ()
    return ", ".join(converted), ()


def normalize_skills(value: object) -> str | bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    if isinstance(value, list):
        skills = [str(item).strip() for item in value if str(item).strip()]
        if not skills:
            return None
        return ", ".join(skills)
    return str(value).strip() or None


def normalize_bool_or_string(value: object) -> object:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
    return value


def validate_choice(key: str, value: object, choices: set[str]) -> object | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip().lower()
    if normalized not in choices:
        return None
    return normalized


def normalize_metadata(metadata: dict) -> tuple[dict, tuple[str, ...]]:
    out: dict = {}
    unsupported: list[str] = []

    if "description" in metadata:
        out["description"] = metadata["description"]
    if "display_name" in metadata:
        out["display_name"] = metadata["display_name"]

    tools, unsupported_tools = convert_tools(metadata.get("tools"))
    unsupported.extend(unsupported_tools)
    if tools is not None:
        out["tools"] = tools
        if tools != "none" and "edit" not in tools and "write" not in tools:
            out["disallowed_tools"] = "edit, write"

    if "extensions" in metadata:
        out["extensions"] = normalize_bool_or_string(metadata["extensions"])

    skills = normalize_skills(metadata.get("skills"))
    if skills is not None:
        out["skills"] = skills

    memory = validate_choice("memory", metadata.get("memory"), PI_MEMORY_VALUES)
    if memory is not None:
        out["memory"] = memory

    if "disallowed_tools" in metadata:
        disallowed, unsupported_disallowed = convert_tools(metadata["disallowed_tools"])
        unsupported.extend(unsupported_disallowed)
        if disallowed is not None:
            out["disallowed_tools"] = disallowed

    if "model" in metadata:
        out["model"] = metadata["model"]

    thinking = validate_choice("thinking", metadata.get("thinking"), PI_THINKING_VALUES)
    if thinking is None and "effort" in metadata:
        effort = str(metadata["effort"]).strip().lower()
        thinking = EFFORT_TO_THINKING.get(effort)
    if thinking is not None:
        out["thinking"] = thinking

    for key in ("max_turns", "inherit_context", "run_in_background", "isolated"):
        if key in metadata:
            out[key] = metadata[key]

    prompt_mode = validate_choice(
        "prompt_mode",
        metadata.get("prompt_mode"),
        PI_PROMPT_MODES,
    )
    if prompt_mode is not None:
        out["prompt_mode"] = prompt_mode

    isolation = validate_choice(
        "isolation",
        metadata.get("isolation"),
        PI_ISOLATION_VALUES,
    )
    if isolation is not None:
        out["isolation"] = isolation

    if "enabled" in metadata:
        out["enabled"] = metadata["enabled"]

    ordered = {
        key: out[key]
        for key in PI_AGENT_FRONTMATTER_FIELDS
        if key in out and out[key] is not None
    }
    return ordered, tuple(unsupported)


def body_uses_unavailable_tools(body: str) -> bool:
    return UNAVAILABLE_BODY_PATTERN.search(body) is not None


def transform_agent(
    source: Path,
    output: Path,
    is_overlay: bool,
) -> tuple[DesiredFile | None, tuple[str, ...]]:
    post = frontmatter.load(str(source))
    metadata, unsupported = normalize_metadata(dict(post.metadata))
    body = strip_cc_body(post.content)

    reasons: list[str] = []
    if unsupported:
        reasons.append("requires unavailable tools: " + ", ".join(unsupported))
    if not is_overlay and body_uses_unavailable_tools(body):
        reasons.append("mentions Claude-only or unavailable tools")

    if reasons:
        return None, tuple(reasons)

    content = frontmatter.dumps(frontmatter.Post(body, **metadata)) + "\n"
    return DesiredFile(content.encode()), ()


def source_output_name(source: Path) -> str:
    return f"{source.stem}.md"


def compute_desired_state() -> AgentDesiredState:
    desired: dict[Path, DesiredFile] = {}
    rejected: list[RejectedAgent] = []
    seen_outputs: dict[str, Path] = {}

    for plugin_dir in iter_plugin_dirs():
        for source in agent_source_files(plugin_dir):
            output_name = source_output_name(source)
            if output_name in seen_outputs:
                first = seen_outputs[output_name].relative_to(ROOT)
                second = source.relative_to(ROOT)
                raise AgentGenerationError(
                    f"duplicate Pi agent filename {output_name}: {first}, {second}"
                )
            seen_outputs[output_name] = source

            overlay = pi_override_for(source)
            is_overlay = overlay.exists()
            selected = overlay if is_overlay else source
            output = plugin_dir / "agents-pi" / output_name
            desired_file, reasons = transform_agent(selected, output, is_overlay)
            if desired_file is None:
                rejected.append(RejectedAgent(selected, output, reasons))
                continue
            desired[output] = desired_file

    return AgentDesiredState(desired, tuple(rejected))


def generated_root_dirs() -> list[Path]:
    return [
        plugin_dir / "agents-pi"
        for plugin_dir in iter_plugin_dirs()
        if (plugin_dir / "agents-pi").is_dir()
    ]


def remove_empty_dirs(root: Path) -> int:
    changes = 0
    dirs = [path for path in root.rglob("*") if path.is_dir()]
    for path in sorted(dirs, key=lambda item: len(item.parts), reverse=True):
        try:
            path.rmdir()
        except OSError:
            continue
        changes += 1
    try:
        root.rmdir()
    except OSError:
        pass
    else:
        changes += 1
    return changes


def sync(desired: dict[Path, DesiredFile]) -> int:
    changes = 0

    for root in generated_root_dirs():
        paths = sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True)
        for path in paths:
            if (path.is_file() or path.is_symlink()) and path not in desired:
                path.unlink()
                changes += 1
        changes += remove_empty_dirs(root)

    for out_path, desired_file in sorted(desired.items()):
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if out_path.is_symlink():
            out_path.unlink()

        if out_path.exists() and out_path.is_dir():
            raise AgentGenerationError(f"output path is a directory: {out_path}")

        wrote_file = False
        if not out_path.exists() or out_path.read_bytes() != desired_file.data:
            out_path.write_bytes(desired_file.data)
            wrote_file = True
            changes += 1

        current_mode = out_path.stat().st_mode & 0o777
        if current_mode != desired_file.mode:
            out_path.chmod(desired_file.mode)
            if not wrote_file:
                changes += 1

    return changes


def check(desired: dict[Path, DesiredFile]) -> int:
    mismatches = 0

    for out_path, desired_file in sorted(desired.items()):
        rel_path = out_path.relative_to(ROOT)
        if out_path.is_symlink():
            print(f"  stale symlink: {rel_path}")
            mismatches += 1
        elif not out_path.exists():
            print(f"  missing: {rel_path}")
            mismatches += 1
        elif out_path.is_dir():
            print(f"  directory blocks file: {rel_path}")
            mismatches += 1
        elif out_path.read_bytes() != desired_file.data:
            print(f"  stale: {rel_path}")
            mismatches += 1
        elif (out_path.stat().st_mode & 0o777) != desired_file.mode:
            current = out_path.stat().st_mode & 0o777
            print(f"  mode: {rel_path} {current:04o} != {desired_file.mode:04o}")
            mismatches += 1

    for root in generated_root_dirs():
        for path in sorted(root.rglob("*")):
            if (path.is_file() or path.is_symlink()) and path not in desired:
                print(f"  stale: {path.relative_to(ROOT)}")
                mismatches += 1

    return mismatches


def print_rejections(rejected: tuple[RejectedAgent, ...]) -> None:
    if not rejected:
        return
    print(f"agents-pi/ skipped unsupported agents: {len(rejected)}")
    for rejection in rejected[:10]:
        source = rejection.source.relative_to(ROOT)
        print(f"  skipped {source}: {'; '.join(rejection.reasons)}")
    if len(rejected) > 10:
        print(f"  ... {len(rejected) - 10} more")


def stage_generated_dirs() -> None:
    for plugin_dir in iter_plugin_dirs():
        out_dir = plugin_dir / "agents-pi"
        if out_dir.is_dir():
            subprocess.run(["git", "add", str(out_dir)], cwd=ROOT, check=False)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--hook", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    try:
        state = compute_desired_state()
    except AgentGenerationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print_rejections(state.rejected)

    if args.check:
        mismatches = check(state.files)
        if mismatches:
            print(f"agents-pi/ out of sync: {mismatches} issue(s)")
            print("Run: uv run python scripts/generate-pi-agents.py")
            return 1
        print(
            f"agents-pi/ in sync "
            f"({len(state.files)} files, {len(state.rejected)} skipped)"
        )
        return 0

    try:
        changes = sync(state.files)
    except AgentGenerationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.hook and changes > 0:
        stage_generated_dirs()
        print(f"agents-pi/ synced: {changes} change(s) (staged)")
    elif changes > 0:
        print(f"agents-pi/ synced: {changes} change(s)")
    else:
        print(f"agents-pi/ already in sync ({len(state.files)} files)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
