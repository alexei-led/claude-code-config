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

import re
import sys
from dataclasses import dataclass
from pathlib import Path

_REPO = next(
    p for p in Path(__file__).resolve().parents if (p / "pyproject.toml").is_file()
)
sys.path.insert(0, str(_REPO / "scripts"))
from _common import (  # noqa: E402
    ROOT,
    DesiredFile,
    frontmatter,
    iter_plugin_dirs,
    strip_cc_body,
    sync_files,
)

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
class RejectedAgent:
    source: Path
    output: Path
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AgentDesiredState:
    files: dict[Path, DesiredFile]
    rejected: tuple[RejectedAgent, ...]


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


WATERMARK = (
    "<!-- generated by scripts/build/generate-subagents.py — edits will be overwritten "
    "by `make build`. Edit the canonical agent file in plugins/<plugin>/agents/. -->"
)


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

    body = WATERMARK + "\n\n" + body
    content = frontmatter.dumps(frontmatter.Post(body, **metadata)) + "\n"
    return DesiredFile(content.encode()), ()


def source_output_name(source: Path) -> str:
    return f"{source.stem}.md"


def compute_desired_state() -> AgentDesiredState:
    desired: dict[Path, DesiredFile] = {}
    rejected: list[RejectedAgent] = []
    seen_outputs: dict[str, Path] = {}

    for plugin_dir in iter_plugin_dirs(ROOT):
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
        for plugin_dir in iter_plugin_dirs(ROOT)
        if (plugin_dir / "agents-pi").is_dir()
    ]


def sync(desired: dict[Path, DesiredFile]) -> int:
    return sync_files(desired, generated_root_dirs(), error_type=AgentGenerationError)


def print_rejections(rejected: tuple[RejectedAgent, ...]) -> None:
    if not rejected:
        return
    print(f"agents-pi/ skipped unsupported agents: {len(rejected)}")
    for rejection in rejected[:10]:
        source = rejection.source.relative_to(ROOT)
        print(f"  skipped {source}: {'; '.join(rejection.reasons)}")
    if len(rejected) > 10:
        print(f"  ... {len(rejected) - 10} more")


def main(argv: list[str] | None = None) -> int:
    del argv  # no flags; drift detection lives in `make check`
    try:
        state = compute_desired_state()
    except AgentGenerationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print_rejections(state.rejected)

    try:
        changes = sync(state.files)
    except AgentGenerationError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if changes > 0:
        print(f"agents-pi/ synced: {changes} change(s)")
    else:
        print(f"agents-pi/ already in sync ({len(state.files)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
