"""Per-target agent compilation pipeline.

Orchestrates the overlay engine to turn a `src/agents/<name>/` source tree into
the final agent definition for a single target. The result is materialized at
one or more `dist/` paths resolved through `output_paths`.

Per-target output format:

- Claude / Gemini / Pi: markdown + YAML frontmatter (`.md`).
- Codex: TOML (`.toml`) — frontmatter + body collapse into a single TOML doc
  via `codex_toml.to_toml`. The body lands in `developer_instructions`.

Steps per call:

1. Load base `AGENT.md` (frontmatter + body).
2. Honor `targets:` restriction — if present and the current target is not
   listed, skip the agent.
3. Merge per-target frontmatter overlay (`<target>/frontmatter.yaml`) onto the
   base via `overlay.merge_frontmatter`. `targets` is stripped; non-allowed
   keys are filtered.
4. Apply per-target body overlay (`<target>/body.md`) via
   `overlay.apply_body_overlay` — auto-detects mirror vs full replacement.
5. Render: TOML for codex, markdown+YAML otherwise. The agent's name (parent
   directory) is injected when missing so downstream consumers always see one.
6. Write to every resolved output path.

Agents have no support files (no `scripts/`, `references/`, `assets/`) and no
per-target preamble — both differences from skills are intentional and follow
the design doc table for agent compiler output.
"""

from __future__ import annotations

import logging
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import frontmatter

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import compile as _compile  # noqa: E402
from codex_toml import to_toml  # noqa: E402
from overlay import (  # noqa: E402
    apply_body_overlay,
    load_base,
    merge_frontmatter,
)

log = logging.getLogger("compile.agent")


def output_paths(
    name: str,
    target: str,
    plugin_index: Mapping[str, list[str]] | None,
    root: Path,
    extension: str,
) -> list[Path]:
    """Resolve per-target dist file paths for an agent.

    Agents are single files (not directories), so the path is
    `<dist>/<...>/<agent_dir>/<name><extension>`. Plugin-grouped targets
    (`claude`, `codex`) emit once per owning plugin from `plugin_index`;
    agents with no owning plugin emit nothing for that target — an unowned
    plugin-grouped artifact would land at an unreachable flat path that the
    marketplace manifests never reference. Flat targets (`gemini`, `pi`)
    always emit to the flat path.
    """
    cfg = _compile.OUTPUT[target]
    dist = root / "dist" / target
    agent_dir = cfg["agent_dir"]
    filename = f"{name}{extension}"
    if cfg["layout"] == "plugin":
        plugins = list((plugin_index or {}).get(name, []))
        return [dist / "plugins" / p / agent_dir / filename for p in plugins]
    return [dist / agent_dir / filename]


def _target_listed(base_meta: Mapping[str, Any], target: str) -> bool:
    """Return True when `target` passes the base `targets:` restriction."""
    raw = base_meta.get("targets")
    if raw is None:
        return True
    listed = [raw] if isinstance(raw, str) else list(raw)
    return target in listed


def _render_md(meta: Mapping[str, Any], body: str) -> str:
    """Render `meta` as YAML frontmatter followed by `body`.

    Mirrors `compile_skill._render` so md outputs are byte-stable across runs.
    """
    post = frontmatter.Post(body, **dict(meta))
    text = frontmatter.dumps(post)
    if not text.endswith("\n"):
        text += "\n"
    return text


def compile_agent(
    agent_dir: Path,
    target: str,
    plugin_index: Mapping[str, list[str]] | None,
    root: Path,
) -> list[Path]:
    """Compile a single agent for a single target.

    Returns the list of written file paths (empty when the agent is skipped
    via a `targets:` restriction).
    """
    base_path = agent_dir / "AGENT.md"
    base_meta, base_body = load_base(base_path)

    if not _target_listed(base_meta, target):
        log.debug(
            "agent=%s target=%s skipped (not in targets:%s)",
            agent_dir.name,
            target,
            base_meta.get("targets"),
        )
        return []

    overlay_fm = agent_dir / target / "frontmatter.yaml"
    merged_meta = merge_frontmatter(
        base_meta,
        overlay_fm if overlay_fm.is_file() else None,
        target,
    )

    overlay_body_path = agent_dir / target / "body.md"
    if overlay_body_path.is_file():
        body = apply_body_overlay(
            base_body,
            overlay_body_path.read_text(),
            overlay_filename=str(overlay_body_path),
        )
    else:
        body = base_body

    name = agent_dir.name
    if not merged_meta.get("name"):
        # `setdefault` would skip an explicit `name: null`, so check the value.
        merged_meta["name"] = name

    if target == "codex":
        rendered = to_toml(merged_meta, body)
        extension = ".toml"
    else:
        rendered = _render_md(merged_meta, body)
        extension = ".md"

    written: list[Path] = []
    for out_path in output_paths(name, target, plugin_index, root, extension):
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered)
        written.append(out_path)
    return written
