"""Tests for `scripts.validate.validate_genericity`."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def vg(load_script):
    return load_script("validate_genericity.py")


def _write(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip("\n"))
    return path


def test_clean_base_passes(vg, tmp_path: Path) -> None:
    skill = _write(
        tmp_path / "src" / "skills" / "x" / "SKILL.md",
        """
        ---
        name: x
        description: A clean skill.
        ---

        # Body

        Run the test suite and report results.
        """,
    )
    assert vg.scan_file(skill) == []


def test_dollar_arguments_fails(vg, tmp_path: Path) -> None:
    skill = _write(
        tmp_path / "src" / "skills" / "x" / "SKILL.md",
        """
        ---
        name: x
        description: bad.
        ---

        Run with $ARGUMENTS to do things.
        """,
    )
    violations = vg.scan_file(skill)
    assert len(violations) == 1
    assert "$ARGUMENTS" in violations[0]


def test_task_call_fails(vg, tmp_path: Path) -> None:
    agent = _write(
        tmp_path / "src" / "agents" / "x" / "AGENT.md",
        """
        ---
        name: x
        description: bad.
        ---

        Delegate using Task(prompt="foo").
        """,
    )
    violations = vg.scan_file(agent)
    assert len(violations) == 1
    assert "Task(" in violations[0]


def test_claude_restricted_base_allowed_to_use_forbidden(vg, tmp_path: Path) -> None:
    skill = _write(
        tmp_path / "src" / "skills" / "x" / "SKILL.md",
        """
        ---
        name: x
        description: claude-only.
        targets: [claude]
        ---

        Use Task() and $ARGUMENTS freely; this is Claude-only.
        Also mcp__perplexity-ask__perplexity_ask is fine.
        """,
    )
    assert vg.scan_file(skill) == []


def test_claude_restricted_scalar_form_opts_out(vg, tmp_path: Path) -> None:
    skill = _write(
        tmp_path / "src" / "skills" / "x" / "SKILL.md",
        """
        ---
        name: x
        description: claude-only.
        targets: claude
        ---

        $ARGUMENTS allowed here.
        """,
    )
    assert vg.scan_file(skill) == []


def test_mcp_prefix_detected(vg, tmp_path: Path) -> None:
    skill = _write(
        tmp_path / "src" / "skills" / "x" / "SKILL.md",
        """
        ---
        name: x
        description: bad.
        ---

        Call mcp__plugin_claude-mem_mcp-search__smart_search for context.
        """,
    )
    violations = vg.scan_file(skill)
    assert len(violations) == 1
    assert "mcp__plugin_claude" in violations[0]


def test_claude_env_var_detected(vg, tmp_path: Path) -> None:
    skill = _write(
        tmp_path / "src" / "skills" / "x" / "SKILL.md",
        """
        ---
        name: x
        description: bad.
        ---

        Read ${CLAUDE_PROJECT_DIR} for the path.
        """,
    )
    violations = vg.scan_file(skill)
    assert len(violations) == 1
    assert "${CLAUDE_PROJECT_DIR}" in violations[0]


def test_inline_shell_preprocessor_detected(vg, tmp_path: Path) -> None:
    skill = _write(
        tmp_path / "src" / "skills" / "x" / "SKILL.md",
        """
        ---
        name: x
        description: bad.
        ---

        Current branch: !`git branch --show-current`
        """,
    )
    violations = vg.scan_file(skill)
    assert len(violations) == 1
    assert "!`git branch --show-current`" in violations[0]


def test_ask_user_question_detected(vg, tmp_path: Path) -> None:
    skill = _write(
        tmp_path / "src" / "skills" / "x" / "SKILL.md",
        """
        ---
        name: x
        description: bad.
        ---

        Use AskUserQuestion to prompt.
        """,
    )
    violations = vg.scan_file(skill)
    assert len(violations) == 1
    assert "AskUserQuestion" in violations[0]


def test_todo_write_detected(vg, tmp_path: Path) -> None:
    skill = _write(
        tmp_path / "src" / "skills" / "x" / "SKILL.md",
        """
        ---
        name: x
        description: bad.
        ---

        Update progress with TodoWrite.
        """,
    )
    violations = vg.scan_file(skill)
    assert len(violations) == 1
    assert "TodoWrite" in violations[0]


def test_multiple_violations_reported(vg, tmp_path: Path) -> None:
    skill = _write(
        tmp_path / "src" / "skills" / "x" / "SKILL.md",
        """
        ---
        name: x
        description: bad.
        ---

        Use Task() and TodoWrite together.
        Also $ARGUMENTS.
        """,
    )
    violations = vg.scan_file(skill)
    assert len(violations) == 3


def test_invalid_frontmatter_reported(vg, tmp_path: Path) -> None:
    skill = tmp_path / "src" / "skills" / "x" / "SKILL.md"
    skill.parent.mkdir(parents=True, exist_ok=True)
    skill.write_text("---\nname: [\nbroken\n---\nbody\n")
    violations = vg.scan_file(skill)
    assert len(violations) == 1
    assert "invalid frontmatter" in violations[0]


def test_line_numbers_account_for_frontmatter(vg, tmp_path: Path) -> None:
    skill = _write(
        tmp_path / "src" / "skills" / "x" / "SKILL.md",
        """
        ---
        name: x
        description: bad.
        ---

        # Heading

        Body uses $ARGUMENTS here.
        """,
    )
    violations = vg.scan_file(skill)
    assert len(violations) == 1
    # Frontmatter spans lines 1-4, blank line 5, heading line 6,
    # blank line 7, body line 8.
    assert ":8:" in violations[0], violations[0]


def test_discover_base_files(vg, tmp_path: Path) -> None:
    _write(tmp_path / "src" / "skills" / "a" / "SKILL.md", "---\nname: a\n---\n")
    _write(tmp_path / "src" / "agents" / "b" / "AGENT.md", "---\nname: b\n---\n")
    _write(tmp_path / "src" / "skills" / "a" / "claude" / "body.md", "junk")
    found = vg.discover_base_files(tmp_path)
    assert len(found) == 2
    assert any(p.name == "SKILL.md" for p in found)
    assert any(p.name == "AGENT.md" for p in found)


def test_repo_baselines_pass(vg) -> None:
    """Existing migrated src/ base files must already be vendor-neutral."""
    violations: list[str] = []
    for path in vg.discover_base_files():
        violations.extend(vg.scan_file(path))
    assert violations == [], "\n".join(violations)
