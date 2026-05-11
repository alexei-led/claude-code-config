"""Pi-extension compilation.

Pi extensions are Pi-only TypeScript modules with no equivalent on Claude,
Codex, or Gemini. Compilation is a verbatim tree copy from
`src/pi-extensions/<entry>` to `dist/pi/extensions/<entry>`, preserving
both single-file (`<name>.ts`) and directory (`<name>/index.ts`) layouts
that Pi's extension discoverer accepts.

No frontmatter, overlay, or genericity validation runs — Pi extensions
are vendor-specific by definition.
"""

from __future__ import annotations

import logging
import shutil
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import compile as _compile  # noqa: E402

log = logging.getLogger("compile.pi_extension")


def discover_pi_extensions(root: Path) -> list[Path]:
    """Return every direct child of `src/pi-extensions/` (files or dirs).

    Hidden entries (leading dot) are skipped so editor metadata and stray
    `.DS_Store` files do not leak into dist/.
    """
    src = root / "src" / "pi-extensions"
    if not src.is_dir():
        return []
    return sorted(p for p in src.iterdir() if not p.name.startswith("."))


def compile_pi_extensions(root: Path) -> list[Path]:
    """Copy every `src/pi-extensions/*` entry into `dist/pi/extensions/`.

    Files are copied as-is; directories are copied recursively. Returns
    the list of destination paths (top-level entries only).
    """
    target_cfg = _compile.OUTPUT.get("pi", {})
    leaf = target_cfg.get("extension_dir", "extensions")
    dest_root = root / "dist" / "pi" / leaf
    dest_root.mkdir(parents=True, exist_ok=True)

    written: list[Path] = []
    for entry in discover_pi_extensions(root):
        dest = dest_root / entry.name
        if entry.is_dir():
            shutil.copytree(entry, dest, dirs_exist_ok=True)
        else:
            shutil.copy2(entry, dest)
        written.append(dest)
    if written:
        log.info("wrote %d pi extension(s) under dist/pi/%s", len(written), leaf)
    return written
