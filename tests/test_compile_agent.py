"""Fixture-based golden tests for `scripts.build.compile_agent.compile_agent`.

Covered cases:

- `go-engineer` — base + per-target frontmatter overlay (tools/model/skills),
  no body overlay. Exercises all four targets: three markdown emissions and
  one Codex TOML conversion.
- `scout` — `targets: [pi]` restriction. Verifies only Pi receives an output;
  Claude/Codex/Gemini are skipped.

Each `(agent, target)` pair has a locked snapshot at
`tests/fixtures/golden_agents/<agent>/<target>/`. The test compiles each
agent into a tmp dist root and diffs the result against the snapshot.

Regenerating goldens: run `uv run python scripts/build/compile.py`, then
sync the relevant agent files from `dist/<target>/agents/` into
`tests/fixtures/golden_agents/<agent>/<target>/`.
"""

from __future__ import annotations

import filecmp
import tomllib
from pathlib import Path

import frontmatter
import pytest

ALL_TARGETS = ("claude", "codex", "gemini", "pi")

_REPO_ROOT = Path(__file__).resolve().parent.parent
_GOLDENS = _REPO_ROOT / "tests" / "fixtures" / "golden_agents"
_SRC_AGENTS = _REPO_ROOT / "src" / "agents"


@pytest.fixture(scope="module")
def ca(load_script):
    """Load `compile_agent.py` via the shared loader.

    `compile.py` and `codex_toml.py` must load first so their modules are
    cached on sys.modules under their bare names — `compile_agent` imports
    them directly.
    """
    load_script("build/compile.py")
    load_script("build/codex_toml.py")
    return load_script("build/compile_agent.py")


def _staging_root(tmp_path: Path) -> Path:
    """Layout a tmp repo whose `src/agents/` mirrors the real tree.

    The compiler resolves output dirs relative to `root`, so we need a `root`
    distinct from the real repo to keep tmp_path isolated from `dist/`.
    """
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    (root / "src" / "agents").symlink_to(_SRC_AGENTS)
    return root


def _norm_body(text: str) -> str:
    """Return non-blank, right-stripped lines joined with `\\n`.

    The project's markdown auto-formatter inserts or removes blank separator
    lines around sections that the compiler does not emit identically. Strip
    blank lines for the comparison.
    """
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _diff_files(golden: Path, actual: Path) -> str | None:
    """Return a diff message if files differ semantically, else None.

    `.md` files use parsed comparison (frontmatter dict + body string) so the
    test stays robust against YAML cosmetic differences introduced by the
    project's auto-formatter on the fixture files. `.toml` files use byte
    comparison since TOML is not auto-formatted in this repo.
    """
    if not actual.is_file():
        return f"missing actual file: {actual}"
    if actual.suffix == ".toml":
        if filecmp.cmp(golden, actual, shallow=False):
            return None
        # Fall back to parsed equality as a robustness net (TOML reformatting
        # is unlikely here but the message stays useful either way).
        try:
            golden_data = tomllib.loads(golden.read_text())
            actual_data = tomllib.loads(actual.read_text())
        except tomllib.TOMLDecodeError as e:
            return f"toml parse error at {actual.name}: {e}"
        if golden_data == actual_data:
            return None
        return (
            f"toml mismatch at {actual.name}\n"
            f"--- golden\n{golden.read_text(errors='replace')}\n"
            f"+++ actual\n{actual.read_text(errors='replace')}"
        )

    golden_post = frontmatter.loads(golden.read_text())
    actual_post = frontmatter.loads(actual.read_text())
    if dict(golden_post.metadata) != dict(actual_post.metadata):
        return (
            f"frontmatter mismatch at {actual.name}\n"
            f"--- golden meta\n{golden_post.metadata}\n"
            f"+++ actual meta\n{actual_post.metadata}"
        )
    if _norm_body(golden_post.content) != _norm_body(actual_post.content):
        return (
            f"body mismatch at {actual.name}\n"
            f"--- golden body\n{golden_post.content}\n"
            f"+++ actual body\n{actual_post.content}"
        )
    return None


@pytest.mark.parametrize("target", ALL_TARGETS)
def test_compile_agent_go_engineer_matches_golden(
    ca, tmp_path: Path, target: str
) -> None:
    """go-engineer compiles to .md for claude/gemini/pi, .toml for codex."""
    root = _staging_root(tmp_path)
    agent_dir = root / "src" / "agents" / "go-engineer"

    written = ca.compile_agent(agent_dir, target, None, root)
    assert written, f"compile_agent returned no writes for go-engineer/{target}"
    assert len(written) == 1

    ext = ".toml" if target == "codex" else ".md"
    actual = root / "dist" / target / "agents" / f"go-engineer{ext}"
    golden = _GOLDENS / "go-engineer" / target / f"go-engineer{ext}"

    assert golden.is_file(), f"missing golden snapshot: {golden}"
    diff = _diff_files(golden, actual)
    assert diff is None, diff


def test_compile_agent_scout_pi_only(ca, tmp_path: Path) -> None:
    """scout has `targets: [pi]` — only Pi receives an output."""
    root = _staging_root(tmp_path)
    agent_dir = root / "src" / "agents" / "scout"

    for target in ("claude", "codex", "gemini"):
        assert ca.compile_agent(agent_dir, target, None, root) == [], (
            f"scout should not emit for {target}"
        )

    written = ca.compile_agent(agent_dir, "pi", None, root)
    assert len(written) == 1
    actual = root / "dist" / "pi" / "agents" / "scout.md"
    golden = _GOLDENS / "scout" / "pi" / "scout.md"

    assert golden.is_file(), f"missing golden snapshot: {golden}"
    diff = _diff_files(golden, actual)
    assert diff is None, diff


def test_codex_target_emits_toml_extension(ca, tmp_path: Path) -> None:
    agent = tmp_path / "src" / "agents" / "tiny"
    agent.mkdir(parents=True)
    (agent / "AGENT.md").write_text(
        "---\nname: tiny\ndescription: small agent\n---\n\nbody.\n"
    )
    root = tmp_path / "repo"
    root.mkdir()

    written = ca.compile_agent(agent, "codex", None, root)
    assert len(written) == 1
    assert written[0].suffix == ".toml"
    text = written[0].read_text()
    assert text.startswith('name = "tiny"')
    assert 'description = "small agent"' in text
    assert "developer_instructions" in text


def test_md_targets_emit_md_extension(ca, tmp_path: Path) -> None:
    agent = tmp_path / "src" / "agents" / "tiny"
    agent.mkdir(parents=True)
    (agent / "AGENT.md").write_text(
        "---\nname: tiny\ndescription: small agent\n---\n\nbody.\n"
    )
    root = tmp_path / "repo"
    root.mkdir()

    for target in ("claude", "gemini", "pi"):
        written = ca.compile_agent(agent, target, None, root)
        assert len(written) == 1, target
        assert written[0].suffix == ".md", target
        text = written[0].read_text()
        assert text.startswith("---\n"), target
        assert "name: tiny" in text


def test_targets_restriction_string_form(ca, tmp_path: Path) -> None:
    agent = tmp_path / "src" / "agents" / "a"
    agent.mkdir(parents=True)
    (agent / "AGENT.md").write_text(
        "---\nname: a\ndescription: d\ntargets: pi\n---\n\nbody\n"
    )
    root = tmp_path / "repo"
    root.mkdir()

    assert ca.compile_agent(agent, "pi", None, root) != []
    assert ca.compile_agent(agent, "claude", None, root) == []


def test_targets_key_stripped_from_md_output(ca, tmp_path: Path) -> None:
    agent = tmp_path / "src" / "agents" / "a"
    agent.mkdir(parents=True)
    (agent / "AGENT.md").write_text(
        "---\nname: a\ndescription: d\ntargets:\n  - claude\n  - pi\n---\n\nbody\n"
    )
    root = tmp_path / "repo"
    root.mkdir()

    written = ca.compile_agent(agent, "claude", None, root)
    assert len(written) == 1
    assert "targets:" not in written[0].read_text()


def test_targets_key_stripped_from_toml_output(ca, tmp_path: Path) -> None:
    agent = tmp_path / "src" / "agents" / "a"
    agent.mkdir(parents=True)
    (agent / "AGENT.md").write_text(
        "---\nname: a\ndescription: d\ntargets:\n  - codex\n---\n\nbody\n"
    )
    root = tmp_path / "repo"
    root.mkdir()

    written = ca.compile_agent(agent, "codex", None, root)
    assert len(written) == 1
    assert "targets" not in written[0].read_text()


def test_name_injected_from_directory_when_missing(ca, tmp_path: Path) -> None:
    agent = tmp_path / "src" / "agents" / "from-dirname"
    agent.mkdir(parents=True)
    (agent / "AGENT.md").write_text(
        "---\ndescription: name not in frontmatter\n---\n\nbody\n"
    )
    root = tmp_path / "repo"
    root.mkdir()

    written = ca.compile_agent(agent, "claude", None, root)
    assert "name: from-dirname" in written[0].read_text()


def test_plugin_index_routes_to_plugin_dir(ca, tmp_path: Path) -> None:
    agent = tmp_path / "src" / "agents" / "my-agent"
    agent.mkdir(parents=True)
    (agent / "AGENT.md").write_text(
        "---\nname: my-agent\ndescription: routed via plugin index\n---\n\nbody\n"
    )
    root = tmp_path / "repo"
    root.mkdir()

    plugin_index = {"my-agent": ["alpha", "beta"]}
    written = ca.compile_agent(agent, "claude", plugin_index, root)
    assert len(written) == 2
    plugin_dirs = {p.parent.parent.name for p in written}
    assert plugin_dirs == {"alpha", "beta"}


def test_flat_layout_ignores_plugin_index(ca, tmp_path: Path) -> None:
    agent = tmp_path / "src" / "agents" / "my-agent"
    agent.mkdir(parents=True)
    (agent / "AGENT.md").write_text(
        "---\nname: my-agent\ndescription: flat path even with index\n---\n\nbody\n"
    )
    root = tmp_path / "repo"
    root.mkdir()

    plugin_index = {"my-agent": ["alpha"]}
    written = ca.compile_agent(agent, "pi", plugin_index, root)
    assert len(written) == 1
    assert written[0] == root / "dist" / "pi" / "agents" / "my-agent.md"


def test_body_overlay_applied_when_present(ca, tmp_path: Path) -> None:
    agent = tmp_path / "src" / "agents" / "with-overlay"
    (agent / "claude").mkdir(parents=True)
    (agent / "AGENT.md").write_text(
        "---\nname: with-overlay\ndescription: d\n---\n\n# Original\nbase body.\n"
    )
    (agent / "claude" / "body.md").write_text("# Replaced\nclaude-only body.\n")
    root = tmp_path / "repo"
    root.mkdir()

    written = ca.compile_agent(agent, "claude", None, root)
    text = written[0].read_text()
    assert "claude-only body." in text
    assert "base body." not in text
