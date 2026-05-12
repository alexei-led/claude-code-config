"""Tests for the compiler scaffold (Task 1).

Cover target-config sanity, source discovery, and the --dry-run entry point.
"""

from __future__ import annotations

import logging

import pytest


@pytest.fixture(scope="module")
def compile_mod(load_script):
    return load_script("build/compile.py")


def test_targets_list_complete(compile_mod):
    assert compile_mod.TARGETS == ["claude", "codex", "gemini", "pi"]


def test_output_has_entry_per_target(compile_mod):
    assert set(compile_mod.OUTPUT) == set(compile_mod.TARGETS)


def test_output_required_fields(compile_mod):
    for target, cfg in compile_mod.OUTPUT.items():
        for field in compile_mod.REQUIRED_OUTPUT_FIELDS:
            assert field in cfg, f"{target} missing {field}"
            assert isinstance(cfg[field], str) and cfg[field], (
                f"{target}.{field} must be a non-empty string"
            )


def test_layouts_match_design(compile_mod):
    layouts = {t: c["layout"] for t, c in compile_mod.OUTPUT.items()}
    assert layouts == {
        "claude": "plugin",
        "codex": "plugin",
        "gemini": "flat",
        "pi": "flat",
    }


def test_validate_output_config_passes(compile_mod):
    compile_mod.validate_output_config()  # must not raise


def test_validate_output_config_detects_missing_field(compile_mod, monkeypatch):
    broken = {t: dict(cfg) for t, cfg in compile_mod.OUTPUT.items()}
    del broken["claude"]["skill_dir"]
    monkeypatch.setattr(compile_mod, "OUTPUT", broken)
    with pytest.raises(ValueError, match="skill_dir"):
        compile_mod.validate_output_config()


def test_validate_output_config_detects_bad_layout(compile_mod, monkeypatch):
    broken = {t: dict(cfg) for t, cfg in compile_mod.OUTPUT.items()}
    broken["pi"]["layout"] = "bogus"
    monkeypatch.setattr(compile_mod, "OUTPUT", broken)
    with pytest.raises(ValueError, match="invalid layout"):
        compile_mod.validate_output_config()


def test_validate_output_config_detects_missing_target(compile_mod, monkeypatch):
    broken = {t: dict(cfg) for t, cfg in compile_mod.OUTPUT.items()}
    del broken["pi"]
    monkeypatch.setattr(compile_mod, "OUTPUT", broken)
    with pytest.raises(ValueError, match="pi"):
        compile_mod.validate_output_config()


def test_repo_root_points_at_repo(compile_mod):
    root = compile_mod.repo_root()
    assert (root / "src").is_dir()
    assert (root / "scripts" / "build" / "compile.py").is_file()


def test_discover_returns_sorted_dirs(compile_mod, tmp_path):
    (tmp_path / "b").mkdir()
    (tmp_path / "a").mkdir()
    (tmp_path / "c.txt").write_text("ignored")
    assert compile_mod.discover(tmp_path) == [tmp_path / "a", tmp_path / "b"]


def test_discover_missing_dir_returns_empty(compile_mod, tmp_path):
    assert compile_mod.discover(tmp_path / "nope") == []


def test_discover_finds_real_sources(compile_mod):
    root = compile_mod.repo_root()
    skills = compile_mod.discover(root / "src" / "skills")
    agents = compile_mod.discover(root / "src" / "agents")
    assert any(p.name == "committing-code" for p in skills)
    assert any(p.name == "go-engineer" for p in agents)


def test_main_dry_run_exits_zero(compile_mod, caplog):
    caplog.set_level(logging.INFO, logger="compile")
    assert compile_mod.main(["--dry-run"]) == 0
    messages = " ".join(r.getMessage() for r in caplog.records)
    assert "discovered" in messages
    assert "dry-run" in messages


def test_required_output_fields_includes_hook_dir(compile_mod):
    assert "hook_dir" in compile_mod.REQUIRED_OUTPUT_FIELDS
