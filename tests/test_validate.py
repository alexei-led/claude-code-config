"""Tests for the config validator."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

_spec = importlib.util.spec_from_file_location(
    "validate_config",
    Path(__file__).resolve().parent.parent
    / "scripts"
    / "validate"
    / "validate-config.py",
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


class TestGeminiExtension:
    def _write_flat_skill(self, tmp_path, skill):
        skill_dir = tmp_path / "flat" / "skills-codex" / skill
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("---\nname: test\n---\n")

    def test_root_gemini_count_must_match_flat_skill_count(self, tmp_path):
        self._write_flat_skill(tmp_path, "writing-go")
        (tmp_path / "gemini-extension.json").write_text(
            json.dumps(
                {
                    "name": "cc-thingz",
                    "version": "1.0.0",
                    "description": "29 portable development skills exported",
                }
            )
        )
        (tmp_path / "plugins").mkdir()

        with patch.object(validate_config, "ROOT", tmp_path):
            errors, warnings = validate_config.validate_gemini_extensions()

        assert not warnings
        assert any("declares 29 skills" in error for error in errors)


class TestPlatformOverlays:
    def test_clean_codex_overlay_passes(self, tmp_path):
        skill_dir = (
            tmp_path / "plugins" / "dev-tools" / "skills-codex" / "researching-web"
        )
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("Use available web research tools.\n")

        with patch.object(validate_config, "ROOT", tmp_path):
            errors = validate_config.validate_platform_overlays()

        assert not errors

    def test_claude_tool_leak_is_error(self, tmp_path):
        skill_dir = (
            tmp_path / "plugins" / "dev-tools" / "skills-codex" / "researching-web"
        )
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("Use AskUserQuestion or mcp__tool.\n")

        with patch.object(validate_config, "ROOT", tmp_path):
            errors = validate_config.validate_platform_overlays()

        assert any("AskUserQuestion" in error for error in errors)
        assert any("mcp__" in error for error in errors)


class TestPiExports:
    def _write_pi_skill(
        self,
        tmp_path: Path,
        name: str,
        body: str = "Body\n",
    ) -> Path:
        skill_dir = tmp_path / "flat" / "skills-pi" / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\ndescription: Test skill\n---\n{body}"
        )
        return skill_dir

    def _write_pi_agent(self, tmp_path: Path, name: str, frontmatter: str) -> Path:
        agent_dir = tmp_path / "flat" / "agents-pi"
        agent_dir.mkdir(parents=True, exist_ok=True)
        agent = agent_dir / f"{name}.md"
        agent.write_text(f"---\n{frontmatter}---\nBody\n")
        return agent

    def test_pi_skill_frontmatter_validates_name(self, tmp_path):
        self._write_pi_skill(tmp_path, "good-skill")
        bad = tmp_path / "flat" / "skills-pi" / "bad-skill"
        bad.mkdir(parents=True)
        (bad / "SKILL.md").write_text("---\nname: other\ndescription: Bad\n---\nBody\n")

        with patch.object(validate_config, "ROOT", tmp_path):
            errors = validate_config.validate_pi_skill_frontmatter()

        assert any("does not match directory" in error for error in errors)
        assert not any("good-skill" in error for error in errors)

    def test_pi_agent_frontmatter_rejects_unknown_fields_and_tools(self, tmp_path):
        self._write_pi_agent(
            tmp_path,
            "reviewer",
            "description: Review\ntools: read, Bash\ncolor: blue\n",
        )

        with patch.object(validate_config, "ROOT", tmp_path):
            errors = validate_config.validate_pi_agent_frontmatter()

        assert any("unsupported Pi agent field" in error for error in errors)
        assert any("unsupported tools entry 'Bash'" in error for error in errors)

    def test_pi_export_tool_name_leaks_are_errors(self, tmp_path):
        self._write_pi_skill(tmp_path, "docs", "Use WebFetch and mcp__context7.\n")

        with patch.object(validate_config, "ROOT", tmp_path):
            errors = validate_config.validate_pi_export_tool_names()

        assert any("WebFetch" in error for error in errors)
        assert any("mcp__" in error for error in errors)

    def test_pi_agent_skill_refs_must_resolve(self, tmp_path):
        self._write_pi_skill(tmp_path, "known-skill")
        self._write_pi_agent(
            tmp_path,
            "worker",
            "description: Work\ntools: read\nskills: known-skill, missing-skill\n",
        )

        with patch.object(validate_config, "ROOT", tmp_path):
            errors = validate_config.validate_pi_agent_skill_refs()

        assert any("missing-skill" in error for error in errors)
        assert not any("known-skill" in error for error in errors)

    def test_pi_skill_links_and_executable_scripts(self, tmp_path):
        skill_dir = self._write_pi_skill(
            tmp_path,
            "linked-skill",
            "See [ok](references/ok.md) and [bad](missing.md).\n",
        )
        (skill_dir / "references").mkdir()
        (skill_dir / "references" / "ok.md").write_text("ok\n")
        script = skill_dir / "scripts" / "run.sh"
        script.parent.mkdir()
        script.write_text("#!/bin/sh\n")

        with patch.object(validate_config, "ROOT", tmp_path):
            link_errors = validate_config.validate_pi_skill_links()
            exec_errors = validate_config.validate_pi_support_executables()

        assert any("missing.md" in error for error in link_errors)
        assert any("run.sh" in error for error in exec_errors)

    def test_ctx7_refs_must_exist(self, tmp_path):
        ctx7 = self._write_pi_skill(
            tmp_path,
            "context7-cli",
            "Run ctx7 library and ctx7 docs.\n",
        )
        (ctx7 / "references").mkdir()
        for name in ("docs.md", "skills.md", "setup.md"):
            (ctx7 / "references" / name).write_text("ref\n")
        self._write_pi_skill(
            tmp_path,
            "looking-up-docs",
            "Route to context7-cli with ctx7 library and ctx7 docs.\n",
        )

        with patch.object(validate_config, "ROOT", tmp_path):
            errors = validate_config.validate_ctx7_skill_refs()

        assert not errors


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
