from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BANNED = ("mcp__context7", "WebFetch", "WebSearch")


def _docs_lookup_files() -> list[Path]:
    roots = [
        ROOT / "plugins" / "dev-tools" / "skills" / "context7-cli",
        ROOT / "plugins" / "dev-tools" / "skills" / "looking-up-docs",
        ROOT / "plugins" / "dev-tools" / "skills-codex" / "context7-cli",
        ROOT / "plugins" / "dev-tools" / "skills-codex" / "looking-up-docs",
        ROOT / "plugins" / "dev-tools" / "skills-pi" / "context7-cli",
        ROOT / "plugins" / "dev-tools" / "skills-pi" / "looking-up-docs",
    ]
    files: list[Path] = []
    for root in roots:
        if root.is_file():
            files.append(root)
        elif root.is_dir():
            files.extend(path for path in root.rglob("*.md") if path.is_file())
    return sorted(files)


def test_docs_lookup_skills_do_not_reference_removed_tools():
    files = _docs_lookup_files()
    assert files
    for path in files:
        text = path.read_text()
        for banned in BANNED:
            assert banned not in text, f"{path.relative_to(ROOT)} contains {banned}"


def test_context7_cli_skill_documents_required_commands():
    skill = (
        ROOT / "plugins" / "dev-tools" / "skills" / "context7-cli" / "SKILL.md"
    ).read_text()

    assert "ctx7 library <name>" in skill
    assert "ctx7 docs /org/project" in skill
    assert "npx ctx7@latest library" in skill
    assert "Do not include secrets" in skill
    assert "Do not call `ctx7 library` more than 3 times" in skill
    assert "Do not call `ctx7 docs` more than 3 times" in skill
