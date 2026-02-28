"""Smoke tests for specctl CLI."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path

import pytest

SPECCTL = Path(__file__).resolve().parent.parent / "scripts" / "specctl.py"


def run_specctl(*args: str, cwd: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(SPECCTL), *args],
        capture_output=True,
        text=True,
        cwd=cwd,
        timeout=10,
    )


class TestHelp:
    def test_help_exits_zero(self):
        result = run_specctl("--help")
        assert result.returncode == 0
        assert "specctl" in result.stdout.lower()

    def test_status_help(self):
        result = run_specctl("status", "--help")
        assert result.returncode == 0

    def test_ready_help(self):
        result = run_specctl("ready", "--help")
        assert result.returncode == 0


class TestNoSpecDir:
    """Commands should fail gracefully outside a .spec/ project."""

    def test_status_no_spec(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_specctl("status", cwd=tmp)
            assert result.returncode != 0

    def test_ready_no_spec(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_specctl("ready", cwd=tmp)
            assert result.returncode != 0

    def test_validate_no_spec(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_specctl("validate", cwd=tmp)
            assert result.returncode != 0


class TestJsonFlags:
    """Verify --json flags are accepted by argparse."""

    def test_status_json_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_specctl("status", "--json", cwd=tmp)
            # Should fail (no .spec/) but NOT with argparse error
            assert "unrecognized arguments" not in result.stderr

    def test_ready_json_flag(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = run_specctl("ready", "--json", cwd=tmp)
            assert "unrecognized arguments" not in result.stderr


class TestWithSpecDir:
    """Tests that create a minimal .spec/ directory."""

    @pytest.fixture()
    def spec_dir(self, tmp_path):
        (tmp_path / ".spec" / "tasks").mkdir(parents=True)
        (tmp_path / ".spec" / "reqs").mkdir(parents=True)
        (tmp_path / ".spec" / "epics").mkdir(parents=True)
        (tmp_path / ".spec" / "memory").mkdir(parents=True)
        return tmp_path

    def test_status_empty_project(self, spec_dir):
        result = run_specctl("status", cwd=str(spec_dir))
        assert result.returncode == 0

    def test_status_json_empty(self, spec_dir):
        result = run_specctl("status", "--json", cwd=str(spec_dir))
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["total"] == 0
        assert data["done"] == 0

    def test_ready_empty(self, spec_dir):
        result = run_specctl("ready", cwd=str(spec_dir))
        assert result.returncode == 0

    def test_ready_json_empty(self, spec_dir):
        result = run_specctl("ready", "--json", cwd=str(spec_dir))
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data == []

    def test_validate_empty(self, spec_dir):
        result = run_specctl("validate", cwd=str(spec_dir))
        assert result.returncode == 0

    def test_with_task(self, spec_dir):
        task = spec_dir / ".spec" / "tasks" / "TASK-test-smoke.md"
        task.write_text(
            "---\n"
            "id: TASK-test-smoke\n"
            "status: todo\n"
            "priority: high\n"
            "---\n"
            "# Smoke test task\n"
            "\nA task for testing.\n"
        )
        result = run_specctl("status", "--json", cwd=str(spec_dir))
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["total"] == 1
        assert data["todo"] == 1

    def test_ready_with_task(self, spec_dir):
        task = spec_dir / ".spec" / "tasks" / "TASK-ready-test.md"
        task.write_text(
            "---\n"
            "id: TASK-ready-test\n"
            "status: todo\n"
            "priority: normal\n"
            "---\n"
            "# Ready test task\n"
        )
        result = run_specctl("ready", "--json", cwd=str(spec_dir))
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["id"] == "TASK-ready-test"
