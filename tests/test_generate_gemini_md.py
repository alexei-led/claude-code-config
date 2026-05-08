from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch

_spec = importlib.util.spec_from_file_location(
    "generate_gemini_md",
    Path(__file__).resolve().parent.parent / "scripts" / "generate-gemini-md.py",
)
assert _spec is not None and _spec.loader is not None
generate_gemini_md = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(generate_gemini_md)


def _make_flat_skill(tmp_path: Path, plugin: str, skill: str) -> None:
    target = tmp_path / "plugins" / plugin / "skills-codex" / skill
    target.mkdir(parents=True)
    (target / "SKILL.md").write_text("---\nname: test\n---\n", encoding="utf-8")
    flat = tmp_path / "flat" / "skills-codex"
    flat.mkdir(parents=True, exist_ok=True)
    (flat / skill).symlink_to(target, target_is_directory=True)


def test_builds_gemini_links_from_flat_skills(tmp_path):
    _make_flat_skill(tmp_path, "dev-workflow", "coding")
    _make_flat_skill(tmp_path, "go-dev", "writing-go")

    with (
        patch.object(generate_gemini_md, "ROOT", tmp_path),
        patch.object(
            generate_gemini_md, "FLAT_SKILLS", tmp_path / "flat" / "skills-codex"
        ),
    ):
        content = generate_gemini_md.compute_desired_content()

    assert "Total skills: 2" in content
    assert "## Development Workflow" in content
    assert "@flat/skills-codex/coding/SKILL.md" in content
    assert "## Go Development" in content
    assert "@flat/skills-codex/writing-go/SKILL.md" in content


def test_empty_flat_dir_generates_empty_catalog(tmp_path):
    (tmp_path / "flat" / "skills-codex").mkdir(parents=True)

    with patch.object(
        generate_gemini_md,
        "FLAT_SKILLS",
        tmp_path / "flat" / "skills-codex",
    ):
        content = generate_gemini_md.compute_desired_content()

    assert "Total skills: 0" in content
    assert "@flat/skills-codex" not in content
