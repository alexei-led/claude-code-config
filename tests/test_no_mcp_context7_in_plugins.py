from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
BANNED = "mcp__context7__"


def _markdown_files() -> list[Path]:
    return sorted(path for path in SRC.rglob("*.md") if path.is_file())


def test_no_mcp_context7_anywhere_in_sources():
    """Vendor-neutral sources must use the ctx7 CLI, never the context7 MCP."""
    files = _markdown_files()
    assert files, f"no markdown files found under {SRC}"
    offenders: list[str] = []
    for path in files:
        if BANNED in path.read_text():
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, (
        f"{len(offenders)} file(s) still reference {BANNED}: "
        + ", ".join(offenders)
        + ". Replace with Bash(ctx7 *) / Bash(npx ctx7@latest *) and rewrite "
        "body refs to use ctx7 CLI commands."
    )
