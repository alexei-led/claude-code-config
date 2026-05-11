"""One-shot helper: migrate legacy skill dirs into `src/skills/<name>/`.

Takes the same pragmatic shape as `migrate_hooks.py`: read the legacy source
under `plugins/<plugin>/skills/<name>/` (and the per-target sidecars under
`plugins/<plugin>/skills-codex/<name>/` / `skills-pi/<name>/`) and emit the
vendor-neutral overlay tree:

    src/skills/<name>/SKILL.md                — base, frontmatter holds only
                                                cross-target keys (name,
                                                description, optional targets)
    src/skills/<name>/claude/frontmatter.yaml — CC-only frontmatter keys
    src/skills/<name>/<target>/body.md        — full-replacement body when the
                                                legacy sidecar diverges from
                                                base content
    src/skills/<name>/<target>/frontmatter.yaml — per-target frontmatter
                                                  overlay extracted from the
                                                  hand-edited sidecar
    src/skills/<name>/scripts|references|assets/... — support trees copied as-is

The script is parametric: callers pass a list of `MigrationSpec` records
describing each skill (source plugin dir, optional sidecars to import, optional
`targets:` restriction, optional swap of base vs Claude body for skills whose
vendor-neutral content lives in a codex sidecar).

Idempotent: re-running overwrites only files whose contents differ.
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

try:
    import frontmatter
    import yaml
except ImportError:
    print("ERROR: uv pip install -e .[test]", file=sys.stderr)
    sys.exit(1)

log = logging.getLogger("migrate_skills")

ROOT = Path(__file__).resolve().parents[2]

CC_ONLY_FRONTMATTER_KEYS = frozenset(
    {
        "allowed-tools",
        "user-invocable",
        "context",
        "agent",
        "argument-hint",
        "arguments",
        "disable-model-invocation",
        "hooks",
        "paths",
        "shell",
        "tools",
        "model",
        "color",
        "effort",
        "skills",
        "license",
        "metadata",
    }
)

BASE_FRONTMATTER_KEYS = frozenset({"name", "description", "targets"})


@dataclass
class MigrationSpec:
    """One skill migration."""

    name: str
    source_plugin_dir: Path
    targets_restriction: list[str] | None = None
    swap_claude_body: bool = False
    swap_pi_body: bool = False
    import_codex_body: bool = False
    import_pi_body: bool = False
    extra_files: list[Path] = field(default_factory=list)
    move_md_siblings_to_references: bool = True


def _split_frontmatter(meta: dict) -> tuple[dict, dict]:
    """Split a base SKILL.md frontmatter into (base_meta, claude_meta)."""
    base: dict = {}
    claude: dict = {}
    for key, value in meta.items():
        if key in BASE_FRONTMATTER_KEYS:
            base[key] = value
        elif key in CC_ONLY_FRONTMATTER_KEYS:
            claude[key] = value
        else:
            log.warning("dropping unrecognised frontmatter key %r", key)
    return base, claude


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _write_text_if_changed(path: Path, content: str) -> bool:
    if path.is_file() and path.read_text() == content:
        return False
    _ensure_dir(path.parent)
    path.write_text(content)
    return True


def _write_yaml_if_changed(path: Path, data: dict) -> bool:
    rendered = yaml.safe_dump(data, sort_keys=False)
    return _write_text_if_changed(path, rendered)


def _write_skill_md(path: Path, meta: dict, body: str) -> bool:
    post = frontmatter.Post(body, **meta)
    rendered = frontmatter.dumps(post)
    if not rendered.endswith("\n"):
        rendered += "\n"
    return _write_text_if_changed(path, rendered)


def _copy_support_tree(src: Path, dst: Path) -> int:
    """Copy a subdir tree, returning the number of files copied."""
    if not src.is_dir():
        return 0
    n = 0
    for item in sorted(src.rglob("*")):
        if not item.is_file():
            continue
        rel = item.relative_to(src)
        target = dst / rel
        _ensure_dir(target.parent)
        if target.is_file() and target.read_bytes() == item.read_bytes():
            continue
        shutil.copy2(item, target)
        n += 1
    return n


def _discover_md_siblings(src_dir: Path) -> list[Path]:
    """Return non-SKILL .md files that live directly under `src_dir`."""
    skipped = {"SKILL.md", "SKILL.codex.md", "SKILL.pi.md"}
    return [
        p
        for p in sorted(src_dir.iterdir())
        if p.is_file() and p.suffix == ".md" and p.name not in skipped
    ]


def _rewrite_sibling_links(body: str, names: Iterable[str]) -> str:
    """Rewrite `[label](Foo.md)` → `[label](references/Foo.md)` for each name.

    Only rewrites a bare basename target; leaves links already prefixed
    (`./Foo.md`, `references/Foo.md`, absolute URLs) untouched.
    """
    out = body
    for name in names:
        out = out.replace(f"]({name})", f"](references/{name})")
    return out


def _copy_extras(srcs: Iterable[Path], dst: Path) -> int:
    n = 0
    for src in srcs:
        if not src.is_file():
            log.warning("extra file %s not found, skipping", src)
            continue
        target = dst / src.name
        _ensure_dir(target.parent)
        if target.is_file() and target.read_bytes() == src.read_bytes():
            continue
        shutil.copy2(src, target)
        n += 1
    return n


def _load(skill_path: Path) -> tuple[dict, str]:
    post = frontmatter.loads(skill_path.read_text())
    return dict(post.metadata), post.content


def migrate(spec: MigrationSpec, out_root: Path) -> None:
    """Materialise a single skill under `src/skills/<name>/`."""
    src_dir = spec.source_plugin_dir / "skills" / spec.name
    base_path = src_dir / "SKILL.md"
    if not base_path.is_file():
        raise FileNotFoundError(base_path)

    base_meta, base_body = _load(base_path)
    cc_codex_sidecar = src_dir / "SKILL.codex.md"
    cc_pi_sidecar = src_dir / "SKILL.pi.md"

    plugin = spec.source_plugin_dir.name
    target_dir = out_root / spec.name

    sibling_md = (
        _discover_md_siblings(src_dir) if spec.move_md_siblings_to_references else []
    )
    sibling_names = [p.name for p in sibling_md]

    if sibling_names:
        base_body = _rewrite_sibling_links(base_body, sibling_names)

    if spec.swap_claude_body and cc_codex_sidecar.is_file():
        codex_meta, codex_body = _load(cc_codex_sidecar)
        new_base_meta = {
            k: codex_meta[k] for k in ("name", "description") if k in codex_meta
        }
        if "name" not in new_base_meta:
            new_base_meta["name"] = base_meta.get("name", spec.name)
        if spec.targets_restriction:
            new_base_meta["targets"] = list(spec.targets_restriction)
        if sibling_names:
            codex_body = _rewrite_sibling_links(codex_body, sibling_names)
        _write_skill_md(target_dir / "SKILL.md", new_base_meta, codex_body)

        _, claude_meta = _split_frontmatter(base_meta)
        if claude_meta:
            _write_yaml_if_changed(
                target_dir / "claude" / "frontmatter.yaml", claude_meta
            )
        _write_text_if_changed(target_dir / "claude" / "body.md", base_body)
    elif spec.swap_pi_body and cc_pi_sidecar.is_file():
        pi_meta, pi_body = _load(cc_pi_sidecar)
        new_base_meta = {k: pi_meta[k] for k in ("name", "description") if k in pi_meta}
        if "name" not in new_base_meta:
            new_base_meta["name"] = base_meta.get("name", spec.name)
        if spec.targets_restriction:
            new_base_meta["targets"] = list(spec.targets_restriction)
        if sibling_names:
            pi_body = _rewrite_sibling_links(pi_body, sibling_names)
        _write_skill_md(target_dir / "SKILL.md", new_base_meta, pi_body)

        _, claude_meta = _split_frontmatter(base_meta)
        if claude_meta:
            _write_yaml_if_changed(
                target_dir / "claude" / "frontmatter.yaml", claude_meta
            )
        _write_text_if_changed(target_dir / "claude" / "body.md", base_body)
    else:
        new_base_meta, claude_meta = _split_frontmatter(base_meta)
        if spec.targets_restriction:
            new_base_meta["targets"] = list(spec.targets_restriction)
        _write_skill_md(target_dir / "SKILL.md", new_base_meta, base_body)
        if claude_meta:
            _write_yaml_if_changed(
                target_dir / "claude" / "frontmatter.yaml", claude_meta
            )

    if spec.import_codex_body and cc_codex_sidecar.is_file():
        codex_meta, codex_body = _load(cc_codex_sidecar)
        _write_text_if_changed(target_dir / "codex" / "body.md", codex_body)
        overlay = {
            k: v
            for k, v in codex_meta.items()
            if k not in ("name", "description") and k not in CC_ONLY_FRONTMATTER_KEYS
        }
        if overlay:
            _write_yaml_if_changed(target_dir / "codex" / "frontmatter.yaml", overlay)

    if spec.import_pi_body and not spec.swap_pi_body and cc_pi_sidecar.is_file():
        pi_meta, pi_body = _load(cc_pi_sidecar)
        _write_text_if_changed(target_dir / "pi" / "body.md", pi_body)
        overlay = {
            k: v
            for k, v in pi_meta.items()
            if k not in ("name", "description") and k not in CC_ONLY_FRONTMATTER_KEYS
        }
        if overlay:
            _write_yaml_if_changed(target_dir / "pi" / "frontmatter.yaml", overlay)

    for sub in ("scripts", "references", "assets"):
        _copy_support_tree(src_dir / sub, target_dir / sub)

    if sibling_md:
        _copy_extras(sibling_md, target_dir / "references")

    if spec.import_pi_body and cc_pi_sidecar.is_file() and sibling_names:
        pi_overlay_path = target_dir / "pi" / "body.md"
        if pi_overlay_path.is_file():
            pi_body = pi_overlay_path.read_text()
            rewritten = _rewrite_sibling_links(pi_body, sibling_names)
            _write_text_if_changed(pi_overlay_path, rewritten)

    if spec.extra_files:
        _copy_extras(spec.extra_files, target_dir / "references")

    log.info("migrated skill=%s from plugin=%s", spec.name, plugin)


BATCH_2: list[MigrationSpec] = []  # populated below after BATCH_1 declaration


BATCH_1: list[MigrationSpec] = [
    MigrationSpec(name="writing-go", source_plugin_dir=ROOT / "plugins" / "go-dev"),
    MigrationSpec(
        name="writing-python", source_plugin_dir=ROOT / "plugins" / "python-dev"
    ),
    MigrationSpec(
        name="writing-typescript",
        source_plugin_dir=ROOT / "plugins" / "typescript-dev",
    ),
    MigrationSpec(name="writing-web", source_plugin_dir=ROOT / "plugins" / "web-dev"),
    MigrationSpec(
        name="sequential-thinking",
        source_plugin_dir=ROOT / "plugins" / "dev-tools",
    ),
    MigrationSpec(
        name="using-modern-cli",
        source_plugin_dir=ROOT / "plugins" / "dev-tools",
    ),
    MigrationSpec(
        name="using-cloud-cli",
        source_plugin_dir=ROOT / "plugins" / "infra-ops",
    ),
    MigrationSpec(
        name="using-git-worktrees",
        source_plugin_dir=ROOT / "plugins" / "dev-tools",
    ),
    MigrationSpec(
        name="refactoring-code",
        source_plugin_dir=ROOT / "plugins" / "dev-workflow",
        import_pi_body=True,
    ),
    MigrationSpec(
        name="smart-explore",
        source_plugin_dir=ROOT / "plugins" / "dev-tools",
        import_pi_body=True,
    ),
    MigrationSpec(
        name="searching-code",
        source_plugin_dir=ROOT / "plugins" / "dev-workflow",
        import_pi_body=True,
    ),
    MigrationSpec(
        name="brainstorming-ideas",
        source_plugin_dir=ROOT / "plugins" / "dev-tools",
        swap_claude_body=True,
    ),
    MigrationSpec(
        name="grill-me",
        source_plugin_dir=ROOT / "plugins" / "dev-tools",
        extra_files=[
            ROOT / "plugins" / "dev-tools" / "skills" / "grill-me" / "CREDITS.md"
        ],
    ),
    MigrationSpec(
        name="debating-ideas",
        source_plugin_dir=ROOT / "plugins" / "dev-tools",
        targets_restriction=["claude"],
    ),
]


BATCH_2[:] = [
    MigrationSpec(
        name="testing-e2e",
        source_plugin_dir=ROOT / "plugins" / "testing-e2e",
        swap_pi_body=True,
        import_codex_body=True,
    ),
    MigrationSpec(
        name="mem-history",
        source_plugin_dir=ROOT / "plugins" / "dev-tools",
        import_pi_body=True,
    ),
    MigrationSpec(
        name="exploring-repos",
        source_plugin_dir=ROOT / "plugins" / "dev-tools",
        swap_pi_body=True,
    ),
    MigrationSpec(
        name="researching-web",
        source_plugin_dir=ROOT / "plugins" / "dev-tools",
        swap_pi_body=True,
    ),
    MigrationSpec(
        name="reviewing-cc-config",
        source_plugin_dir=ROOT / "plugins" / "dev-tools",
        targets_restriction=["claude"],
    ),
    MigrationSpec(
        name="evolving-config",
        source_plugin_dir=ROOT / "plugins" / "dev-tools",
        swap_pi_body=True,
    ),
    MigrationSpec(
        name="fixing-code",
        source_plugin_dir=ROOT / "plugins" / "dev-workflow",
        swap_claude_body=True,
    ),
    MigrationSpec(
        name="improving-tests",
        source_plugin_dir=ROOT / "plugins" / "dev-workflow",
        swap_claude_body=True,
    ),
    MigrationSpec(
        name="documenting-code",
        source_plugin_dir=ROOT / "plugins" / "dev-workflow",
        swap_pi_body=True,
    ),
    MigrationSpec(
        name="deploying-infra",
        source_plugin_dir=ROOT / "plugins" / "infra-ops",
        targets_restriction=["claude"],
    ),
    MigrationSpec(
        name="managing-infra",
        source_plugin_dir=ROOT / "plugins" / "infra-ops",
    ),
    MigrationSpec(
        name="linting-instructions",
        source_plugin_dir=ROOT / "plugins" / "dev-tools",
        targets_restriction=["claude"],
    ),
    MigrationSpec(
        name="analyzing-usage",
        source_plugin_dir=ROOT / "plugins" / "dev-tools",
        targets_restriction=["claude"],
    ),
    MigrationSpec(
        name="looking-up-docs",
        source_plugin_dir=ROOT / "plugins" / "dev-tools",
    ),
    MigrationSpec(
        name="context7-cli",
        source_plugin_dir=ROOT / "plugins" / "dev-tools",
    ),
    MigrationSpec(
        name="improve-codebase-architecture",
        source_plugin_dir=ROOT / "plugins" / "dev-workflow",
    ),
    MigrationSpec(
        name="ccgram-messaging",
        source_plugin_dir=ROOT / "plugins" / "dev-workflow",
    ),
]


BATCHES: dict[str, list[MigrationSpec]] = {
    "batch1": BATCH_1,
    "batch2": BATCH_2,
    "all": BATCH_1 + BATCH_2,
}


def run(out_root: Path, specs: Iterable[MigrationSpec]) -> None:
    out_root.mkdir(parents=True, exist_ok=True)
    for spec in specs:
        migrate(spec, out_root)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out",
        type=Path,
        default=ROOT / "src" / "skills",
        help="Output dir (default: src/skills/)",
    )
    ap.add_argument(
        "--batch",
        choices=sorted(BATCHES),
        default="batch1",
        help="Which migration batch to run (default: batch1)",
    )
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )
    run(args.out, BATCHES[args.batch])
    return 0


if __name__ == "__main__":
    sys.exit(main())
