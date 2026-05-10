from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path
from unittest.mock import patch

_spec = importlib.util.spec_from_file_location(
    "generate_skills",
    Path(__file__).resolve().parent.parent / "scripts" / "generate-skills.py",
)
assert _spec is not None and _spec.loader is not None
generate_skills = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = generate_skills
_spec.loader.exec_module(generate_skills)


def _write_skill(
    root: Path,
    plugin: str,
    skill: str,
    file_name: str,
    body: str,
) -> Path:
    skill_dir = root / "plugins" / plugin / "skills" / skill
    skill_dir.mkdir(parents=True, exist_ok=True)
    path = skill_dir / file_name
    path.write_text(body)
    return path


def _write_pi_preamble(root: Path, body: str = "<!-- pi preamble -->") -> None:
    preamble = root / "scripts" / "preambles" / "pi.md"
    preamble.parent.mkdir(parents=True)
    preamble.write_text(body)


def test_pi_overlay_prefers_pi_then_codex_then_source(tmp_path):
    _write_pi_preamble(tmp_path)
    _write_skill(
        tmp_path,
        "demo",
        "docs",
        "SKILL.md",
        "---\nname: docs\ndescription: Source\n---\nsource body\n",
    )
    _write_skill(
        tmp_path,
        "demo",
        "docs",
        "SKILL.codex.md",
        "---\nname: docs\ndescription: Codex\n---\ncodex body\n",
    )
    _write_skill(
        tmp_path,
        "demo",
        "docs",
        "SKILL.pi.md",
        "---\nname: docs\ndescription: Pi\nallowed-tools: [Read]\n---\npi body\n",
    )

    with patch.object(generate_skills, "ROOT", tmp_path):
        desired = generate_skills.compute_desired_state("pi")

    out = tmp_path / "plugins" / "demo" / "skills-pi" / "docs" / "SKILL.md"
    content = desired[out].data.decode()
    assert "<!-- pi preamble -->" in content
    assert "description: Pi" in content
    assert "pi body" in content
    assert "codex body" not in content
    assert "source body" not in content
    assert "allowed-tools" not in content


def test_pi_overlay_uses_codex_overlay_when_pi_overlay_is_missing(tmp_path):
    _write_pi_preamble(tmp_path)
    _write_skill(
        tmp_path,
        "demo",
        "docs",
        "SKILL.md",
        "---\nname: docs\ndescription: Source\n---\nsource body\n",
    )
    _write_skill(
        tmp_path,
        "demo",
        "docs",
        "SKILL.codex.md",
        "---\nname: docs\ndescription: Codex\n---\ncodex body\n",
    )

    with patch.object(generate_skills, "ROOT", tmp_path):
        desired = generate_skills.compute_desired_state("pi")

    out = tmp_path / "plugins" / "demo" / "skills-pi" / "docs" / "SKILL.md"
    content = desired[out].data.decode()
    assert "description: Codex" in content
    assert "codex body" in content
    assert "source body" not in content


def test_pi_transform_strips_frontmatter_and_cc_only_blocks(tmp_path):
    _write_pi_preamble(tmp_path, "<!-- pi tools -->")
    _write_skill(
        tmp_path,
        "demo",
        "review",
        "SKILL.md",
        "---\n"
        "name: review\n"
        "description: Review code\n"
        "allowed-tools: [Read, Task]\n"
        "model: opus\n"
        "argument-hint: files\n"
        "---\n"
        "keep this\n"
        "<!-- CC-ONLY: begin -->\n"
        "remove this\n"
        "<!-- CC-ONLY: end -->\n",
    )

    with patch.object(generate_skills, "ROOT", tmp_path):
        desired = generate_skills.compute_desired_state("pi")

    out = tmp_path / "plugins" / "demo" / "skills-pi" / "review" / "SKILL.md"
    content = desired[out].data.decode()
    assert "<!-- pi tools -->" in content
    assert "name: review" in content
    assert "description: Review code" in content
    assert "allowed-tools" not in content
    assert "model:" not in content
    assert "argument-hint" not in content
    assert "keep this" in content
    assert "remove this" not in content


def test_pi_support_files_are_copied_with_executable_bits(tmp_path):
    _write_pi_preamble(tmp_path)
    _write_skill(
        tmp_path,
        "demo",
        "runner",
        "SKILL.md",
        "---\nname: runner\ndescription: Runner\n---\nbody\n",
    )
    skill_dir = tmp_path / "plugins" / "demo" / "skills" / "runner"
    script = skill_dir / "scripts" / "run.sh"
    script.parent.mkdir()
    script.write_text("#!/bin/sh\n")
    script.chmod(0o755)
    (skill_dir / "references").mkdir()
    (skill_dir / "references" / "docs.md").write_text("docs\n")
    (skill_dir / "NOTES.md").write_text("notes\n")
    (skill_dir / "evals").mkdir()
    (skill_dir / "evals" / "fixture.md").write_text("fixture\n")
    (skill_dir / "scratch.tmp").write_text("tmp\n")

    with patch.object(generate_skills, "ROOT", tmp_path):
        desired = generate_skills.compute_desired_state("pi")

    out_dir = tmp_path / "plugins" / "demo" / "skills-pi" / "runner"
    assert desired[out_dir / "scripts" / "run.sh"].mode == 0o755
    assert desired[out_dir / "scripts" / "run.sh"].data == b"#!/bin/sh\n"
    assert out_dir / "references" / "docs.md" in desired
    assert out_dir / "NOTES.md" in desired
    assert out_dir / "evals" / "fixture.md" not in desired
    assert out_dir / "scratch.tmp" not in desired


def test_sync_removes_stale_pi_overlay_files(tmp_path):
    _write_pi_preamble(tmp_path)
    _write_skill(
        tmp_path,
        "demo",
        "runner",
        "SKILL.md",
        "---\nname: runner\ndescription: Runner\n---\nbody\n",
    )
    stale_file = tmp_path / "plugins" / "demo" / "skills-pi" / "old" / "SKILL.md"
    stale_file.parent.mkdir(parents=True)
    stale_file.write_text("stale\n")

    with patch.object(generate_skills, "ROOT", tmp_path):
        desired = generate_skills.compute_desired_state("pi")
        changes = generate_skills.sync("pi", desired)

    out_file = tmp_path / "plugins" / "demo" / "skills-pi" / "runner" / "SKILL.md"
    assert changes > 0
    assert out_file.is_file()
    assert not stale_file.exists()
    assert not stale_file.parent.exists()


def test_sync_preserves_support_executable_mode(tmp_path):
    _write_pi_preamble(tmp_path)
    _write_skill(
        tmp_path,
        "demo",
        "runner",
        "SKILL.md",
        "---\nname: runner\ndescription: Runner\n---\nbody\n",
    )
    script = tmp_path / "plugins" / "demo" / "skills" / "runner" / "scripts" / "run.sh"
    script.parent.mkdir()
    script.write_text("#!/bin/sh\n")
    script.chmod(0o755)

    with patch.object(generate_skills, "ROOT", tmp_path):
        desired = generate_skills.compute_desired_state("pi")
        generate_skills.sync("pi", desired)

    out_script = (
        tmp_path / "plugins" / "demo" / "skills-pi" / "runner" / "scripts" / "run.sh"
    )
    assert out_script.is_file()
    assert os.access(out_script, os.X_OK)
    assert (out_script.stat().st_mode & 0o777) == 0o755
