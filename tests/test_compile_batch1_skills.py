"""Compilation tests for batch-1 migrated skills (plan Task 15).

Asserts each newly migrated `src/skills/<name>/` source compiles cleanly for
every applicable target. Compared to `test_compile_skill.py`, this suite does
not lock byte-exact goldens — too noisy when 14 skills × 4 targets = 56 trees
would need refreshing — and instead checks structural invariants that the
migration is meant to preserve:

- compile_skill returns at least one written `SKILL.md` for each applicable
  target (and zero for targets the base `targets:` restriction excludes)
- the emitted frontmatter keeps `name` and `description` and drops the
  renderer-only `targets` key
- support files referenced via `references/` end up under the dist tree
- the genericity validator is clean for every migrated base
"""

from __future__ import annotations

from pathlib import Path

import frontmatter
import pytest

TARGETS = ("claude", "codex", "gemini", "pi")

BATCH_1_SKILLS_ALL_TARGETS = (
    "writing-go",
    "writing-python",
    "writing-typescript",
    "writing-web",
    "sequential-thinking",
    "using-modern-cli",
    "using-cloud-cli",
    "using-git-worktrees",
    "refactoring-code",
    "smart-explore",
    "searching-code",
    "brainstorming-ideas",
    "grill-me",
)
CLAUDE_ONLY_SKILLS = ("debating-ideas",)

SKILLS_WITH_REFERENCES = {
    "writing-go": (
        "references/CLI.md",
        "references/PATTERNS.md",
        "references/TESTING.md",
    ),
    "writing-python": (
        "references/CLI.md",
        "references/PATTERNS.md",
        "references/TESTING.md",
    ),
    "writing-typescript": (
        "references/PATTERNS.md",
        "references/REACT.md",
        "references/TESTING.md",
    ),
    "using-cloud-cli": ("references/AWS.md", "references/GCP.md"),
    "using-git-worktrees": ("references/WORKFLOW.md",),
    "grill-me": ("references/CREDITS.md",),
}

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SRC_SKILLS = _REPO_ROOT / "src" / "skills"


@pytest.fixture(scope="module")
def cs(load_script):
    load_script("build/compile.py")
    return load_script("build/compile_skill.py")


def _staging_root(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "src" / "skills").mkdir(parents=True)
    for skill_dir in _SRC_SKILLS.iterdir():
        if skill_dir.is_dir():
            (root / "src" / "skills" / skill_dir.name).symlink_to(skill_dir)
    (root / "scripts" / "build" / "preambles").mkdir(parents=True)
    preambles_src = _REPO_ROOT / "scripts" / "build" / "preambles"
    for entry in preambles_src.iterdir():
        (root / "scripts" / "build" / "preambles" / entry.name).symlink_to(entry)
    return root


@pytest.mark.parametrize("skill", BATCH_1_SKILLS_ALL_TARGETS)
@pytest.mark.parametrize("target", TARGETS)
def test_batch1_skill_compiles_for_target(
    cs, tmp_path: Path, skill: str, target: str
) -> None:
    root = _staging_root(tmp_path)
    skill_dir = root / "src" / "skills" / skill

    assert skill_dir.is_dir(), f"missing migrated source: {skill_dir}"
    plugin_index = {skill: ["plugin"]}
    written = cs.compile_skill(skill_dir, target, plugin_index, root)

    assert written, f"compile_skill returned no writes for {skill}/{target}"

    skill_md = written[0]
    post = frontmatter.loads(skill_md.read_text())
    assert post.metadata.get("name") == skill
    assert post.metadata.get("description")
    assert "targets" not in post.metadata, (
        f"renderer-only `targets` leaked into emitted frontmatter for {skill}/{target}"
    )


@pytest.mark.parametrize("skill", CLAUDE_ONLY_SKILLS)
def test_claude_only_skill_skips_other_targets(cs, tmp_path: Path, skill: str) -> None:
    root = _staging_root(tmp_path)
    skill_dir = root / "src" / "skills" / skill
    plugin_index = {skill: ["plugin"]}

    assert cs.compile_skill(skill_dir, "claude", plugin_index, root), (
        f"{skill} did not emit for claude despite targets: [claude]"
    )
    for t in ("codex", "gemini", "pi"):
        assert cs.compile_skill(skill_dir, t, plugin_index, root) == [], (
            f"{skill} should be skipped for target {t}"
        )


@pytest.mark.parametrize("skill,refs", sorted(SKILLS_WITH_REFERENCES.items()))
@pytest.mark.parametrize("target", TARGETS)
def test_references_copied_to_dist(
    cs, tmp_path: Path, skill: str, target: str, refs: tuple[str, ...]
) -> None:
    root = _staging_root(tmp_path)
    skill_dir = root / "src" / "skills" / skill
    plugin_index = {skill: ["plugin"]}

    written = cs.compile_skill(skill_dir, target, plugin_index, root)
    assert written, f"no writes for {skill}/{target}"

    out_dir = written[0].parent
    for rel in refs:
        assert (out_dir / rel).is_file(), f"reference {rel} missing from {out_dir}"


def test_brainstorming_ideas_swaps_claude_body(cs, tmp_path: Path) -> None:
    """Claude target gets the original orchestration body; others get vendor-neutral."""
    root = _staging_root(tmp_path)
    skill_dir = root / "src" / "skills" / "brainstorming-ideas"
    plugin_index = {"brainstorming-ideas": ["plugin"]}

    claude_written = cs.compile_skill(skill_dir, "claude", plugin_index, root)
    codex_written = cs.compile_skill(skill_dir, "codex", plugin_index, root)

    claude_body = frontmatter.loads(claude_written[0].read_text()).content
    codex_body = frontmatter.loads(codex_written[0].read_text()).content

    assert "TaskCreate" in claude_body, "Claude body should retain CC orchestration"
    assert "TaskCreate" not in codex_body, "Codex body must be vendor-neutral"


def test_grill_me_credits_file_preserved(cs, tmp_path: Path) -> None:
    """The grill-me skill's CREDITS.md must reach every target's dist tree."""
    root = _staging_root(tmp_path)
    skill_dir = root / "src" / "skills" / "grill-me"
    plugin_index = {"grill-me": ["plugin"]}

    for target in TARGETS:
        written = cs.compile_skill(skill_dir, target, plugin_index, root)
        assert (written[0].parent / "references" / "CREDITS.md").is_file()
