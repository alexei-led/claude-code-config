"""Tests for the slim root-manifest validator."""

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


def _write(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


def _good_claude() -> dict:
    return {
        "name": "test-mp",
        "owner": {"name": "Test"},
        "plugins": [{"name": "p", "source": "./dist/claude/plugins/p"}],
    }


def _good_codex() -> dict:
    return {
        "name": "test-codex",
        "plugins": [{"name": "p", "source": {"path": "./dist/codex/plugins/p"}}],
    }


def _good_gemini() -> dict:
    return {"name": "ext", "version": "1.0.0", "description": "desc"}


class TestClaudeMarketplace:
    def test_valid(self, tmp_path):
        _write(tmp_path / ".claude-plugin" / "marketplace.json", _good_claude())
        with (
            patch.object(validate_config, "ROOT", tmp_path),
            patch.object(
                validate_config,
                "CLAUDE_MARKETPLACE",
                tmp_path / ".claude-plugin" / "marketplace.json",
            ),
        ):
            assert validate_config.validate_claude_marketplace() == []

    def test_missing_file(self, tmp_path):
        with (
            patch.object(validate_config, "ROOT", tmp_path),
            patch.object(
                validate_config,
                "CLAUDE_MARKETPLACE",
                tmp_path / ".claude-plugin" / "marketplace.json",
            ),
        ):
            errors = validate_config.validate_claude_marketplace()
        assert errors and "missing file" in errors[0]

    def test_missing_field(self, tmp_path):
        data = _good_claude()
        del data["owner"]
        _write(tmp_path / ".claude-plugin" / "marketplace.json", data)
        with (
            patch.object(validate_config, "ROOT", tmp_path),
            patch.object(
                validate_config,
                "CLAUDE_MARKETPLACE",
                tmp_path / ".claude-plugin" / "marketplace.json",
            ),
        ):
            errors = validate_config.validate_claude_marketplace()
        assert any("missing required field 'owner'" in e for e in errors)

    def test_bad_source_path(self, tmp_path):
        data = _good_claude()
        data["plugins"][0]["source"] = "./plugins/p"
        _write(tmp_path / ".claude-plugin" / "marketplace.json", data)
        with (
            patch.object(validate_config, "ROOT", tmp_path),
            patch.object(
                validate_config,
                "CLAUDE_MARKETPLACE",
                tmp_path / ".claude-plugin" / "marketplace.json",
            ),
        ):
            errors = validate_config.validate_claude_marketplace()
        assert any("./dist/claude/" in e for e in errors)


class TestCodexMarketplace:
    def test_valid(self, tmp_path):
        _write(tmp_path / ".agents" / "plugins" / "marketplace.json", _good_codex())
        with (
            patch.object(validate_config, "ROOT", tmp_path),
            patch.object(
                validate_config,
                "CODEX_MARKETPLACE",
                tmp_path / ".agents" / "plugins" / "marketplace.json",
            ),
        ):
            assert validate_config.validate_codex_marketplace() == []

    def test_bad_source_path(self, tmp_path):
        data = _good_codex()
        data["plugins"][0]["source"]["path"] = "./plugins/p"
        _write(tmp_path / ".agents" / "plugins" / "marketplace.json", data)
        with (
            patch.object(validate_config, "ROOT", tmp_path),
            patch.object(
                validate_config,
                "CODEX_MARKETPLACE",
                tmp_path / ".agents" / "plugins" / "marketplace.json",
            ),
        ):
            errors = validate_config.validate_codex_marketplace()
        assert any("./dist/codex/" in e for e in errors)


class TestGeminiExtension:
    def test_valid(self, tmp_path):
        _write(tmp_path / "gemini-extension.json", _good_gemini())
        with (
            patch.object(validate_config, "ROOT", tmp_path),
            patch.object(
                validate_config,
                "GEMINI_EXTENSION",
                tmp_path / "gemini-extension.json",
            ),
        ):
            assert validate_config.validate_gemini_extension() == []

    def test_missing_field(self, tmp_path):
        data = _good_gemini()
        del data["version"]
        _write(tmp_path / "gemini-extension.json", data)
        with (
            patch.object(validate_config, "ROOT", tmp_path),
            patch.object(
                validate_config,
                "GEMINI_EXTENSION",
                tmp_path / "gemini-extension.json",
            ),
        ):
            errors = validate_config.validate_gemini_extension()
        assert any("missing required field 'version'" in e for e in errors)


class TestAgentsMd:
    def test_present(self, tmp_path):
        (tmp_path / "AGENTS.md").write_text("# Agents")
        with patch.object(validate_config, "ROOT", tmp_path):
            assert validate_config.validate_agents_md() == []

    def test_missing(self, tmp_path):
        with patch.object(validate_config, "ROOT", tmp_path):
            assert validate_config.validate_agents_md() != []


class TestMain:
    def test_all_good(self, tmp_path):
        _write(tmp_path / ".claude-plugin" / "marketplace.json", _good_claude())
        _write(tmp_path / ".agents" / "plugins" / "marketplace.json", _good_codex())
        _write(tmp_path / "gemini-extension.json", _good_gemini())
        (tmp_path / "AGENTS.md").write_text("# Agents")
        with (
            patch.object(validate_config, "ROOT", tmp_path),
            patch.object(
                validate_config,
                "CLAUDE_MARKETPLACE",
                tmp_path / ".claude-plugin" / "marketplace.json",
            ),
            patch.object(
                validate_config,
                "CODEX_MARKETPLACE",
                tmp_path / ".agents" / "plugins" / "marketplace.json",
            ),
            patch.object(
                validate_config,
                "GEMINI_EXTENSION",
                tmp_path / "gemini-extension.json",
            ),
        ):
            assert validate_config.main() == 0
