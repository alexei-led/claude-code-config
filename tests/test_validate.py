"""Tests for the config validator."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from unittest.mock import patch

# Import validate-config.py dynamically (has hyphen in name)
_spec = importlib.util.spec_from_file_location(
    "validate_config",
    Path(__file__).resolve().parent.parent / "scripts" / "validate-config.py",
)
validate_config = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate_config)


class TestFrontmatterValidation:
    def test_valid_skill(self, tmp_path):
        skill_dir = tmp_path / "skills" / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: test-skill\ndescription: A test skill\n---\n# Test\n"
        )
        with patch.object(validate_config, "ROOT", tmp_path):
            spec = {"glob": "skills/*/SKILL.md", "required": ["name", "description"]}
            errors = validate_config.validate_frontmatter("skill", spec)
        assert not any("ERROR" in e for e in errors)

    def test_missing_name(self, tmp_path):
        skill_dir = tmp_path / "skills" / "bad-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\ndescription: Missing name field\n---\n# Bad\n"
        )
        with patch.object(validate_config, "ROOT", tmp_path):
            spec = {"glob": "skills/*/SKILL.md", "required": ["name", "description"]}
            errors = validate_config.validate_frontmatter("skill", spec)
        assert any("missing required field 'name'" in e for e in errors)

    def test_valid_agent(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "test-agent.md").write_text(
            "---\nname: test-agent\ndescription: A test\ntools: [Read, Grep]\n---\n"
        )
        with patch.object(validate_config, "ROOT", tmp_path):
            spec = {
                "glob": "agents/**/*.md",
                "required": ["name", "description", "tools"],
            }
            errors = validate_config.validate_frontmatter("agent", spec)
        assert not any("ERROR" in e for e in errors)

    def test_no_frontmatter(self, tmp_path):
        skill_dir = tmp_path / "skills" / "bare-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# No frontmatter here\n")
        with patch.object(validate_config, "ROOT", tmp_path):
            spec = {"glob": "skills/*/SKILL.md", "required": ["name"]}
            errors = validate_config.validate_frontmatter("skill", spec)
        assert any("no YAML frontmatter" in e for e in errors)

    def test_system_skills_skipped(self, tmp_path):
        skill_dir = tmp_path / "skills" / ".system" / "internal"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("no frontmatter at all")
        with patch.object(validate_config, "ROOT", tmp_path):
            spec = {"glob": "skills/*/SKILL.md", "required": ["name"]}
            errors = validate_config.validate_frontmatter("skill", spec)
        # .system should be skipped, so no errors about it
        assert not any(".system" in e for e in errors)


class TestSkillFolders:
    def test_missing_skill_md(self, tmp_path):
        (tmp_path / "skills" / "orphan-skill").mkdir(parents=True)
        with patch.object(validate_config, "ROOT", tmp_path):
            errors = validate_config.validate_skill_folders()
        assert any("missing SKILL.md" in e for e in errors)

    def test_valid_folders(self, tmp_path):
        skill_dir = tmp_path / "skills" / "good-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: good\n---\n")
        with patch.object(validate_config, "ROOT", tmp_path):
            errors = validate_config.validate_skill_folders()
        assert not errors


class TestCommandToolsFormat:
    def test_string_tools_flagged(self, tmp_path):
        cmd_dir = tmp_path / "commands"
        cmd_dir.mkdir(parents=True)
        (cmd_dir / "bad.md").write_text(
            '---\ndescription: test\nallowed-tools: "Read, Grep"\n---\n'
        )
        with patch.object(validate_config, "ROOT", tmp_path):
            errors = validate_config.validate_command_tools_format()
        assert any("should be a list" in e for e in errors)

    def test_list_tools_ok(self, tmp_path):
        cmd_dir = tmp_path / "commands"
        cmd_dir.mkdir(parents=True)
        (cmd_dir / "good.md").write_text(
            "---\ndescription: test\nallowed-tools: [Read, Grep]\n---\n"
        )
        with patch.object(validate_config, "ROOT", tmp_path):
            errors = validate_config.validate_command_tools_format()
        assert not errors


class TestTomlValidation:
    def test_valid_toml(self, tmp_path):
        (tmp_path / "test.toml").write_text('[section]\nkey = "value"\n')
        with patch.object(validate_config, "ROOT", tmp_path):
            errors = validate_config.validate_toml_files()
        assert not errors

    def test_invalid_toml(self, tmp_path):
        (tmp_path / "bad.toml").write_text("this is not valid toml {{{\n")
        with patch.object(validate_config, "ROOT", tmp_path):
            errors = validate_config.validate_toml_files()
        assert any("invalid TOML" in e for e in errors)


class TestJsonValidation:
    def test_valid_json(self, tmp_path):
        (tmp_path / "hook-config.json").write_text(
            '{"file-protector": {}, "smart-lint": {}}'
        )
        keys = {
            "hook-config.json": ["file-protector", "smart-lint"],
        }
        with patch.object(validate_config, "ROOT", tmp_path):
            with patch.dict(validate_config.EXPECTED_JSON_KEYS, keys):
                errors = validate_config.validate_json_files()
        assert not any("ERROR" in e for e in errors)

    def test_invalid_json(self, tmp_path):
        (tmp_path / "hook-config.json").write_text("{bad json")
        keys = {"hook-config.json": []}
        with patch.object(validate_config, "ROOT", tmp_path):
            with patch.dict(validate_config.EXPECTED_JSON_KEYS, keys):
                errors = validate_config.validate_json_files()
        assert any("invalid JSON" in e for e in errors)
