"""Shared helpers for scripts/ generators.

Internal module — kept underscore-prefixed so it doesn't appear as a CLI.
"""

from __future__ import annotations

import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

try:
    import frontmatter as _frontmatter
except ImportError:
    print("ERROR: pip install python-frontmatter", file=sys.stderr)
    sys.exit(1)

frontmatter = _frontmatter


def find_repo_root(start: Path) -> Path:
    """Walk up from ``start`` until a directory containing ``pyproject.toml``
    is found. Anchor-based so script reorgs don't break it.
    """
    for parent in start.resolve().parents:
        if (parent / "pyproject.toml").is_file():
            return parent
    raise RuntimeError(f"no pyproject.toml found above {start}")


ROOT = find_repo_root(Path(__file__))

CC_ONLY_BEGIN = "<!-- CC-ONLY: begin -->"
CC_ONLY_END = "<!-- CC-ONLY: end -->"


@dataclass(frozen=True, slots=True)
class DesiredFile:
    data: bytes
    mode: int = 0o644


def iter_plugin_dirs(root: Path = ROOT) -> list[Path]:
    plugins = root / "plugins"
    if not plugins.is_dir():
        return []
    return [
        p
        for p in sorted(plugins.iterdir())
        if p.is_dir() and not p.name.startswith(".")
    ]


def strip_cc_body(body: str) -> str:
    """Remove <!-- CC-ONLY: begin --> ... <!-- CC-ONLY: end --> blocks."""
    out: list[str] = []
    inside = False
    for line in body.split("\n"):
        if CC_ONLY_BEGIN in line:
            inside = True
            continue
        if CC_ONLY_END in line:
            inside = False
            continue
        if not inside:
            out.append(line)
    return "\n".join(out)


def remove_empty_dirs(root: Path) -> int:
    """Remove empty subdirectories of ``root``, then ``root`` itself if empty."""
    changes = 0
    dirs = [p for p in root.rglob("*") if p.is_dir()]
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


def sync_files(
    desired: dict[Path, DesiredFile],
    stale_roots: Iterable[Path],
    *,
    error_type: type[Exception] = RuntimeError,
) -> int:
    """Apply desired-state file map. Removes stale files under ``stale_roots``.

    Returns count of changes (writes, deletes, mode-only flips).
    """
    changes = 0

    for root in stale_roots:
        paths = sorted(root.rglob("*"), key=lambda item: len(item.parts), reverse=True)
        for path in paths:
            if (path.is_file() or path.is_symlink()) and path not in desired:
                path.unlink()
                changes += 1
        changes += remove_empty_dirs(root)

    for out_path, df in sorted(desired.items()):
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if out_path.is_symlink():
            out_path.unlink()

        if out_path.exists() and out_path.is_dir():
            raise error_type(f"output path is a directory: {out_path}")

        wrote = False
        if not out_path.exists() or out_path.read_bytes() != df.data:
            out_path.write_bytes(df.data)
            wrote = True
            changes += 1

        current_mode = out_path.stat().st_mode & 0o777
        if current_mode != df.mode:
            out_path.chmod(df.mode)
            if not wrote:
                changes += 1

    return changes
