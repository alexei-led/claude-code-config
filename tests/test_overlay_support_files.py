"""Tests for `scripts.build.overlay.apply_support_files`."""

from __future__ import annotations

import os
import stat
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def ov(load_script):
    return load_script("build/overlay.py")


def _write(path: Path, content: str, *, mode: int | None = None) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    if mode is not None:
        path.chmod(mode)
    return path


def test_no_support_dirs_yields_no_output(ov, tmp_path: Path) -> None:
    base = tmp_path / "skill"
    base.mkdir()
    out = tmp_path / "out"
    written = ov.apply_support_files(base, "claude", out)
    assert written == []
    assert not out.exists() or not any(out.rglob("*"))


def test_copies_base_scripts_references_assets(ov, tmp_path: Path) -> None:
    base = tmp_path / "skill"
    _write(base / "scripts" / "run.sh", "#!/bin/sh\necho hi\n")
    _write(base / "references" / "doc.md", "ref\n")
    _write(base / "assets" / "img.txt", "asset\n")

    out = tmp_path / "out"
    ov.apply_support_files(base, "claude", out)

    assert (out / "scripts" / "run.sh").read_text() == "#!/bin/sh\necho hi\n"
    assert (out / "references" / "doc.md").read_text() == "ref\n"
    assert (out / "assets" / "img.txt").read_text() == "asset\n"


def test_overlay_adds_new_file(ov, tmp_path: Path) -> None:
    base = tmp_path / "skill"
    _write(base / "scripts" / "base.sh", "base\n")
    _write(base / "claude" / "scripts" / "claude-only.sh", "claude\n")

    out = tmp_path / "out"
    ov.apply_support_files(base, "claude", out)

    assert (out / "scripts" / "base.sh").read_text() == "base\n"
    assert (out / "scripts" / "claude-only.sh").read_text() == "claude\n"


def test_overlay_replaces_same_path(ov, tmp_path: Path) -> None:
    base = tmp_path / "skill"
    _write(base / "scripts" / "run.sh", "base impl\n")
    _write(base / "pi" / "scripts" / "run.sh", "pi impl\n")

    out = tmp_path / "out"
    ov.apply_support_files(base, "pi", out)

    assert (out / "scripts" / "run.sh").read_text() == "pi impl\n"


def test_overlay_for_different_target_ignored(ov, tmp_path: Path) -> None:
    base = tmp_path / "skill"
    _write(base / "scripts" / "run.sh", "base\n")
    _write(base / "pi" / "scripts" / "run.sh", "pi only\n")

    out = tmp_path / "out"
    ov.apply_support_files(base, "claude", out)

    assert (out / "scripts" / "run.sh").read_text() == "base\n"


def test_executable_bit_preserved_from_base(ov, tmp_path: Path) -> None:
    base = tmp_path / "skill"
    src = _write(base / "scripts" / "run.sh", "#!/bin/sh\n", mode=0o755)
    assert src.stat().st_mode & stat.S_IXUSR

    out = tmp_path / "out"
    ov.apply_support_files(base, "claude", out)

    assert out.joinpath("scripts", "run.sh").stat().st_mode & stat.S_IXUSR


def test_executable_bit_preserved_from_overlay(ov, tmp_path: Path) -> None:
    base = tmp_path / "skill"
    _write(base / "scripts" / "run.sh", "base\n", mode=0o644)
    _write(base / "codex" / "scripts" / "run.sh", "#!/bin/sh\n", mode=0o755)

    out = tmp_path / "out"
    ov.apply_support_files(base, "codex", out)

    dst = out / "scripts" / "run.sh"
    assert dst.read_text() == "#!/bin/sh\n"
    assert dst.stat().st_mode & stat.S_IXUSR


def test_nested_subdirectories_preserved(ov, tmp_path: Path) -> None:
    base = tmp_path / "skill"
    _write(base / "references" / "guides" / "intro.md", "g\n")
    _write(base / "gemini" / "references" / "guides" / "extra.md", "x\n")

    out = tmp_path / "out"
    ov.apply_support_files(base, "gemini", out)

    assert (out / "references" / "guides" / "intro.md").read_text() == "g\n"
    assert (out / "references" / "guides" / "extra.md").read_text() == "x\n"


def test_overlay_only_no_base(ov, tmp_path: Path) -> None:
    base = tmp_path / "skill"
    _write(base / "pi" / "scripts" / "pi-helper.sh", "pi\n")

    out = tmp_path / "out"
    ov.apply_support_files(base, "pi", out)

    assert (out / "scripts" / "pi-helper.sh").read_text() == "pi\n"


def test_symlinks_in_source_are_skipped(ov, tmp_path: Path) -> None:
    base = tmp_path / "skill"
    real = _write(base / "scripts" / "real.sh", "real\n")
    link = base / "scripts" / "link.sh"
    link.symlink_to(real)

    out = tmp_path / "out"
    ov.apply_support_files(base, "claude", out)

    assert (out / "scripts" / "real.sh").exists()
    assert not (out / "scripts" / "link.sh").exists()


def test_returns_list_of_written_paths(ov, tmp_path: Path) -> None:
    base = tmp_path / "skill"
    _write(base / "scripts" / "a.sh", "a\n")
    _write(base / "claude" / "scripts" / "b.sh", "b\n")

    out = tmp_path / "out"
    written = ov.apply_support_files(base, "claude", out)

    rel = {p.relative_to(out).as_posix() for p in written}
    assert rel == {"scripts/a.sh", "scripts/b.sh"}


def test_idempotent_when_run_twice(ov, tmp_path: Path) -> None:
    base = tmp_path / "skill"
    _write(base / "scripts" / "run.sh", "v1\n")

    out = tmp_path / "out"
    ov.apply_support_files(base, "claude", out)
    # mutate output; second run should restore from base.
    (out / "scripts" / "run.sh").write_text("tampered\n")
    ov.apply_support_files(base, "claude", out)

    assert (out / "scripts" / "run.sh").read_text() == "v1\n"


def test_no_deletion_when_overlay_omits_base_file(ov, tmp_path: Path) -> None:
    """Overlay-only-adds: omitting a file in the overlay does not remove it."""
    base = tmp_path / "skill"
    _write(base / "scripts" / "keep.sh", "keep\n")
    # overlay omits keep.sh entirely
    _write(base / "pi" / "scripts" / "extra.sh", "extra\n")

    out = tmp_path / "out"
    ov.apply_support_files(base, "pi", out)

    assert (out / "scripts" / "keep.sh").exists()
    assert (out / "scripts" / "extra.sh").exists()


def test_overwrites_into_existing_output_dir(ov, tmp_path: Path) -> None:
    """Output directory already populated by a prior pipeline step is fine."""
    base = tmp_path / "skill"
    _write(base / "scripts" / "run.sh", "v2\n")
    out = tmp_path / "out"
    _write(out / "SKILL.md", "preexisting body\n")

    ov.apply_support_files(base, "claude", out)

    assert (out / "SKILL.md").read_text() == "preexisting body\n"
    assert (out / "scripts" / "run.sh").read_text() == "v2\n"


def test_umask_does_not_strip_executable_bit(ov, tmp_path: Path) -> None:
    """copystat must restore the executable bit even under a restrictive umask."""
    original = os.umask(0o077)
    try:
        base = tmp_path / "skill"
        _write(base / "scripts" / "run.sh", "#!/bin/sh\n", mode=0o755)
        out = tmp_path / "out"
        ov.apply_support_files(base, "claude", out)
        mode = (out / "scripts" / "run.sh").stat().st_mode
        assert mode & stat.S_IXUSR
    finally:
        os.umask(original)
