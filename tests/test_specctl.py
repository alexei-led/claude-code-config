"""Smoke tests for specctl CLI."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from conftest import REPO_ROOT

SPECCTL = REPO_ROOT / "src" / "skills" / "spec-core" / "scripts" / "specctl.py"


def run_specctl(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(SPECCTL), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=10,
    )


@pytest.fixture()
def empty_spec(tmp_path: Path) -> Path:
    """A minimal .spec/ project with no tasks."""
    for sub in ("tasks", "reqs", "epics", "memory"):
        (tmp_path / ".spec" / sub).mkdir(parents=True)
    return tmp_path


# ---------------------------------------------------------------------------
# Help flags
# ---------------------------------------------------------------------------


def test_help_exits_zero():
    result = run_specctl("--help")
    assert result.returncode == 0
    assert "specctl" in result.stdout.lower()


@pytest.mark.parametrize("cmd", ["status", "ready"])
def test_subcommand_help_exits_zero(cmd: str):
    result = run_specctl(cmd, "--help")
    assert result.returncode == 0


# ---------------------------------------------------------------------------
# No .spec/ directory — commands must fail gracefully
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cmd", ["status", "ready", "validate"])
def test_fails_without_spec_dir(cmd: str, tmp_path: Path):
    result = run_specctl(cmd, cwd=str(tmp_path))
    assert result.returncode != 0


# ---------------------------------------------------------------------------
# --json flags accepted by argparse (argparse errors, not domain errors)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cmd", ["status", "ready"])
def test_json_flag_accepted(cmd: str, tmp_path: Path):
    result = run_specctl(cmd, "--json", cwd=str(tmp_path))
    assert "unrecognized arguments" not in result.stderr


# ---------------------------------------------------------------------------
# Empty project
# ---------------------------------------------------------------------------


def test_status_empty_project(empty_spec: Path):
    result = run_specctl("status", cwd=str(empty_spec))
    assert result.returncode == 0


def test_status_json_empty(empty_spec: Path):
    result = run_specctl("status", "--json", cwd=str(empty_spec))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["total"] == 0
    assert data["done"] == 0


def test_ready_empty(empty_spec: Path):
    result = run_specctl("ready", cwd=str(empty_spec))
    assert result.returncode == 0


def test_ready_json_empty(empty_spec: Path):
    result = run_specctl("ready", "--json", cwd=str(empty_spec))
    assert result.returncode == 0
    assert json.loads(result.stdout) == []


def test_validate_empty(empty_spec: Path):
    result = run_specctl("validate", cwd=str(empty_spec))
    assert result.returncode == 0


# ---------------------------------------------------------------------------
# Project with tasks
# ---------------------------------------------------------------------------


def test_status_counts_task(empty_spec: Path):
    (empty_spec / ".spec" / "tasks" / "TASK-smoke.md").write_text(
        "---\nid: TASK-smoke\nstatus: todo\npriority: high\n---\n# Smoke\n"
    )
    result = run_specctl("status", "--json", cwd=str(empty_spec))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert data["total"] == 1
    assert data["todo"] == 1


def test_ready_returns_unblocked_task(empty_spec: Path):
    (empty_spec / ".spec" / "tasks" / "TASK-ready.md").write_text(
        "---\nid: TASK-ready\nstatus: todo\npriority: normal\n---\n# Ready\n"
    )
    result = run_specctl("ready", "--json", cwd=str(empty_spec))
    assert result.returncode == 0
    data = json.loads(result.stdout)
    assert len(data) == 1
    assert data[0]["id"] == "TASK-ready"
