from __future__ import annotations

import importlib.util
import io
import json
import subprocess

import pytest
from conftest import REPO_ROOT

MODULE_PATH = REPO_ROOT / "src" / "hooks" / "revdiff-plan-review" / "hook.py"


def load_module():
    spec = importlib.util.spec_from_file_location(
        "revdiff_plan_review_hook", MODULE_PATH
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_module_does_not_rewrite_ask_decisions():
    """Wrapper passes `ask` through verbatim; plan-mode extension surfaces it
    via the ask_user_question tool. The wrapper has no convert helper."""
    hook = load_module()
    assert not hasattr(hook, "convert_ask_to_allow")


def test_no_plugin_found_exits_zero(monkeypatch, tmp_path):
    hook = load_module()
    monkeypatch.setenv("PI_CODING_AGENT_DIR", str(tmp_path / "agent"))
    monkeypatch.delenv("PI_PACKAGE_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("sys.stdin", io.StringIO(""))

    with pytest.raises(SystemExit) as exc:
        hook.main()

    assert exc.value.code == 0


def test_candidate_roots_include_project_and_agent_dirs(monkeypatch, tmp_path):
    hook = load_module()
    agent = tmp_path / "agent"
    monkeypatch.setenv("PI_CODING_AGENT_DIR", str(agent))
    monkeypatch.delenv("PI_PACKAGE_DIR", raising=False)
    monkeypatch.chdir(tmp_path)

    roots = hook.candidate_roots()

    assert (
        tmp_path
        / ".pi"
        / "git"
        / "github.com"
        / "umputun"
        / "revdiff"
        / "plugins"
        / "revdiff-planning"
        in roots
    )
    assert (
        agent
        / "git"
        / "github.com"
        / "umputun"
        / "revdiff"
        / "plugins"
        / "revdiff-planning"
        in roots
    )


def test_resolve_timeout_uses_env_var_with_kill_margin(monkeypatch):
    hook = load_module()
    monkeypatch.setenv("PI_HOOK_TIMEOUT_SEC", "600")
    # Subprocess timeout sits below the parent kill so the child exits with a
    # blocking message before SIGKILL.
    assert hook.resolve_timeout() == 600 - hook._PARENT_KILL_MARGIN_SEC


def test_resolve_timeout_falls_back_when_env_missing_or_garbage(monkeypatch):
    hook = load_module()
    monkeypatch.delenv("PI_HOOK_TIMEOUT_SEC", raising=False)
    assert hook.resolve_timeout() == hook._FALLBACK_TIMEOUT_SEC

    monkeypatch.setenv("PI_HOOK_TIMEOUT_SEC", "not-a-number")
    assert hook.resolve_timeout() == hook._FALLBACK_TIMEOUT_SEC

    monkeypatch.setenv("PI_HOOK_TIMEOUT_SEC", "0")
    assert hook.resolve_timeout() == hook._FALLBACK_TIMEOUT_SEC

    monkeypatch.setenv("PI_HOOK_TIMEOUT_SEC", "-7")
    assert hook.resolve_timeout() == hook._FALLBACK_TIMEOUT_SEC


def test_resolve_timeout_clamps_short_parent_to_one(monkeypatch):
    hook = load_module()
    monkeypatch.setenv("PI_HOOK_TIMEOUT_SEC", "1")
    # 1 - margin would go below 1; clamp keeps a non-zero positive timeout.
    assert hook.resolve_timeout() == 1


def test_main_invokes_plugin_and_passes_through_ask(monkeypatch, tmp_path, capsys):
    hook = load_module()
    plugin_root = (
        tmp_path
        / "agent"
        / "git"
        / "github.com"
        / "umputun"
        / "revdiff"
        / "plugins"
        / "revdiff-planning"
    )
    script = plugin_root / "scripts" / "plan-review-hook.py"
    script.parent.mkdir(parents=True)
    script.write_text("#!/usr/bin/env python3\n")
    monkeypatch.setenv("PI_CODING_AGENT_DIR", str(tmp_path / "agent"))
    monkeypatch.delenv("PI_PACKAGE_DIR", raising=False)
    monkeypatch.chdir(tmp_path)

    def fake_run(*args, **kwargs):
        assert args[0][1] == str(script)
        assert kwargs["env"]["CLAUDE_PLUGIN_ROOT"] == str(plugin_root)
        assert "PYTHONPATH" not in kwargs["env"]
        return subprocess.CompletedProcess(
            args=args[0],
            returncode=0,
            stdout=json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "ask",
                    }
                }
            ),
            stderr="",
        )

    monkeypatch.setattr(hook.subprocess, "run", fake_run)
    monkeypatch.setattr(hook.sys, "stdin", io.StringIO(""))

    with pytest.raises(SystemExit) as exc:
        hook.main()

    assert exc.value.code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["hookSpecificOutput"]["permissionDecision"] == "ask"
