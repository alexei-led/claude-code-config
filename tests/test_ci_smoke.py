"""CI smoke test: a fresh compile produces the same dist/ as the committed one.

This is the local stand-in for the CI drift check (`make check`): we invoke the
compiler in-process and confirm the build is deterministic — running it twice
yields identical file content. That's the same property `git diff --exit-code`
proves on CI, but it works inside pytest without depending on a clean tree.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest
from conftest import REPO_ROOT as _REPO_ROOT


def _hash_tree(root: Path) -> dict[str, str]:
    digests: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        rel = str(path.relative_to(root))
        digests[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return digests


@pytest.fixture(scope="module")
def compile_mod(load_script):
    return load_script("build/compile.py")


def test_main_dry_run_succeeds(compile_mod):
    assert compile_mod.main(["--dry-run"]) == 0


def test_build_is_idempotent(compile_mod):
    dist = _REPO_ROOT / "dist"
    if not dist.is_dir():
        pytest.skip("dist/ not present; run `make build` first")

    before = _hash_tree(dist)
    assert compile_mod.main([]) == 0
    after = _hash_tree(dist)

    changed = sorted(p for p, h in after.items() if before.get(p) != h)
    added = sorted(p for p in after if p not in before)
    removed = sorted(p for p in before if p not in after)

    assert not changed, f"rebuild mutated existing files: {changed[:5]}"
    assert not added, f"rebuild produced new files: {added[:5]}"
    assert not removed, f"rebuild removed files: {removed[:5]}"
