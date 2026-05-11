"""Shared overlay engine for the skill/agent/hook compiler.

This task wires the frontmatter half of the overlay pipeline:

- `load_base` reads `SKILL.md` / `AGENT.md` (YAML+markdown via `python-frontmatter`)
  and `HOOK.sh` / `HOOK.py` (shell-comment YAML block).
- `merge_frontmatter` layers a per-target `<target>/frontmatter.yaml` overlay on
  the base via `mergedeep.merge` with overlay-side wins, strips the `targets`
  renderer metadata, and filters out keys not allowed for the target.

Body-overlay and support-file logic land in later tasks; this module grows
those exports without breaking the frontmatter contract.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import frontmatter
import mergedeep
import yaml

log = logging.getLogger("compile.overlay")


# Keys allowed in the emitted frontmatter per target. Anything outside this set
# is dropped during the merge so a Claude-only field (e.g. `argument-hint`) does
# not leak into Codex/Gemini/Pi output. Sets are inclusive across skills and
# agents — per-kind validation lives in the skill/agent pipelines.
#
# Common base keys (agentskills.io): `name`, `description`, `license`,
# `metadata`. Each target adds the extensions documented in
# `docs/skill-compiler-design.md`.
ALLOWED_KEYS: dict[str, frozenset[str]] = {
    "claude": frozenset(
        {
            "name",
            "description",
            "license",
            "metadata",
            "allowed-tools",
            "when_to_use",
            "argument-hint",
            "arguments",
            "disable-model-invocation",
            "user-invocable",
            "context",
            "hooks",
            "paths",
            "shell",
            "tools",
            "model",
            "color",
            "effort",
            "skills",
            "agent",
        }
    ),
    "codex": frozenset(
        {
            "name",
            "description",
            "license",
            "metadata",
            "model",
            "model_reasoning_effort",
            "sandbox_mode",
            "nickname_candidates",
            "mcp_servers",
            "skills",
            "developer_instructions",
        }
    ),
    "gemini": frozenset(
        {
            "name",
            "description",
            "license",
            "metadata",
            "allowed-tools",
            "tools",
        }
    ),
    "pi": frozenset(
        {
            "name",
            "description",
            "license",
            "metadata",
            "disable-model-invocation",
            "model",
            "thinking",
            "tools",
            "skills",
        }
    ),
}


# Renderer-only metadata stripped from every emitted frontmatter.
RENDERER_KEYS: frozenset[str] = frozenset({"targets"})


def load_base(path: Path) -> tuple[dict[str, Any], str]:
    """Return `(metadata, body)` for a base source file.

    Markdown files use python-frontmatter. Shell/Python files use a top-of-file
    `# ---` … `# ---` YAML comment block (optionally preceded by a shebang).
    Files with no parseable frontmatter return an empty dict and the full text
    as body.
    """
    text = path.read_text()
    if path.suffix == ".md":
        post = frontmatter.loads(text)
        return dict(post.metadata), post.content
    return _parse_shell_frontmatter(text)


def merge_frontmatter(
    base_meta: Mapping[str, Any],
    overlay_path: Path | None,
    target: str,
) -> dict[str, Any]:
    """Merge per-target frontmatter overlay onto base, filter to allowed keys.

    `mergedeep.merge` defaults to recursive dict merge and replacement for
    scalars/lists — that matches the design's "overlay-side wins, no delete"
    rule. The `targets` renderer key is stripped before key-filtering so it
    never reaches dist/.
    """
    if target not in ALLOWED_KEYS:
        raise ValueError(f"unknown target {target!r}")

    merged: dict[str, Any] = dict(mergedeep.merge({}, dict(base_meta)))

    if overlay_path is not None and overlay_path.exists():
        overlay_raw = yaml.safe_load(overlay_path.read_text())
        if overlay_raw is None:
            overlay_raw = {}
        if not isinstance(overlay_raw, Mapping):
            raise ValueError(
                f"{overlay_path}: frontmatter overlay must be a YAML mapping, "
                f"got {type(overlay_raw).__name__}"
            )
        merged = dict(mergedeep.merge({}, merged, dict(overlay_raw)))

    for key in RENDERER_KEYS:
        merged.pop(key, None)

    return filter_allowed_keys(merged, target)


def filter_allowed_keys(meta: Mapping[str, Any], target: str) -> dict[str, Any]:
    """Drop keys not in the target's allowlist; log each drop at debug level."""
    if target not in ALLOWED_KEYS:
        raise ValueError(f"unknown target {target!r}")
    allowed = ALLOWED_KEYS[target]
    out: dict[str, Any] = {}
    for k, v in meta.items():
        if k in allowed:
            out[k] = v
        else:
            log.debug("target=%s drop key %r (not in allowlist)", target, k)
    return out


def _parse_shell_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Extract `# ---` YAML block at the top of a shell/python source file."""
    lines = text.splitlines(keepends=True)
    i = 0
    if i < len(lines) and lines[i].startswith("#!"):
        i += 1
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i >= len(lines) or lines[i].rstrip() != "# ---":
        return {}, text

    fm_start = i
    i += 1
    fm_body_lines: list[str] = []
    while i < len(lines):
        if lines[i].rstrip() == "# ---":
            i += 1
            yaml_src = "\n".join(_strip_comment(ln) for ln in fm_body_lines)
            data = yaml.safe_load(yaml_src) or {}
            if not isinstance(data, Mapping):
                raise ValueError(
                    "shell frontmatter must be a YAML mapping, "
                    f"got {type(data).__name__}"
                )
            body = "".join(lines[:fm_start]) + "".join(lines[i:])
            return dict(data), body
        fm_body_lines.append(lines[i])
        i += 1
    return {}, text


def _strip_comment(line: str) -> str:
    raw = line.rstrip("\n")
    if raw.startswith("# "):
        return raw[2:]
    if raw.startswith("#"):
        return raw[1:]
    return raw
