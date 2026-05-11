"""Tests for the Pi-extension compiler.

Pi extensions are copied verbatim from src/pi-extensions/ to
dist/pi/extensions/, preserving both single-file and directory layouts
that Pi's discovery accepts.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def cpe(load_script):
    load_script("build/compile.py")  # populate _compile.OUTPUT
    return load_script("build/compile_pi_extension.py")


def test_discover_returns_empty_when_dir_missing(cpe, tmp_path: Path) -> None:
    assert cpe.discover_pi_extensions(tmp_path) == []


def test_discover_lists_files_and_dirs_sorted(cpe, tmp_path: Path) -> None:
    ext = tmp_path / "src" / "pi-extensions"
    ext.mkdir(parents=True)
    (ext / "zeta.ts").write_text("// zeta\n")
    (ext / "alpha").mkdir()
    (ext / "alpha" / "index.ts").write_text("// alpha\n")
    (ext / ".DS_Store").write_text("hidden")

    entries = cpe.discover_pi_extensions(tmp_path)
    names = [p.name for p in entries]
    assert names == ["alpha", "zeta.ts"]


def test_compile_copies_single_file_extension(cpe, tmp_path: Path) -> None:
    ext = tmp_path / "src" / "pi-extensions"
    ext.mkdir(parents=True)
    (ext / "todo.ts").write_text("export const t = 1;\n")

    written = cpe.compile_pi_extensions(tmp_path)
    assert len(written) == 1
    dest = tmp_path / "dist" / "pi" / "extensions" / "todo.ts"
    assert dest.is_file()
    assert dest.read_text() == "export const t = 1;\n"


def test_compile_copies_directory_extension(cpe, tmp_path: Path) -> None:
    ext = tmp_path / "src" / "pi-extensions"
    sub = ext / "plan-mode"
    sub.mkdir(parents=True)
    (sub / "index.ts").write_text("export const m = 1;\n")
    (sub / "utils.ts").write_text("export const u = 2;\n")

    cpe.compile_pi_extensions(tmp_path)
    dest = tmp_path / "dist" / "pi" / "extensions" / "plan-mode"
    assert (dest / "index.ts").read_text() == "export const m = 1;\n"
    assert (dest / "utils.ts").read_text() == "export const u = 2;\n"


def test_compile_skips_when_source_absent(cpe, tmp_path: Path) -> None:
    written = cpe.compile_pi_extensions(tmp_path)
    assert written == []


def test_compile_is_idempotent(cpe, tmp_path: Path) -> None:
    ext = tmp_path / "src" / "pi-extensions"
    ext.mkdir(parents=True)
    (ext / "todo.ts").write_text("export const t = 1;\n")

    cpe.compile_pi_extensions(tmp_path)
    cpe.compile_pi_extensions(tmp_path)
    dest = tmp_path / "dist" / "pi" / "extensions" / "todo.ts"
    assert dest.read_text() == "export const t = 1;\n"
