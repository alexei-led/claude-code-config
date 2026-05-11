from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

_spec = importlib.util.spec_from_file_location(
    "generate_hooks",
    Path(__file__).resolve().parent.parent / "scripts" / "build" / "generate-hooks.py",
)
assert _spec is not None and _spec.loader is not None
gen = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = gen
_spec.loader.exec_module(gen)


# --- schema validation ---


def test_validate_unknown_event(tmp_path):
    with pytest.raises(ValueError, match="unknown event"):
        gen.validate_source(
            {"bogus": [{"script": "x.sh", "timeout": 5}]}, "p", tmp_path
        )


def test_validate_missing_required_fields(tmp_path):
    with pytest.raises(ValueError, match="missing"):
        gen.validate_source({"sessionstart": [{"script": "x.sh"}]}, "p", tmp_path)


def test_validate_event_not_list(tmp_path):
    with pytest.raises(ValueError, match="must be a list"):
        gen.validate_source(
            {"sessionstart": {"script": "x.sh", "timeout": 5}}, "p", tmp_path
        )


def test_validate_valid_source_passes(tmp_path):
    hooks_dir = tmp_path / "hooks"
    hooks_dir.mkdir()
    (hooks_dir / "s.sh").touch()
    gen.validate_source(
        {"sessionstart": [{"script": "s.sh", "timeout": 5}]}, "p", tmp_path
    )


def test_validate_missing_script_file(tmp_path):
    with pytest.raises(ValueError, match="script not found"):
        gen.validate_source(
            {"sessionstart": [{"script": "missing.sh", "timeout": 5}]}, "p", tmp_path
        )


# --- CC output ---


def test_cc_sessionstart():
    out = gen.build_cc(
        [
            (
                "myplugin",
                {
                    "sessionstart": [
                        {"script": "start.sh", "timeout": 5, "name": "start"}
                    ]
                },
            )
        ]
    )
    hooks = out["hooks"]
    assert "SessionStart" in hooks
    grp = hooks["SessionStart"][0]
    assert "matcher" not in grp
    assert "sequential" not in grp
    h = grp["hooks"][0]
    assert h["type"] == "command"
    assert h["name"] == "start"
    assert h["command"] == "${extensionPath}/plugins/myplugin/hooks/start.sh"
    assert h["timeout"] == 5000


def test_cc_preedit_sequential_no_codex():
    out = gen.build_cc(
        [
            (
                "p",
                {
                    "preedit": [
                        {"script": "protect.sh", "timeout": 10, "name": "protect"}
                    ]
                },
            )
        ]
    )
    hooks = out["hooks"]
    assert "BeforeTool" in hooks
    grp = hooks["BeforeTool"][0]
    assert grp["matcher"] == "write_file|replace"
    assert grp["sequential"] is True


def test_cc_prebash_before_tool():
    out = gen.build_cc(
        [("p", {"prebash": [{"script": "guard.sh", "timeout": 10, "name": "guard"}]})]
    )
    grp = out["hooks"]["BeforeTool"][0]
    assert grp["matcher"] == "run_shell_command"
    assert grp["sequential"] is True


def test_cc_postedit_after_tool():
    out = gen.build_cc(
        [("p", {"postedit": [{"script": "lint.sh", "timeout": 60, "name": "lint"}]})]
    )
    grp = out["hooks"]["AfterTool"][0]
    assert grp["matcher"] == "write_file|replace"
    assert grp["sequential"] is True


def test_cc_name_defaults_to_script_stem():
    out = gen.build_cc(
        [("p", {"sessionstart": [{"script": "my-hook.sh", "timeout": 5}]})]
    )
    h = out["hooks"]["SessionStart"][0]["hooks"][0]
    assert h["name"] == "my-hook"


def test_cc_timeout_multiplied_by_1000():
    out = gen.build_cc([("p", {"sessionstart": [{"script": "x.sh", "timeout": 7}]})])
    assert out["hooks"]["SessionStart"][0]["hooks"][0]["timeout"] == 7000


def test_cc_multi_plugin_aggregation():
    plugins = [
        ("plugin-a", {"sessionstart": [{"script": "a.sh", "timeout": 5, "name": "a"}]}),
        ("plugin-b", {"sessionstart": [{"script": "b.sh", "timeout": 5, "name": "b"}]}),
    ]
    out = gen.build_cc(plugins)
    # Same event from multiple plugins merges into one group's hooks array
    ss = out["hooks"]["SessionStart"]
    assert len(ss) == 1
    hooks = ss[0]["hooks"]
    assert len(hooks) == 2
    names = [h["name"] for h in hooks]
    assert "a" in names
    assert "b" in names
    cmds = [h["command"] for h in hooks]
    assert any("plugin-a" in c for c in cmds)
    assert any("plugin-b" in c for c in cmds)


def test_cc_event_order():
    """BeforeTool precedes AfterTool precedes SessionStart in output."""
    source = {
        "sessionstart": [{"script": "s.sh", "timeout": 5, "name": "s"}],
        "postedit": [{"script": "p.sh", "timeout": 60, "name": "p"}],
        "preedit": [{"script": "r.sh", "timeout": 10, "name": "r"}],
    }
    out = gen.build_cc([("p", source)])
    keys = list(out["hooks"])
    assert keys.index("BeforeTool") < keys.index("AfterTool")
    assert keys.index("AfterTool") < keys.index("SessionStart")


# --- Codex output ---


def test_codex_preedit_skipped():
    out = gen.build_codex({"preedit": [{"script": "protect.sh", "timeout": 10}]})
    assert "PreToolUse" not in out["hooks"]
    assert out["hooks"] == {}


def test_codex_prebash_maps_to_pretooluse():
    out = gen.build_codex(
        {
            "prebash": [
                {
                    "script": "guard.sh",
                    "timeout": 10,
                    "name": "guard",
                    "status_message": "checking",
                }
            ]
        }
    )
    hooks = out["hooks"]
    assert "PreToolUse" in hooks
    grp = hooks["PreToolUse"][0]
    assert grp["matcher"] == "^Bash$"
    h = grp["hooks"][0]
    assert h["command"] == '"$PLUGIN_ROOT/hooks/guard.sh"'
    assert h["timeout"] == 10
    assert h["statusMessage"] == "checking"


def test_codex_postedit_maps_to_posttooluse():
    out = gen.build_codex(
        {
            "postedit": [
                {
                    "script": "lint.sh",
                    "timeout": 60,
                    "name": "lint",
                    "status_message": "linting",
                }
            ]
        }
    )
    grp = out["hooks"]["PostToolUse"][0]
    assert grp["matcher"] == "^apply_patch$"


def test_codex_no_status_message_omitted():
    out = gen.build_codex({"prebash": [{"script": "g.sh", "timeout": 5, "name": "g"}]})
    h = out["hooks"]["PreToolUse"][0]["hooks"][0]
    assert "statusMessage" not in h


def test_codex_sessionstart_no_matcher():
    out = gen.build_codex(
        {
            "sessionstart": [
                {
                    "script": "s.sh",
                    "timeout": 5,
                    "name": "s",
                    "status_message": "starting",
                }
            ]
        }
    )
    grp = out["hooks"]["SessionStart"][0]
    assert "matcher" not in grp


def test_codex_timeout_kept_in_seconds():
    out = gen.build_codex({"sessionstart": [{"script": "s.sh", "timeout": 7}]})
    h = out["hooks"]["SessionStart"][0]["hooks"][0]
    assert h["timeout"] == 7


def test_codex_userpromptsubmit_skipped():
    out = gen.build_codex({"userpromptsubmit": [{"script": "u.sh", "timeout": 5}]})
    assert out["hooks"] == {}


# --- JSON serialization ---


def test_json_output_ends_with_newline():
    data = gen._to_bytes({"hooks": {}})
    assert data.endswith(b"\n")


def test_json_output_is_valid():
    data = gen._to_bytes({"hooks": {"SessionStart": []}})
    parsed = json.loads(data)
    assert "hooks" in parsed


# --- byte-equality with existing configs ---


def test_byte_equal_codex_hooks_json():
    """Generator must reproduce dev-workflow's codex.hooks.json byte-for-byte."""
    desired = gen.compute_desired()
    root = Path(__file__).resolve().parent.parent
    codex_path = root / "plugins" / "dev-workflow" / "hooks" / "codex.hooks.json"
    assert codex_path in desired, "Codex hooks.json missing from desired state"
    assert desired[codex_path] == codex_path.read_bytes(), (
        "Generated codex.hooks.json differs from on-disk file"
    )
