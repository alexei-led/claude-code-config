"""Tests for the config validator."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

_spec = importlib.util.spec_from_file_location(
    "validate_config",
    Path(__file__).resolve().parent.parent / "scripts" / "validate-config.py",
)
assert _spec is not None and _spec.loader is not None
validate_config = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate_config)


class TestMarketplaceJson:
    def test_valid_marketplace(self, tmp_path):
        mp_dir = tmp_path / ".claude-plugin"
        mp_dir.mkdir()
        (mp_dir / "marketplace.json").write_text(
            json.dumps(
                {
                    "name": "test-mp",
                    "owner": {"name": "Test"},
                    "metadata": {
                        "description": "Test",
                        "version": "1.0.0",
                    },
                    "plugins": [
                        {
                            "name": "my-plugin",
                            "source": "./plugins/my-plugin",
                            "description": "A plugin",
                        }
                    ],
                }
            )
        )
        (tmp_path / "plugins" / "my-plugin").mkdir(parents=True)
        with patch.object(validate_config, "ROOT", tmp_path):
            errors, warnings = validate_config.validate_marketplace_json()
        assert not errors
        assert not warnings

    def test_missing_marketplace(self, tmp_path):
        with patch.object(validate_config, "ROOT", tmp_path):
            errors, _ = validate_config.validate_marketplace_json()
        assert any("not found" in e for e in errors)

    def test_missing_required_fields(self, tmp_path):
        mp_dir = tmp_path / ".claude-plugin"
        mp_dir.mkdir()
        (mp_dir / "marketplace.json").write_text("{}")
        with patch.object(validate_config, "ROOT", tmp_path):
            errors, _ = validate_config.validate_marketplace_json()
        assert any("'name'" in e for e in errors)
        assert any("'owner'" in e for e in errors)
        assert any("'plugins'" in e for e in errors)

    def test_non_kebab_case_name(self, tmp_path):
        mp_dir = tmp_path / ".claude-plugin"
        mp_dir.mkdir()
        (mp_dir / "marketplace.json").write_text(
            json.dumps(
                {
                    "name": "Bad Name",
                    "owner": {"name": "Test"},
                    "plugins": [],
                }
            )
        )
        with patch.object(validate_config, "ROOT", tmp_path):
            errors, _ = validate_config.validate_marketplace_json()
        assert any("not kebab-case" in e for e in errors)

    def test_duplicate_plugin_names(self, tmp_path):
        mp_dir = tmp_path / ".claude-plugin"
        mp_dir.mkdir()
        (mp_dir / "marketplace.json").write_text(
            json.dumps(
                {
                    "name": "test-mp",
                    "owner": {"name": "Test"},
                    "plugins": [
                        {"name": "dup", "source": "./a"},
                        {"name": "dup", "source": "./b"},
                    ],
                }
            )
        )
        with patch.object(validate_config, "ROOT", tmp_path):
            errors, _ = validate_config.validate_marketplace_json()
        assert any("duplicate" in e for e in errors)

    def test_missing_source_path(self, tmp_path):
        mp_dir = tmp_path / ".claude-plugin"
        mp_dir.mkdir()
        (mp_dir / "marketplace.json").write_text(
            json.dumps(
                {
                    "name": "test-mp",
                    "owner": {"name": "Test"},
                    "plugins": [
                        {
                            "name": "missing",
                            "source": "./plugins/nope",
                        }
                    ],
                }
            )
        )
        with patch.object(validate_config, "ROOT", tmp_path):
            errors, _ = validate_config.validate_marketplace_json()
        assert any("does not exist" in e for e in errors)

    def test_missing_metadata_warnings(self, tmp_path):
        mp_dir = tmp_path / ".claude-plugin"
        mp_dir.mkdir()
        (mp_dir / "marketplace.json").write_text(
            json.dumps(
                {
                    "name": "test-mp",
                    "owner": {"name": "Test"},
                    "plugins": [],
                }
            )
        )
        with patch.object(validate_config, "ROOT", tmp_path):
            _, warnings = validate_config.validate_marketplace_json()
        assert any("metadata.description" in w for w in warnings)
        assert any("metadata.version" in w for w in warnings)


class TestPluginJsons:
    def test_valid_plugin(self, tmp_path):
        pdir = tmp_path / "plugins" / "my-plugin" / ".claude-plugin"
        pdir.mkdir(parents=True)
        (pdir / "plugin.json").write_text(
            json.dumps(
                {
                    "name": "my-plugin",
                    "description": "Test",
                    "version": "1.0.0",
                }
            )
        )
        with patch.object(validate_config, "ROOT", tmp_path):
            errors, warnings = validate_config.validate_plugin_jsons()
        assert not errors
        assert not warnings

    def test_missing_required_fields(self, tmp_path):
        pdir = tmp_path / "plugins" / "bad" / ".claude-plugin"
        pdir.mkdir(parents=True)
        (pdir / "plugin.json").write_text("{}")
        with patch.object(validate_config, "ROOT", tmp_path):
            errors, _ = validate_config.validate_plugin_jsons()
        assert any("'name'" in e for e in errors)
        assert any("'description'" in e for e in errors)
        assert any("'version'" in e for e in errors)

    def test_name_dir_mismatch_warns(self, tmp_path):
        pdir = tmp_path / "plugins" / "dir-name" / ".claude-plugin"
        pdir.mkdir(parents=True)
        (pdir / "plugin.json").write_text(
            json.dumps(
                {
                    "name": "other-name",
                    "description": "Test",
                    "version": "1.0.0",
                }
            )
        )
        with patch.object(validate_config, "ROOT", tmp_path):
            _, warnings = validate_config.validate_plugin_jsons()
        assert any("doesn't match" in w for w in warnings)

    def test_non_kebab_case_plugin_name(self, tmp_path):
        pdir = tmp_path / "plugins" / "bad" / ".claude-plugin"
        pdir.mkdir(parents=True)
        (pdir / "plugin.json").write_text(
            json.dumps(
                {
                    "name": "BadName",
                    "description": "Test",
                    "version": "1.0.0",
                }
            )
        )
        with patch.object(validate_config, "ROOT", tmp_path):
            errors, _ = validate_config.validate_plugin_jsons()
        assert any("not kebab-case" in e for e in errors)


class TestFrontmatterValidation:
    def test_valid_skill_in_plugin(self, tmp_path):
        skill_dir = tmp_path / "plugins" / "test" / "skills" / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: test\ndescription: A test\n---\n# Test\n"
        )
        with patch.object(validate_config, "ROOT", tmp_path):
            spec = {
                "glob": "skills/*/SKILL.md",
                "required": ["name", "description"],
            }
            errors = validate_config.validate_frontmatter("skill", spec)
        assert not any("ERROR" in e for e in errors)

    def test_valid_skill(self, tmp_path):
        skill_dir = tmp_path / "skills" / "test-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\nname: test\ndescription: A test\n---\n# Test\n"
        )
        with patch.object(validate_config, "ROOT", tmp_path):
            spec = {
                "glob": "skills/*/SKILL.md",
                "required": ["name", "description"],
            }
            errors = validate_config.validate_frontmatter("skill", spec)
        assert not any("ERROR" in e for e in errors)

    def test_missing_name(self, tmp_path):
        skill_dir = tmp_path / "skills" / "bad-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            "---\ndescription: Missing name\n---\n# Bad\n"
        )
        with patch.object(validate_config, "ROOT", tmp_path):
            spec = {
                "glob": "skills/*/SKILL.md",
                "required": ["name", "description"],
            }
            errors = validate_config.validate_frontmatter("skill", spec)
        assert any("missing required field 'name'" in e for e in errors)

    def test_valid_agent(self, tmp_path):
        agents_dir = tmp_path / "agents"
        agents_dir.mkdir(parents=True)
        (agents_dir / "test-agent.md").write_text(
            "---\nname: test\ndescription: A test\ntools: [Read, Grep]\n---\n"
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
        assert not any(".system" in e for e in errors)


class TestSkillFolders:
    def test_missing_skill_md_in_plugin(self, tmp_path):
        orphan = tmp_path / "plugins" / "test" / "skills" / "orphan"
        orphan.mkdir(parents=True)
        with patch.object(validate_config, "ROOT", tmp_path):
            errors = validate_config.validate_skill_folders()
        assert any("missing SKILL.md" in e for e in errors)

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

    def test_plugin_commands_checked(self, tmp_path):
        cmd_dir = tmp_path / "plugins" / "test" / "commands"
        cmd_dir.mkdir(parents=True)
        (cmd_dir / "bad.md").write_text(
            '---\ndescription: test\nallowed-tools: "Read"\n---\n'
        )
        with patch.object(validate_config, "ROOT", tmp_path):
            errors = validate_config.validate_command_tools_format()
        assert any("should be a list" in e for e in errors)


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
