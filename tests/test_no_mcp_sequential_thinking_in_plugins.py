from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGINS = ROOT / "plugins"
BANNED = "mcp__sequential-thinking__"


def _markdown_files() -> list[Path]:
    return sorted(path for path in PLUGINS.rglob("*.md") if path.is_file())


def test_no_mcp_sequential_thinking_anywhere_in_plugins():
    """Source-of-truth plugins must use the sequential-thinking skill, not the MCP.

    The MCP server has been replaced by the `sequential-thinking` skill
    (plugins/dev-tools/skills/sequential-thinking/SKILL.md), which produces
    the same numbered/revisable/branchable reasoning artifact via prompting
    and is portable across Claude Code, Codex, Gemini, and Pi.
    """
    files = _markdown_files()
    assert files, f"no markdown files found under {PLUGINS}"
    offenders: list[str] = []
    for path in files:
        if BANNED in path.read_text():
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, (
        f"{len(offenders)} file(s) still reference {BANNED}: "
        + ", ".join(offenders)
        + ". Drop the MCP tool from allowed-tools/tools, add "
        '"sequential-thinking" to the skills list, and rewrite body refs '
        "to use the skill name."
    )
