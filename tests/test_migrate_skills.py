"""Unit tests for `scripts.build.migrate_skills` helper functions.

The migration script is one-shot — we don't need to exercise the full plugin
import path here. The contracts that matter are:

- frontmatter splitter routes CC-only keys to the claude overlay and keeps the
  cross-target keys on the base
- the sibling `.md` discovery picks up non-SKILL markdown next to SKILL.md
- the link rewriter only retargets bare basenames, never absolute or
  already-prefixed paths
- writing the same content twice is a no-op (idempotent)
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def ms(load_script):
    return load_script("build/migrate_skills.py")


def test_split_frontmatter_keeps_name_and_description_on_base(ms) -> None:
    base, claude = ms._split_frontmatter(
        {
            "name": "writing-go",
            "description": "Go dev",
            "allowed-tools": ["Read", "Bash"],
            "context": "fork",
            "agent": "go-engineer",
        }
    )
    assert base == {"name": "writing-go", "description": "Go dev"}
    assert claude == {
        "allowed-tools": ["Read", "Bash"],
        "context": "fork",
        "agent": "go-engineer",
    }


def test_split_frontmatter_passes_through_targets(ms) -> None:
    base, claude = ms._split_frontmatter(
        {
            "name": "x",
            "description": "y",
            "targets": ["claude"],
            "user-invocable": True,
        }
    )
    assert base == {"name": "x", "description": "y", "targets": ["claude"]}
    assert claude == {"user-invocable": True}


def test_discover_md_siblings_excludes_skill_files(ms, tmp_path: Path) -> None:
    (tmp_path / "SKILL.md").write_text("base")
    (tmp_path / "SKILL.codex.md").write_text("codex")
    (tmp_path / "SKILL.pi.md").write_text("pi")
    (tmp_path / "PATTERNS.md").write_text("p")
    (tmp_path / "CLI.md").write_text("c")
    (tmp_path / "config.yaml").write_text("ignored")
    siblings = ms._discover_md_siblings(tmp_path)
    assert [p.name for p in siblings] == ["CLI.md", "PATTERNS.md"]


def test_rewrite_sibling_links_only_retargets_bare_basenames(ms) -> None:
    body = (
        "See [Patterns](PATTERNS.md) and [Testing](TESTING.md).\n"
        "Already prefixed: [other](references/PATTERNS.md).\n"
        "Relative path: [rel](./PATTERNS.md).\n"
        "External: [ext](https://example.com/PATTERNS.md).\n"
    )
    rewritten = ms._rewrite_sibling_links(body, ["PATTERNS.md", "TESTING.md"])
    assert "[Patterns](references/PATTERNS.md)" in rewritten
    assert "[Testing](references/TESTING.md)" in rewritten
    # Already-prefixed link is preserved (one occurrence only, not doubly-prefixed)
    assert rewritten.count("references/PATTERNS.md") == 2
    assert "./PATTERNS.md" in rewritten
    assert "https://example.com/PATTERNS.md" in rewritten


def test_write_text_if_changed_is_idempotent(ms, tmp_path: Path) -> None:
    target = tmp_path / "out" / "file.md"
    assert ms._write_text_if_changed(target, "hello\n") is True
    assert ms._write_text_if_changed(target, "hello\n") is False
    assert ms._write_text_if_changed(target, "different\n") is True


def test_copy_support_tree_preserves_executable_bit(ms, tmp_path: Path) -> None:
    src = tmp_path / "src" / "scripts"
    dst = tmp_path / "dst" / "scripts"
    src.mkdir(parents=True)
    script = src / "run.sh"
    script.write_text("#!/bin/sh\necho hi\n")
    script.chmod(0o755)

    n = ms._copy_support_tree(src, dst)
    assert n == 1
    out = dst / "run.sh"
    assert out.is_file()
    assert out.stat().st_mode & 0o111
