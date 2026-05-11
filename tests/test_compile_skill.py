"""Fixture-based golden tests for `scripts.build.compile_skill.compile_skill`.

Three real skills cover the variations the pipeline must handle:

- `committing-code` — base only, no per-target body/frontmatter overlay.
- `reviewing-code` — Claude body overlay in mirror mode (`(\\_+)` suffixes).
- `playwright-skill` — Pi body overlay in full-replacement mode, plus support
  files (`scripts/`, `references/`) the overlay engine must copy across.

Each `(skill, target)` pair has a locked snapshot under
`tests/fixtures/golden_skills/<skill>/<target>/`. The test compiles each skill
into a tmp dist root and diffs the result against the snapshot. Regenerating
goldens: run `uv run python scripts/build/compile.py`, then sync the four
target dirs for the affected skills into `tests/fixtures/golden_skills/`.
"""

from __future__ import annotations

import filecmp
from pathlib import Path

import pytest

TARGETS = ("claude", "codex", "gemini", "pi")
GOLDEN_SKILLS = ("committing-code", "reviewing-code", "playwright-skill")

_REPO_ROOT = Path(__file__).resolve().parent.parent
_GOLDENS = _REPO_ROOT / "tests" / "fixtures" / "golden_skills"
_SRC_SKILLS = _REPO_ROOT / "src" / "skills"


@pytest.fixture(scope="module")
def cs(load_script):
    """Load `compile_skill.py` as a module via the shared loader."""
    # compile.py must load first so `compile_skill` can import it.
    load_script("build/compile.py")
    return load_script("build/compile_skill.py")


def _staging_root(tmp_path: Path) -> Path:
    """Layout a tmp repo that mirrors what compile_skill expects.

    Symlinks `src/` and `scripts/build/preambles/` so resolved paths line up
    with how `output_dirs` and `load_preamble` interpret their `root` arg.
    """
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    (root / "src" / "skills").symlink_to(_SRC_SKILLS)
    (root / "scripts" / "build" / "preambles").mkdir(parents=True)
    preambles_src = _REPO_ROOT / "scripts" / "build" / "preambles"
    for entry in preambles_src.iterdir():
        (root / "scripts" / "build" / "preambles" / entry.name).symlink_to(entry)
    return root


def _diff_trees(golden: Path, actual: Path) -> list[str]:
    """Return a list of human-readable diffs between two directory trees."""
    diffs: list[str] = []

    golden_files = {p.relative_to(golden) for p in golden.rglob("*") if p.is_file()}
    actual_files = {p.relative_to(actual) for p in actual.rglob("*") if p.is_file()}

    for missing in sorted(golden_files - actual_files):
        diffs.append(f"missing from output: {missing}")
    for extra in sorted(actual_files - golden_files):
        diffs.append(f"unexpected in output: {extra}")

    for rel in sorted(golden_files & actual_files):
        if not filecmp.cmp(golden / rel, actual / rel, shallow=False):
            golden_text = (golden / rel).read_text(errors="replace")
            actual_text = (actual / rel).read_text(errors="replace")
            diffs.append(
                f"content mismatch at {rel}\n"
                f"--- golden\n{golden_text}\n"
                f"+++ actual\n{actual_text}"
            )
    return diffs


@pytest.mark.parametrize("skill", GOLDEN_SKILLS)
@pytest.mark.parametrize("target", TARGETS)
def test_compile_skill_matches_golden(
    cs, tmp_path: Path, skill: str, target: str
) -> None:
    root = _staging_root(tmp_path)
    skill_dir = root / "src" / "skills" / skill

    written = cs.compile_skill(skill_dir, target, None, root)

    assert written, f"compile_skill returned no writes for {skill}/{target}"

    actual_dir = root / "dist" / target / "skills" / skill
    golden_dir = _GOLDENS / skill / target

    assert golden_dir.is_dir(), f"missing golden snapshot: {golden_dir}"
    diffs = _diff_trees(golden_dir, actual_dir)
    assert not diffs, "\n\n".join(diffs)


def test_targets_restriction_skips_skill(cs, tmp_path: Path) -> None:
    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: claude-only\ndescription: only on claude\n"
        "targets:\n  - claude\n---\n\nbody\n"
    )
    root = tmp_path / "repo"
    root.mkdir()

    assert cs.compile_skill(skill, "claude", None, root) != []
    assert cs.compile_skill(skill, "codex", None, root) == []
    assert cs.compile_skill(skill, "gemini", None, root) == []
    assert cs.compile_skill(skill, "pi", None, root) == []


def test_targets_string_form_accepted(cs, tmp_path: Path) -> None:
    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: pi-only\ndescription: only on pi\ntargets: pi\n---\n\nbody\n"
    )
    root = tmp_path / "repo"
    root.mkdir()

    assert cs.compile_skill(skill, "pi", None, root) != []
    assert cs.compile_skill(skill, "claude", None, root) == []


def test_targets_key_stripped_from_emitted_frontmatter(cs, tmp_path: Path) -> None:
    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\n"
        "name: leaks-targets\n"
        "description: targets key must not leak to dist\n"
        "targets:\n  - claude\n  - codex\n"
        "---\n\nbody\n"
    )
    root = tmp_path / "repo"
    root.mkdir()

    written = cs.compile_skill(skill, "claude", None, root)
    assert len(written) == 1
    text = written[0].read_text()
    assert "targets:" not in text.splitlines()[1:5], text


def test_preamble_injected_for_codex(cs, tmp_path: Path) -> None:
    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: preamble-check\n"
        "description: body should be preceded by preamble\n"
        "---\n\n# Body\n"
    )
    root = tmp_path / "repo"
    preambles = root / "scripts" / "build" / "preambles"
    preambles.mkdir(parents=True)
    (preambles / "platform.md").write_text("<!-- platform preamble -->\n")

    written = cs.compile_skill(skill, "codex", None, root)
    text = written[0].read_text()
    assert "<!-- platform preamble -->" in text
    assert text.index("<!-- platform preamble -->") < text.index("# Body")


def test_preamble_absent_for_claude(cs, tmp_path: Path) -> None:
    skill = tmp_path / "skill"
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        "---\nname: no-banner\ndescription: claude gets no banner\n---\n\n# Body\n"
    )
    root = tmp_path / "repo"
    preambles = root / "scripts" / "build" / "preambles"
    preambles.mkdir(parents=True)
    (preambles / "platform.md").write_text("<!-- BANNER-PLATFORM -->\n")
    (preambles / "pi.md").write_text("<!-- BANNER-PI -->\n")

    written = cs.compile_skill(skill, "claude", None, root)
    text = written[0].read_text()
    assert "BANNER-PLATFORM" not in text
    assert "BANNER-PI" not in text


def test_plugin_index_routes_to_plugin_dir(cs, tmp_path: Path) -> None:
    skill = tmp_path / "skill_root" / "my-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: my-skill\ndescription: routed via plugin index\n---\n\nbody\n"
    )
    root = tmp_path / "repo"
    root.mkdir()
    plugin_index = {"my-skill": ["alpha", "beta"]}

    written = cs.compile_skill(skill, "claude", plugin_index, root)
    parents = {p.parent.parent.parent.name for p in written}
    assert parents == {"alpha", "beta"}, written


def test_flat_layout_ignores_plugin_index(cs, tmp_path: Path) -> None:
    skill = tmp_path / "skill_root" / "my-skill"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: my-skill\ndescription: flat path even with index\n---\n\nbody\n"
    )
    root = tmp_path / "repo"
    root.mkdir()
    plugin_index = {"my-skill": ["alpha"]}

    written = cs.compile_skill(skill, "pi", plugin_index, root)
    assert len(written) == 1
    assert written[0] == root / "dist" / "pi" / "skills" / "my-skill" / "SKILL.md"
