"""Codex TOML conversion for compiled agents.

Codex CLI consumes agent definitions as TOML rather than markdown+YAML. The
schema is narrow:

- Scalar keys: `name`, `description`, `model`, `model_reasoning_effort`,
  `sandbox_mode`.
- String-array: `nickname_candidates`.
- Multi-line: `developer_instructions` = the agent's markdown body, emitted as
  a triple-quoted TOML basic string with internal `\"\"\"` escaped.
- Tables: `[mcp_servers.<name>]` (one per MCP server) and `[[skills.config]]`
  (array of tables) — both pulled directly from the merged frontmatter.

`effort` (the cross-target key) is renamed to `model_reasoning_effort` here so
the source can stay vendor-neutral. Anything else falls off; the allow-list
filter in `overlay.merge_frontmatter` already runs before this point, so
unknown keys cannot leak through.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

_SCALAR_PASSTHROUGH: tuple[str, ...] = (
    "model",
    "model_reasoning_effort",
    "sandbox_mode",
)


def to_toml(agent_meta: Mapping[str, Any], body: str) -> str:
    """Render an agent's merged metadata + markdown body as Codex TOML.

    Order is fixed (name, description, scalars, nickname_candidates,
    developer_instructions, mcp_servers tables, skills.config array of tables)
    so output diffs stay stable across runs.
    """
    meta = dict(agent_meta)

    if "effort" in meta:
        meta.setdefault("model_reasoning_effort", meta["effort"])
        meta.pop("effort")

    lines: list[str] = []
    if "name" in meta:
        lines.append(f"name = {_basic_string(meta.pop('name'))}")
    if "description" in meta:
        lines.append(f"description = {_basic_string(meta.pop('description'))}")

    for key in _SCALAR_PASSTHROUGH:
        if key in meta:
            lines.append(f"{key} = {_basic_string(meta.pop(key))}")

    if "nickname_candidates" in meta:
        lines.append(
            "nickname_candidates = " + _string_array(meta.pop("nickname_candidates"))
        )

    lines.append(f"developer_instructions = {_multiline_string(body)}")

    mcp_servers = meta.pop("mcp_servers", None)
    if mcp_servers:
        if not isinstance(mcp_servers, Mapping):
            raise ValueError(
                "mcp_servers must be a mapping of server-name → config, "
                f"got {type(mcp_servers).__name__}"
            )
        for server_name, config in mcp_servers.items():
            lines.append("")
            lines.append(f"[mcp_servers.{_bare_key(server_name)}]")
            lines.extend(_emit_table_body(config))

    skills = meta.pop("skills", None)
    if skills is not None:
        for entry in _skills_config_entries(skills):
            lines.append("")
            lines.append("[[skills.config]]")
            lines.extend(_emit_table_body(entry))

    return "\n".join(lines) + "\n"


def _skills_config_entries(skills: Any) -> list[Mapping[str, Any]]:
    """Extract `skills.config` array-of-tables entries from a merged value.

    Accepts either the explicit nested form `{config: [...]}` or the bare list
    form `[...]`. A list of strings is treated as `[{name: <s>}]` so flat
    references still emit valid TOML.
    """
    if isinstance(skills, Mapping):
        config = skills.get("config")
        if config is None:
            return []
        return _normalise_skill_entries(config)
    if isinstance(skills, Sequence) and not isinstance(skills, str):
        return _normalise_skill_entries(skills)
    raise ValueError(
        f"skills must be a mapping with 'config' or a list, got {type(skills).__name__}"
    )


def _normalise_skill_entries(entries: Any) -> list[Mapping[str, Any]]:
    if not isinstance(entries, Sequence) or isinstance(entries, str):
        raise ValueError(f"skills.config must be a list, got {type(entries).__name__}")
    out: list[Mapping[str, Any]] = []
    for entry in entries:
        if isinstance(entry, Mapping):
            out.append(entry)
        elif isinstance(entry, str):
            out.append({"name": entry})
        else:
            raise ValueError(
                "skills.config entry must be a mapping or string, "
                f"got {type(entry).__name__}"
            )
    return out


def _emit_table_body(config: Any) -> list[str]:
    if not isinstance(config, Mapping):
        raise ValueError(f"table body must be a mapping, got {type(config).__name__}")
    out: list[str] = []
    for key, value in config.items():
        out.append(f"{_bare_key(key)} = {_value(value)}")
    return out


def _value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        return _basic_string(value)
    if isinstance(value, Sequence):
        return _string_array(value)
    if isinstance(value, Mapping):
        # Inline table — keep it simple for nested config blobs.
        inner = ", ".join(f"{_bare_key(k)} = {_value(v)}" for k, v in value.items())
        return "{ " + inner + " }"
    raise ValueError(f"cannot render TOML value of type {type(value).__name__}")


def _basic_string(value: Any) -> str:
    """Quote `value` as a TOML basic (single-line) string."""
    text = str(value)
    escaped = (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\b", "\\b")
        .replace("\t", "\\t")
        .replace("\n", "\\n")
        .replace("\f", "\\f")
        .replace("\r", "\\r")
    )
    return f'"{escaped}"'


def _string_array(values: Any) -> str:
    if isinstance(values, str) or not isinstance(values, Sequence):
        raise ValueError(f"expected a sequence of strings, got {type(values).__name__}")
    parts = [_basic_string(v) for v in values]
    return "[" + ", ".join(parts) + "]"


def _multiline_string(body: str) -> str:
    """Render `body` as a TOML multi-line basic string.

    Backslashes are doubled, and any literal `\"\"\"` inside the body is broken
    by escaping the middle quote so the closing delimiter stays unambiguous.
    Leading newline after the opening `\"\"\"` is added by convention so the
    body starts on its own line.
    """
    text = body.replace("\\", "\\\\")
    text = text.replace('"""', '""\\"')
    return f'"""\n{text}\n"""'


def _bare_key(key: Any) -> str:
    """Render a TOML key. Bare when possible, quoted otherwise."""
    text = str(key)
    if text and all(c.isalnum() or c in "-_" for c in text):
        return text
    return _basic_string(text)
