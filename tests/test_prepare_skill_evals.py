from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

import pytest

_spec = importlib.util.spec_from_file_location(
    "prepare_skill_evals",
    Path(__file__).resolve().parent.parent / "scripts" / "prepare-skill-evals.py",
)
assert _spec is not None and _spec.loader is not None
prepare_skill_evals = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(prepare_skill_evals)


def _write_skill(
    root: Path, plugin: str, source_dir: str, skill: str, body: str
) -> None:
    skill_dir = root / "plugins" / plugin / source_dir / skill
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")


def _write_eval(root: Path, plugin: str, skill: str, count: int = 2) -> None:
    eval_dir = root / "tests" / "skill-evals" / plugin / skill / "evals"
    eval_dir.mkdir(parents=True)
    evals = [
        {
            "id": f"case-{index}",
            "name": f"case {index}",
            "prompt": "describe the workflow",
            "assertions": ["mentions verification", "uses the skill"],
        }
        for index in range(count)
    ]
    (eval_dir / "evals.json").write_text(
        json.dumps({"skill_name": skill, "evals": evals}),
        encoding="utf-8",
    )


def _patch_roots(tmp_path: Path):
    return (
        patch.object(prepare_skill_evals, "ROOT", tmp_path),
        patch.object(prepare_skill_evals, "PLUGINS_DIR", tmp_path / "plugins"),
        patch.object(
            prepare_skill_evals, "EVALS_DIR", tmp_path / "tests" / "skill-evals"
        ),
    )


def test_prepare_copies_source_skill_and_evals(tmp_path):
    _write_skill(tmp_path, "dev-tools", "skills", "using-modern-cli", "source skill")
    _write_eval(tmp_path, "dev-tools", "using-modern-cli")
    out = tmp_path.parent / "skill-eval-out-source"

    root_patch, plugins_patch, evals_patch = _patch_roots(tmp_path)
    with root_patch, plugins_patch, evals_patch:
        skills, evals = prepare_skill_evals.prepare(out, "skills")

    assert (skills, evals) == (1, 2)
    dest = out / "dev-tools" / "skills" / "using-modern-cli"
    assert (dest / "SKILL.md").read_text(encoding="utf-8") == "source skill"
    assert (dest / "evals" / "evals.json").is_file()


def test_prepare_can_copy_codex_overlay_while_preserving_eval_layout(tmp_path):
    _write_skill(tmp_path, "dev-tools", "skills", "using-modern-cli", "source skill")
    _write_skill(
        tmp_path,
        "dev-tools",
        "skills-codex",
        "using-modern-cli",
        "codex overlay",
    )
    _write_eval(tmp_path, "dev-tools", "using-modern-cli", count=1)
    out = tmp_path.parent / "skill-eval-out-codex"

    root_patch, plugins_patch, evals_patch = _patch_roots(tmp_path)
    with root_patch, plugins_patch, evals_patch:
        skills, evals = prepare_skill_evals.prepare(out, "skills-codex")

    assert (skills, evals) == (1, 1)
    dest = out / "dev-tools" / "skills" / "using-modern-cli" / "SKILL.md"
    assert dest.read_text(encoding="utf-8") == "codex overlay"


def test_prepare_rejects_repo_output(tmp_path):
    with patch.object(prepare_skill_evals, "ROOT", tmp_path):
        with pytest.raises(
            prepare_skill_evals.EvalPrepError, match="inside the repository"
        ):
            prepare_skill_evals.prepare(tmp_path / "nested", "skills")


def test_prepare_rejects_unknown_source_dir(tmp_path):
    with pytest.raises(prepare_skill_evals.EvalPrepError, match="source directory"):
        prepare_skill_evals.prepare(tmp_path.parent / "out", "flat")
