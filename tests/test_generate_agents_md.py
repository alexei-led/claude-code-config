"""Tests for the AGENTS.md generator."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from unittest.mock import patch

import frontmatter

_spec = importlib.util.spec_from_file_location(
    "generate_agents_md",
    Path(__file__).resolve().parent.parent / "scripts" / "generate-agents-md.py",
)
assert _spec is not None and _spec.loader is not None
gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen)


def _make_skill(
    skills_codex: Path,
    plugin_dir: Path,
    skill_name: str,
    name: str,
    description: str,
) -> None:
    """Create a skill in plugin's skills-codex/ and symlink from flat."""
    # Create actual skill file
    actual = plugin_dir / "skills-codex" / skill_name
    actual.mkdir(parents=True, exist_ok=True)
    post = frontmatter.Post("", name=name, description=description)
    (actual / "SKILL.md").write_text(frontmatter.dumps(post) + "\n")
    # Symlink from flat/skills-codex/ to plugin's skills-codex/
    link = skills_codex / skill_name
    target = os.path.relpath(actual, link.parent)
    link.symlink_to(target)


class TestCollectSkills:
    def test_empty_directory(self, tmp_path: Path) -> None:
        flat = tmp_path / "flat" / "skills-codex"
        flat.mkdir(parents=True)
        with patch.object(gen, "FLAT_SKILLS", flat):
            groups = gen.collect_skills()
        assert groups == {}

    def test_missing_directory(self, tmp_path: Path) -> None:
        flat = tmp_path / "flat" / "skills-codex"
        with patch.object(gen, "FLAT_SKILLS", flat):
            groups = gen.collect_skills()
        assert groups == {}

    def test_single_skill(self, tmp_path: Path) -> None:
        flat = tmp_path / "flat" / "skills-codex"
        flat.mkdir(parents=True)
        plugins = tmp_path / "plugins" / "go-dev"
        plugins.mkdir(parents=True)
        _make_skill(flat, plugins, "writing-go", "writing-go", "Idiomatic Go")
        with patch.object(gen, "FLAT_SKILLS", flat):
            groups = gen.collect_skills()
        assert "go-dev" in groups
        assert groups["go-dev"] == [("writing-go", "Idiomatic Go")]

    def test_multiple_plugins(self, tmp_path: Path) -> None:
        flat = tmp_path / "flat" / "skills-codex"
        flat.mkdir(parents=True)
        for plugin, skill, name, desc in [
            ("go-dev", "writing-go", "writing-go", "Go dev"),
            ("python-dev", "writing-python", "writing-python", "Python dev"),
        ]:
            pdir = tmp_path / "plugins" / plugin
            pdir.mkdir(parents=True)
            _make_skill(flat, pdir, skill, name, desc)
        with patch.object(gen, "FLAT_SKILLS", flat):
            groups = gen.collect_skills()
        assert len(groups) == 2
        assert "go-dev" in groups
        assert "python-dev" in groups


class TestFirstSentence:
    def test_use_when_pattern(self) -> None:
        text = "Smart commits. Use when user says commit"
        assert gen.first_sentence(text) == "Smart commits"

    def test_period_space(self) -> None:
        text = "First sentence. Second sentence."
        assert gen.first_sentence(text) == "First sentence"

    def test_no_period(self) -> None:
        text = "Short description"
        assert gen.first_sentence(text) == "Short description"

    def test_trailing_period_stripped(self) -> None:
        text = "A single sentence."
        assert gen.first_sentence(text) == "A single sentence"

    def test_em_dash_cap(self) -> None:
        text = "X" * 50 + " — " + "Y" * 80
        result = gen.first_sentence(text)
        assert result == "X" * 50

    def test_hard_cap(self) -> None:
        text = "A " + "word " * 30
        result = gen.first_sentence(text.strip())
        assert len(result) <= 100


class TestBuildContent:
    def test_header(self) -> None:
        content = gen.build_content({})
        assert "# cc-thingz Skills" in content
        assert "AGENTS.md" in content

    def test_with_skills(self) -> None:
        groups = {"go-dev": [("writing-go", "Go development")]}
        content = gen.build_content(groups)
        assert "## Go Development" in content
        assert "| writing-go | Go development |" in content

    def test_empty_plugin_skipped(self) -> None:
        groups = {"spec-system": []}
        content = gen.build_content(groups)
        assert "Spec-Driven" not in content

    def test_unknown_plugin_skipped(self) -> None:
        groups = {"nonexistent": [("foo", "bar")]}
        content = gen.build_content(groups)
        assert "foo" not in content


class TestCheckMode:
    def test_in_sync(self, tmp_path: Path) -> None:
        flat = tmp_path / "flat" / "skills-codex"
        flat.mkdir(parents=True)
        plugins = tmp_path / "plugins" / "go-dev"
        plugins.mkdir(parents=True)
        _make_skill(flat, plugins, "writing-go", "writing-go", "Go dev")
        output = tmp_path / "AGENTS.md"
        with (
            patch.object(gen, "FLAT_SKILLS", flat),
            patch.object(gen, "OUTPUT", output),
        ):
            content = gen.compute_desired_content()
            output.write_text(content)
            # Simulate --check
            assert output.read_text() == content

    def test_stale(self, tmp_path: Path) -> None:
        flat = tmp_path / "flat" / "skills-codex"
        flat.mkdir(parents=True)
        output = tmp_path / "AGENTS.md"
        output.write_text("stale content")
        with (
            patch.object(gen, "FLAT_SKILLS", flat),
            patch.object(gen, "OUTPUT", output),
        ):
            content = gen.compute_desired_content()
            assert output.read_text() != content
