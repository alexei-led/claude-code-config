from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "scripts" / "install-pi-exports.sh"
SKILLS_SRC = ROOT / "flat" / "skills-pi"
AGENTS_SRC = ROOT / "flat" / "agents-pi"


def _run(script_args: list[str], target_dir: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PI_CODING_AGENT_DIR"] = str(target_dir)
    return subprocess.run(
        ["bash", str(SCRIPT), *script_args],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _require_flat_artifacts() -> None:
    if not SKILLS_SRC.is_dir() or not AGENTS_SRC.is_dir():
        pytest.skip("flat/skills-pi or flat/agents-pi missing; run `make build` first")


def test_dry_run_reports_intended_symlinks(tmp_path: Path) -> None:
    _require_flat_artifacts()
    target = tmp_path / "pi-agent"
    result = _run(["--target-dir", str(target)], target)
    assert result.returncode == 0, result.stderr
    assert "DRY-RUN" in result.stdout
    assert str(SKILLS_SRC) in result.stdout
    assert str(AGENTS_SRC) in result.stdout
    assert not target.exists(), "dry-run must not create the target dir"


def test_apply_creates_resolving_symlinks(tmp_path: Path) -> None:
    _require_flat_artifacts()
    target = tmp_path / "pi-agent"
    result = _run(["--apply", "--target-dir", str(target)], target)
    assert result.returncode == 0, result.stderr

    skills_link = target / "skills"
    agents_link = target / "agents"
    assert skills_link.is_symlink()
    assert agents_link.is_symlink()
    assert skills_link.resolve() == SKILLS_SRC.resolve()
    assert agents_link.resolve() == AGENTS_SRC.resolve()

    skill_md = skills_link / "context7-cli" / "SKILL.md"
    assert skill_md.is_file(), "known Pi skill must be reachable through symlink"
    assert "name: context7-cli" in skill_md.read_text()


def test_apply_backs_up_existing_target(tmp_path: Path) -> None:
    """Stale link or directory at target/skills is moved to a timestamped backup."""
    _require_flat_artifacts()
    target = tmp_path / "pi-agent"
    target.mkdir()
    stale = target / "skills"
    stale.mkdir()
    (stale / "marker.txt").write_text("stale skill content")

    result = _run(["--apply", "--target-dir", str(target)], target)
    assert result.returncode == 0, result.stderr

    backups = sorted(target.glob("skills.backup.*"))
    assert backups, f"existing target must be backed up: {result.stdout}"
    assert (backups[0] / "marker.txt").read_text() == "stale skill content"
    assert (target / "skills").is_symlink()
    assert (target / "skills").resolve() == SKILLS_SRC.resolve()


def test_idempotent_apply_is_noop_when_links_correct(tmp_path: Path) -> None:
    _require_flat_artifacts()
    target = tmp_path / "pi-agent"
    first = _run(["--apply", "--target-dir", str(target)], target)
    assert first.returncode == 0, first.stderr

    second = _run(["--apply", "--target-dir", str(target)], target)
    assert second.returncode == 0, second.stderr
    assert "OK:" in second.stdout
    backups = sorted(target.glob("skills.backup.*"))
    assert not backups, "no backup should be created when symlinks already match"


def test_unknown_target_dir_is_created(tmp_path: Path) -> None:
    _require_flat_artifacts()
    target = tmp_path / "deep" / "nested" / "pi-agent"
    result = _run(["--apply", "--target-dir", str(target)], target)
    assert result.returncode == 0, result.stderr
    assert (target / "skills").is_symlink()
    shutil.rmtree(target.parent.parent)
