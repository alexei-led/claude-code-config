"""Smoke test for `watch-team` skill migration (Task 17).

Confirms the migrated skill produces a non-empty `SKILL.md` for all four
targets via `compile_skill`, and that Claude's per-target frontmatter overlay
(`allowed-tools`, `argument-hint`) reaches only the Claude output.
"""

from __future__ import annotations

from pathlib import Path

import frontmatter
import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC_SKILLS = _REPO_ROOT / "src" / "skills"

TARGETS = ("claude", "codex", "gemini", "pi")


@pytest.fixture(scope="module")
def cs(load_script):
    load_script("build/compile.py")
    return load_script("build/compile_skill.py")


def _staging_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    (root / "src" / "skills").symlink_to(_SRC_SKILLS)
    (root / "scripts" / "build" / "preambles").mkdir(parents=True)
    preambles_src = _REPO_ROOT / "scripts" / "build" / "preambles"
    for entry in preambles_src.iterdir():
        (root / "scripts" / "build" / "preambles" / entry.name).symlink_to(entry)
    return root


@pytest.mark.parametrize("target", TARGETS)
def test_watch_team_compiles_for_target(cs, tmp_path: Path, target: str) -> None:
    root = _staging_root(tmp_path)
    skill_dir = root / "src" / "skills" / "watch-team"

    written = cs.compile_skill(skill_dir, target, None, root)

    assert len(written) == 1, written
    out = written[0]
    assert out.is_file()

    post = frontmatter.loads(out.read_text())
    assert post.metadata["name"] == "watch-team"
    description = str(post.metadata["description"])
    assert "tmux" in description.lower()
    assert "Watch Team" in post.content
    assert (
        "auto-approve" in post.content.lower()
        or "auto-approver" in post.content.lower()
    )


def test_watch_team_claude_frontmatter_only_on_claude(cs, tmp_path: Path) -> None:
    root = _staging_root(tmp_path)
    skill_dir = root / "src" / "skills" / "watch-team"

    claude_out = cs.compile_skill(skill_dir, "claude", None, root)[0]
    codex_out = cs.compile_skill(skill_dir, "codex", None, root)[0]

    claude_meta = frontmatter.loads(claude_out.read_text()).metadata
    codex_meta = frontmatter.loads(codex_out.read_text()).metadata

    assert claude_meta.get("allowed-tools") == ["Bash", "Read"]
    assert claude_meta.get("argument-hint") == "<tmux-window> [duration-seconds]"

    assert "allowed-tools" not in codex_meta
    assert "argument-hint" not in codex_meta
