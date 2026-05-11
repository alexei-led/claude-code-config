"""Skill/agent/hook compiler.

Compiles vendor-neutral sources under `src/` into per-target plugin/extension
trees under `dist/` for Claude Code, Codex CLI, Gemini CLI, and Pi Agent.

Scaffold stage (Task 1): target config, source discovery, dry-run mode.
Pipelines (skills/agents/hooks) wire in via subsequent tasks.
"""

from __future__ import annotations

import argparse
import logging
import sys
from collections.abc import Iterable
from pathlib import Path

log = logging.getLogger("compile")


TARGETS: list[str] = ["claude", "codex", "gemini", "pi"]


OUTPUT: dict[str, dict[str, str]] = {
    "claude": {
        "layout": "plugin",
        "skill_dir": "skills",
        "agent_dir": "agents",
        "hook_dir": "hooks",
    },
    "codex": {
        "layout": "plugin",
        "skill_dir": "skills",
        "agent_dir": "agents",
        "hook_dir": "hooks",
    },
    "gemini": {
        "layout": "flat",
        "skill_dir": "skills",
        "agent_dir": "agents",
        "hook_dir": "hooks",
    },
    "pi": {
        "layout": "flat",
        "skill_dir": "skills",
        "agent_dir": "agents",
        "hook_dir": "hooks",
    },
}


REQUIRED_OUTPUT_FIELDS: tuple[str, ...] = (
    "layout",
    "skill_dir",
    "agent_dir",
    "hook_dir",
)


VALID_LAYOUTS: frozenset[str] = frozenset({"plugin", "flat"})


def repo_root() -> Path:
    """Return the repo root inferred from this file's location."""
    return Path(__file__).resolve().parents[2]


def discover(src_subdir: Path) -> list[Path]:
    """Return sorted subdirectories of `src_subdir` (empty if absent)."""
    if not src_subdir.is_dir():
        return []
    return sorted(p for p in src_subdir.iterdir() if p.is_dir())


def iter_targets() -> Iterable[str]:
    """Yield configured targets in declaration order."""
    return iter(TARGETS)


def validate_output_config() -> None:
    """Confirm every target has all required output fields and a valid layout.

    Raises ValueError on misconfiguration so the build fails fast.
    """
    for target in TARGETS:
        if target not in OUTPUT:
            raise ValueError(f"target {target!r} missing from OUTPUT")
        cfg = OUTPUT[target]
        missing = [f for f in REQUIRED_OUTPUT_FIELDS if f not in cfg]
        if missing:
            raise ValueError(f"target {target!r} missing required fields: {missing}")
        if cfg["layout"] not in VALID_LAYOUTS:
            raise ValueError(
                f"target {target!r} has invalid layout "
                f"{cfg['layout']!r}; expected one of {sorted(VALID_LAYOUTS)}"
            )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build dist/ from src/.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="discover sources and log planned work without writing dist/",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="enable debug logging",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    validate_output_config()

    root = repo_root()
    src = root / "src"
    skills = discover(src / "skills")
    agents = discover(src / "agents")
    hooks = discover(src / "hooks")

    log.info(
        "discovered %d skill(s), %d agent(s), %d hook(s) under %s",
        len(skills),
        len(agents),
        len(hooks),
        src,
    )

    for target in TARGETS:
        cfg = OUTPUT[target]
        log.info(
            "target=%s layout=%s skills=%d agents=%d hooks=%d",
            target,
            cfg["layout"],
            len(skills),
            len(agents),
            len(hooks),
        )

    if args.dry_run:
        log.info("--dry-run: skipping dist/ writes")
        return 0

    # Wipe each target's dist/ subtree before rebuild so stale outputs
    # (e.g. files for sources later restricted with `targets:`) don't leak.
    import shutil

    for target in TARGETS:
        target_dir = root / "dist" / target
        if target_dir.exists():
            shutil.rmtree(target_dir)

    _here = Path(__file__).resolve().parent
    if str(_here) not in sys.path:
        sys.path.insert(0, str(_here))
    from compile_agent import compile_agent  # local imports: avoid cycle at top
    from compile_hook import compile_hook, write_hook_manifests
    from compile_skill import compile_skill
    from manifests import write_all as write_manifests
    from plugin_index import build_plugin_index, validate_artifacts_exist

    plugin_index = build_plugin_index(root)
    validate_artifacts_exist(root, plugin_index)

    total_skill_writes = 0
    for target in TARGETS:
        for skill in skills:
            written = compile_skill(skill, target, plugin_index["skills"], root)
            total_skill_writes += len(written)
    log.info("wrote %d skill file(s) under dist/", total_skill_writes)

    total_agent_writes = 0
    for target in TARGETS:
        for agent in agents:
            written = compile_agent(agent, target, plugin_index["agents"], root)
            total_agent_writes += len(written)
    log.info("wrote %d agent file(s) under dist/", total_agent_writes)

    total_hook_writes = 0
    for target in TARGETS:
        results = []
        for hook in hooks:
            result = compile_hook(hook, target, plugin_index["hooks"], root)
            total_hook_writes += len(result.placements)
            results.append(result)
        manifest_paths = write_hook_manifests(results, target, root)
        total_hook_writes += len(manifest_paths)
    log.info("wrote %d hook file(s) under dist/", total_hook_writes)

    manifest_paths_meta = write_manifests(root)
    log.info(
        "wrote root manifests: claude=%s codex=%s gemini=%s, %d symlink(s)",
        manifest_paths_meta["claude"].relative_to(root),
        manifest_paths_meta["codex"].relative_to(root),
        manifest_paths_meta["gemini"].relative_to(root),
        len(manifest_paths_meta["symlinks"]),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
