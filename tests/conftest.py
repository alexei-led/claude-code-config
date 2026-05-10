"""Shared pytest fixtures.

`load_script` replaces ad-hoc importlib boilerplate that each test file used to
inline. Scripts in `scripts/` are kebab-cased CLI files; this fixture loads them
as importable modules using the kebab-to-snake convention (e.g.
`generate-skills.py` becomes module name `generate_skills`).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent
_SCRIPTS = _REPO_ROOT / "scripts"

# scripts/_common.py is imported via `from _common import ...` inside the
# generators; tests that load those generators need scripts/ on sys.path.
sys.path.insert(0, str(_SCRIPTS))


def _resolve(rel_or_name: str) -> Path:
    """Locate a script by relative path under scripts/, or by basename
    (searches scripts/build/, scripts/validate/, scripts/evals/, scripts/release/).
    """
    direct = _SCRIPTS / rel_or_name
    if direct.is_file():
        return direct
    for sub in ("build", "validate", "evals", "release"):
        candidate = _SCRIPTS / sub / rel_or_name
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(rel_or_name)


def _load(rel_or_name: str) -> ModuleType:
    path = _resolve(rel_or_name)
    module_name = path.stem.replace("-", "_")
    spec = importlib.util.spec_from_file_location(module_name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="session")
def load_script():
    """Return a function that loads a script in scripts/<sub>/ as a module.

    Pass either a basename ("generate-skills.py") or a relative path
    ("build/generate-skills.py").
    """
    return _load
