"""Tests for `scripts.build.compile_hook` (Task 10).

Covers:

- HookSpec loading from `meta.yaml` + lone `HOOK.*` resolution and validation
- Script placement per target (flat vs plugin-grouped) with mode preservation
- Support-dir mirroring alongside the script
- Gemini aggregated `hooks.json` shape (BeforeTool/AfterTool/SessionStart,
  sequential markers, `${extensionPath}/hooks/<script>` substitution)
- Codex per-plugin `codex.hooks.json` shape (PreToolUse/PostToolUse/
  SessionStart, `$PLUGIN_ROOT/hooks/<script>` substitution, statusMessage)
- Claude / Pi receive no manifest in v1
- CC-only events (notification, worktreecreate, worktreeremove) are dropped
  from Gemini/Codex manifests
"""

from __future__ import annotations

import json
import stat
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def ch(load_script):
    """Load `compile_hook.py` via the shared loader (compile.py must come first)."""
    load_script("build/compile.py")
    return load_script("build/compile_hook.py")


def _write_hook(
    src: Path,
    name: str,
    event: str,
    *,
    timeout: int = 10,
    status_message: str | None = None,
    ext: str = ".sh",
    body: str = "#!/usr/bin/env bash\nexit 0\n",
    executable: bool = True,
    support_dirs: dict[str, dict[str, str]] | None = None,
) -> Path:
    """Build a `src/hooks/<name>/` source tree under `src` and return its path."""
    hook_dir = src / "hooks" / name
    hook_dir.mkdir(parents=True)
    meta_lines = [f"name: {name}", f"event: {event}", f"timeout: {timeout}"]
    if status_message is not None:
        meta_lines.append(f"status_message: {status_message}")
    (hook_dir / "meta.yaml").write_text("\n".join(meta_lines) + "\n")
    script = hook_dir / f"HOOK{ext}"
    script.write_text(body)
    if executable:
        script.chmod(script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP)
    for dir_name, files in (support_dirs or {}).items():
        sub = hook_dir / dir_name
        sub.mkdir()
        for fname, content in files.items():
            (sub / fname).write_text(content)
    return hook_dir


# --- HookSpec loading -------------------------------------------------------


def test_load_hook_minimal(ch, tmp_path):
    hook_dir = _write_hook(tmp_path / "src", "smart-lint", "postedit", timeout=60)
    spec = ch.load_hook(hook_dir)
    assert spec.name == "smart-lint"
    assert spec.event == "postedit"
    assert spec.timeout == 60
    assert spec.script_basename == "smart-lint.sh"
    assert spec.status_message is None


def test_load_hook_with_status_message(ch, tmp_path):
    hook_dir = _write_hook(
        tmp_path / "src",
        "session-start",
        "sessionstart",
        timeout=5,
        status_message="Loading context",
        ext=".py",
        body="#!/usr/bin/env python3\n",
    )
    spec = ch.load_hook(hook_dir)
    assert spec.script_basename == "session-start.py"
    assert spec.status_message == "Loading context"


def test_load_hook_missing_meta(ch, tmp_path):
    hook_dir = tmp_path / "src" / "hooks" / "broken"
    hook_dir.mkdir(parents=True)
    (hook_dir / "HOOK.sh").write_text("#!/bin/sh\n")
    with pytest.raises(FileNotFoundError, match="meta.yaml"):
        ch.load_hook(hook_dir)


def test_load_hook_missing_script(ch, tmp_path):
    hook_dir = tmp_path / "src" / "hooks" / "no-script"
    hook_dir.mkdir(parents=True)
    (hook_dir / "meta.yaml").write_text("name: x\nevent: postedit\ntimeout: 1\n")
    with pytest.raises(FileNotFoundError, match="HOOK"):
        ch.load_hook(hook_dir)


def test_load_hook_multiple_scripts(ch, tmp_path):
    hook_dir = tmp_path / "src" / "hooks" / "dup"
    hook_dir.mkdir(parents=True)
    (hook_dir / "meta.yaml").write_text("name: dup\nevent: postedit\ntimeout: 1\n")
    (hook_dir / "HOOK.sh").write_text("#!/bin/sh\n")
    (hook_dir / "HOOK.py").write_text("#!/usr/bin/env python3\n")
    with pytest.raises(ValueError, match="multiple"):
        ch.load_hook(hook_dir)


def test_load_hook_unknown_event(ch, tmp_path):
    hook_dir = tmp_path / "src" / "hooks" / "weird"
    hook_dir.mkdir(parents=True)
    (hook_dir / "meta.yaml").write_text("name: weird\nevent: madeup\ntimeout: 1\n")
    (hook_dir / "HOOK.sh").write_text("#!/bin/sh\n")
    with pytest.raises(ValueError, match="unknown event"):
        ch.load_hook(hook_dir)


def test_load_hook_missing_required_field(ch, tmp_path):
    hook_dir = tmp_path / "src" / "hooks" / "partial"
    hook_dir.mkdir(parents=True)
    (hook_dir / "meta.yaml").write_text("name: partial\nevent: postedit\n")
    (hook_dir / "HOOK.sh").write_text("#!/bin/sh\n")
    with pytest.raises(ValueError, match="timeout"):
        ch.load_hook(hook_dir)


# --- compile_hook (placement) ----------------------------------------------


def test_compile_hook_flat_target_pi(ch, tmp_path):
    src = tmp_path / "src"
    hook_dir = _write_hook(src, "smart-lint", "postedit", timeout=60)
    result = ch.compile_hook(hook_dir, "pi", {}, tmp_path)
    assert len(result.placements) == 1
    dest, plugin = result.placements[0]
    assert dest == tmp_path / "dist" / "pi" / "hooks" / "smart-lint.sh"
    assert dest.is_file()
    assert plugin is None
    # Mode preserved (executable bit).
    assert dest.stat().st_mode & stat.S_IXUSR


def test_compile_hook_flat_target_gemini(ch, tmp_path):
    src = tmp_path / "src"
    hook_dir = _write_hook(src, "smart-lint", "postedit")
    result = ch.compile_hook(hook_dir, "gemini", {}, tmp_path)
    assert result.placements[0][0] == (
        tmp_path / "dist" / "gemini" / "hooks" / "smart-lint.sh"
    )


def test_compile_hook_plugin_grouped_with_index(ch, tmp_path):
    src = tmp_path / "src"
    hook_dir = _write_hook(src, "smart-lint", "postedit")
    plugin_index = {"smart-lint": ["dev-workflow", "go-dev"]}
    result = ch.compile_hook(hook_dir, "codex", plugin_index, tmp_path)
    paths = {p[0]: p[1] for p in result.placements}
    assert (
        tmp_path
        / "dist"
        / "codex"
        / "plugins"
        / "dev-workflow"
        / "hooks"
        / "smart-lint.sh"
    ) in paths
    assert (
        tmp_path / "dist" / "codex" / "plugins" / "go-dev" / "hooks" / "smart-lint.sh"
    ) in paths
    assert set(paths.values()) == {"dev-workflow", "go-dev"}


def test_compile_hook_plugin_grouped_empty_index_falls_back_flat(ch, tmp_path):
    src = tmp_path / "src"
    hook_dir = _write_hook(src, "smart-lint", "postedit")
    result = ch.compile_hook(hook_dir, "codex", {}, tmp_path)
    assert len(result.placements) == 1
    dest, plugin = result.placements[0]
    assert dest == tmp_path / "dist" / "codex" / "hooks" / "smart-lint.sh"
    assert plugin is None


def test_compile_hook_copies_support_dir(ch, tmp_path):
    src = tmp_path / "src"
    hook_dir = _write_hook(
        src,
        "smart-lint",
        "postedit",
        support_dirs={"smart-lint": {"linter.sh": "#!/bin/sh\necho lint\n"}},
    )
    ch.compile_hook(hook_dir, "pi", {}, tmp_path)
    helper = tmp_path / "dist" / "pi" / "hooks" / "smart-lint" / "linter.sh"
    assert helper.is_file()
    assert helper.read_text() == "#!/bin/sh\necho lint\n"


def test_compile_hook_ignores_target_subdirs(ch, tmp_path):
    src = tmp_path / "src"
    hook_dir = _write_hook(src, "smart-lint", "postedit")
    # Add a stray target-named subdir; must NOT be copied as support.
    (hook_dir / "claude").mkdir()
    (hook_dir / "claude" / "extra.txt").write_text("CC-only stuff")
    ch.compile_hook(hook_dir, "pi", {}, tmp_path)
    leaked = tmp_path / "dist" / "pi" / "hooks" / "claude"
    assert not leaked.exists()


# --- manifest building (Gemini) --------------------------------------------


def _compile_all(ch, hook_dirs, target, plugin_index, root):
    return [ch.compile_hook(h, target, plugin_index, root) for h in hook_dirs]


def test_gemini_manifest_aggregates_events(ch, tmp_path):
    src = tmp_path / "src"
    h_pre = _write_hook(src, "file-protector", "preedit", timeout=10)
    h_post = _write_hook(src, "smart-lint", "postedit", timeout=60)
    h_session = _write_hook(src, "session-start", "sessionstart", timeout=5)
    results = _compile_all(ch, [h_pre, h_post, h_session], "gemini", {}, tmp_path)
    written = ch.write_hook_manifests(results, "gemini", tmp_path)
    assert len(written) == 1
    manifest = json.loads(written[0].read_text())

    events = manifest["hooks"]
    assert set(events) == {"BeforeTool", "AfterTool", "SessionStart"}

    # BeforeTool: write_file|replace matcher present, sequential=True
    before = events["BeforeTool"][0]
    assert before["matcher"] == "write_file|replace"
    assert before["sequential"] is True
    assert before["hooks"][0]["command"] == "${extensionPath}/hooks/file-protector.sh"
    assert before["hooks"][0]["timeout"] == 10_000

    # AfterTool: write_file|replace matcher present
    after = events["AfterTool"][0]
    assert after["matcher"] == "write_file|replace"
    assert after["sequential"] is True
    assert after["hooks"][0]["name"] == "smart-lint"
    assert after["hooks"][0]["timeout"] == 60_000

    # SessionStart: no matcher key, no sequential key
    session = events["SessionStart"][0]
    assert "matcher" not in session
    assert "sequential" not in session
    assert session["hooks"][0]["command"] == "${extensionPath}/hooks/session-start.sh"


def test_gemini_manifest_drops_cc_only_events(ch, tmp_path):
    src = tmp_path / "src"
    h_notify = _write_hook(src, "notify", "notification")
    h_wt = _write_hook(src, "worktree-create", "worktreecreate")
    results = _compile_all(ch, [h_notify, h_wt], "gemini", {}, tmp_path)
    written = ch.write_hook_manifests(results, "gemini", tmp_path)
    # Both events have no Gemini mapping → no manifest emitted.
    assert written == []
    assert not (tmp_path / "dist" / "gemini" / "hooks" / "hooks.json").exists()


def test_gemini_manifest_prebash_routes_to_run_shell_command(ch, tmp_path):
    src = tmp_path / "src"
    hook = _write_hook(src, "git-guardrails", "prebash")
    results = _compile_all(ch, [hook], "gemini", {}, tmp_path)
    written = ch.write_hook_manifests(results, "gemini", tmp_path)
    manifest = json.loads(written[0].read_text())
    before = manifest["hooks"]["BeforeTool"][0]
    assert before["matcher"] == "run_shell_command"


# --- manifest building (Codex) ---------------------------------------------


def test_codex_manifest_per_plugin(ch, tmp_path):
    src = tmp_path / "src"
    h_prebash = _write_hook(
        src,
        "git-guardrails",
        "prebash",
        timeout=10,
        status_message="Checking git",
    )
    h_post = _write_hook(src, "smart-lint", "postedit", timeout=60)
    plugin_index = {
        "git-guardrails": ["dev-workflow"],
        "smart-lint": ["dev-workflow"],
    }
    results = _compile_all(ch, [h_prebash, h_post], "codex", plugin_index, tmp_path)
    written = ch.write_hook_manifests(results, "codex", tmp_path)
    assert len(written) == 1
    assert written[0] == (
        tmp_path
        / "dist"
        / "codex"
        / "plugins"
        / "dev-workflow"
        / "hooks"
        / "codex.hooks.json"
    )
    manifest = json.loads(written[0].read_text())
    assert set(manifest["hooks"]) == {"PreToolUse", "PostToolUse"}

    pre = manifest["hooks"]["PreToolUse"][0]
    assert pre["matcher"] == "^Bash$"
    assert pre["hooks"][0]["command"] == '"$PLUGIN_ROOT/hooks/git-guardrails.sh"'
    assert pre["hooks"][0]["timeout"] == 10
    assert pre["hooks"][0]["statusMessage"] == "Checking git"

    post = manifest["hooks"]["PostToolUse"][0]
    assert post["matcher"] == "^apply_patch$"
    assert "statusMessage" not in post["hooks"][0]


def test_codex_manifest_skips_when_no_plugin(ch, tmp_path):
    """With empty plugin_index, codex hooks land at flat fallback (no manifest)."""
    src = tmp_path / "src"
    hook = _write_hook(src, "smart-lint", "postedit")
    results = _compile_all(ch, [hook], "codex", {}, tmp_path)
    written = ch.write_hook_manifests(results, "codex", tmp_path)
    assert written == []


def test_codex_manifest_drops_cc_only_events(ch, tmp_path):
    src = tmp_path / "src"
    h_pre = _write_hook(src, "file-protector", "preedit")
    h_ups = _write_hook(src, "skill-enforcer", "userpromptsubmit")
    plugin_index = {
        "file-protector": ["dev-workflow"],
        "skill-enforcer": ["dev-workflow"],
    }
    results = _compile_all(ch, [h_pre, h_ups], "codex", plugin_index, tmp_path)
    written = ch.write_hook_manifests(results, "codex", tmp_path)
    # Both events have None for codex → no manifest written.
    assert written == []


def test_codex_manifest_multi_plugin(ch, tmp_path):
    src = tmp_path / "src"
    hook = _write_hook(src, "smart-lint", "postedit", timeout=60)
    plugin_index = {"smart-lint": ["plugin-a", "plugin-b"]}
    results = _compile_all(ch, [hook], "codex", plugin_index, tmp_path)
    written = ch.write_hook_manifests(results, "codex", tmp_path)
    assert len(written) == 2
    plugin_names = {p.parent.parent.name for p in written}
    assert plugin_names == {"plugin-a", "plugin-b"}


# --- manifest building (Claude / Pi) ---------------------------------------


def test_claude_no_manifest(ch, tmp_path):
    src = tmp_path / "src"
    hook = _write_hook(src, "smart-lint", "postedit")
    results = _compile_all(
        ch, [hook], "claude", {"smart-lint": ["dev-workflow"]}, tmp_path
    )
    written = ch.write_hook_manifests(results, "claude", tmp_path)
    assert written == []


def test_pi_no_manifest(ch, tmp_path):
    src = tmp_path / "src"
    hook = _write_hook(src, "smart-lint", "postedit")
    results = _compile_all(ch, [hook], "pi", {}, tmp_path)
    written = ch.write_hook_manifests(results, "pi", tmp_path)
    assert written == []


# --- end-to-end smoke -------------------------------------------------------


def test_real_src_hooks_compile(ch):
    """Smoke: every src/hooks/<name>/ loads cleanly."""
    repo = Path(__file__).resolve().parents[1]
    hook_root = repo / "src" / "hooks"
    if not hook_root.is_dir():
        pytest.skip("src/hooks not present")
    hooks = sorted(p for p in hook_root.iterdir() if p.is_dir())
    assert hooks, "expected migrated hooks under src/hooks/"
    for hook_dir in hooks:
        spec = ch.load_hook(hook_dir)
        assert spec.name == hook_dir.name
        assert spec.event in ch.EVENT_MAP


def test_real_src_hooks_gemini_manifest(ch, tmp_path):
    """End-to-end: compile every real hook for Gemini and inspect the manifest."""
    repo = Path(__file__).resolve().parents[1]
    hook_root = repo / "src" / "hooks"
    if not hook_root.is_dir():
        pytest.skip("src/hooks not present")
    hooks = sorted(p for p in hook_root.iterdir() if p.is_dir())
    results = [ch.compile_hook(h, "gemini", {}, tmp_path) for h in hooks]
    written = ch.write_hook_manifests(results, "gemini", tmp_path)
    if not written:
        pytest.skip("no Gemini-mappable events in real hooks")
    manifest = json.loads(written[0].read_text())
    assert "hooks" in manifest
    for event in manifest["hooks"]:
        assert event in ch.GEMINI_EVENT_ORDER
