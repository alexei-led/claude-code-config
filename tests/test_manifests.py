"""Tests for root manifest generators (Task 12).

Covers:
- `load_plugins` reads `src/plugins/*/plugin.yaml` deterministically.
- `write_claude_marketplace` / `write_codex_marketplace` /
  `write_gemini_extension` produce well-formed JSON with sources
  pointing at the correct dist paths.
- `ensure_gemini_symlinks` creates symlinks idempotently and refuses
  to clobber non-symlink paths.
- Running the generators twice produces no diff (idempotent).
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest


@pytest.fixture(scope="module")
def manifests(load_script):
    return load_script("build/manifests.py")


@pytest.fixture
def fake_root(tmp_path: Path) -> Path:
    plugins = tmp_path / "src" / "plugins"
    plugins.mkdir(parents=True)

    (plugins / "alpha").mkdir()
    (plugins / "alpha" / "plugin.yaml").write_text(
        "name: alpha\n"
        "version: 1.0.0\n"
        "description: Alpha plugin\n"
        "category: workflow\n"
        "tags:\n  - alpha-tag\n"
        "keywords:\n  - alpha-kw\n"
        "skills: [shared-skill, only-alpha]\n"
        "agents: []\n"
        "hooks: []\n"
    )

    (plugins / "beta").mkdir()
    (plugins / "beta" / "plugin.yaml").write_text(
        "name: beta\n"
        "version: 1.0.0\n"
        "description: Beta plugin\n"
        "category: language\n"
        "skills: [only-beta]\n"
        "agents: []\n"
        "hooks: []\n"
    )

    # Plugin dir without manifest — must be skipped.
    (plugins / "skipme").mkdir()

    # Both marketplace generators filter out plugins without a matching
    # dist/<target>/plugins/<name>/ dir; create the dirs so alpha and beta
    # both appear in the manifests under test.
    for target in ("claude", "codex"):
        for name in ("alpha", "beta"):
            plugin_dir = tmp_path / "dist" / target / "plugins" / name
            plugin_dir.mkdir(parents=True, exist_ok=True)
            if target == "codex":
                (plugin_dir / "skills").mkdir()

    return tmp_path


def test_load_plugins_sorted_and_named(manifests, fake_root):
    plugins = manifests.load_plugins(fake_root)
    assert [p["name"] for p in plugins] == ["alpha", "beta"]
    assert plugins[0]["description"] == "Alpha plugin"


def test_load_plugins_missing_root(manifests, tmp_path):
    assert manifests.load_plugins(tmp_path) == []


def test_load_plugins_rejects_non_mapping(manifests, tmp_path):
    bad = tmp_path / "src" / "plugins" / "bad"
    bad.mkdir(parents=True)
    (bad / "plugin.yaml").write_text("- a\n- b\n")
    with pytest.raises(ValueError, match="must be a mapping"):
        manifests.load_plugins(tmp_path)


def test_write_claude_marketplace_paths_and_fields(manifests, fake_root):
    plugins = manifests.load_plugins(fake_root)
    out = manifests.write_claude_marketplace(plugins, fake_root)
    assert out == fake_root / ".claude-plugin" / "marketplace.json"

    data = json.loads(out.read_text())
    assert data["name"] == "cc-thingz"
    assert data["version"] == "1.0.0"
    names = [p["name"] for p in data["plugins"]]
    assert names == ["alpha", "beta"]
    sources = [p["source"] for p in data["plugins"]]
    assert sources == [
        "./dist/claude/plugins/alpha",
        "./dist/claude/plugins/beta",
    ]
    # Optional metadata flows through.
    alpha = data["plugins"][0]
    assert alpha["category"] == "workflow"
    assert alpha["tags"] == ["alpha-tag"]
    assert alpha["keywords"] == ["alpha-kw"]
    assert alpha["version"] == "1.0.0"


def test_write_claude_marketplace_with_global_meta(manifests, fake_root):
    (fake_root / "src" / "plugins" / "marketplace.yaml").write_text(
        "name: cc-thingz\n"
        "version: 9.9.9\n"
        "description: top-level desc\n"
        "homepage: https://example.com\n"
        "repository: https://example.com/repo\n"
        "license: MIT\n"
        "owner:\n  name: Test Owner\n  email: t@example.com\n"
    )
    plugins = manifests.load_plugins(fake_root)
    out = manifests.write_claude_marketplace(plugins, fake_root)
    data = json.loads(out.read_text())
    assert data["version"] == "9.9.9"
    assert data["metadata"]["description"] == "top-level desc"
    assert data["metadata"]["homepage"] == "https://example.com"
    assert data["owner"] == {"name": "Test Owner", "email": "t@example.com"}


def test_write_codex_marketplace_paths(manifests, fake_root):
    plugins = manifests.load_plugins(fake_root)
    out = manifests.write_codex_marketplace(plugins, fake_root)
    assert out == fake_root / ".agents" / "plugins" / "marketplace.json"

    data = json.loads(out.read_text())
    assert data["name"] == "cc-thingz"
    assert data["interface"] == {"displayName": "cc-thingz"}
    assert [p["name"] for p in data["plugins"]] == ["alpha", "beta"]
    for entry in data["plugins"]:
        assert entry["source"]["source"] == "local"
        assert entry["source"]["path"].startswith("./dist/codex/plugins/")
        assert entry["policy"] == {
            "installation": "AVAILABLE",
            "authentication": "ON_FIRST_USE",
        }


def test_write_codex_marketplace_skips_plugins_without_dist_dir(manifests, fake_root):
    """Plugins lacking a dist/codex/plugins/<name>/ dir are omitted."""
    # Remove beta's codex dist dir; only alpha should remain.
    import shutil

    shutil.rmtree(fake_root / "dist" / "codex" / "plugins" / "beta")
    plugins = manifests.load_plugins(fake_root)
    out = manifests.write_codex_marketplace(plugins, fake_root)
    data = json.loads(out.read_text())
    assert [p["name"] for p in data["plugins"]] == ["alpha"]


def test_write_claude_marketplace_skips_plugins_without_dist_dir(manifests, fake_root):
    """Plugins lacking a dist/claude/plugins/<name>/ dir are omitted."""
    import shutil

    shutil.rmtree(fake_root / "dist" / "claude" / "plugins" / "beta")
    plugins = manifests.load_plugins(fake_root)
    out = manifests.write_claude_marketplace(plugins, fake_root)
    data = json.loads(out.read_text())
    assert [p["name"] for p in data["plugins"]] == ["alpha"]


def test_write_codex_marketplace_categories(manifests, fake_root):
    plugins = manifests.load_plugins(fake_root)
    out = manifests.write_codex_marketplace(plugins, fake_root)
    data = json.loads(out.read_text())
    alpha = next(p for p in data["plugins"] if p["name"] == "alpha")
    assert alpha["category"] == "workflow"


def test_write_codex_marketplace_honors_marketplace_name(manifests, fake_root):
    """Mirror rewrites set `marketplace_name` to rename the published entry.

    The Codex marketplace must use the renamed name (like the Claude
    marketplace) while the on-disk source path keeps the canonical dir name.
    """
    plugin_yaml = fake_root / "src" / "plugins" / "alpha" / "plugin.yaml"
    plugin_yaml.write_text(plugin_yaml.read_text() + "marketplace_name: alpha-mirror\n")
    plugins = manifests.load_plugins(fake_root)
    out = manifests.write_codex_marketplace(plugins, fake_root)
    data = json.loads(out.read_text())
    alpha = next(p for p in data["plugins"] if p["source"]["path"].endswith("/alpha"))
    assert alpha["name"] == "alpha-mirror"


def test_write_claude_marketplace_honors_marketplace_name(manifests, fake_root):
    plugin_yaml = fake_root / "src" / "plugins" / "alpha" / "plugin.yaml"
    plugin_yaml.write_text(plugin_yaml.read_text() + "marketplace_name: alpha-mirror\n")
    plugins = manifests.load_plugins(fake_root)
    out = manifests.write_claude_marketplace(plugins, fake_root)
    data = json.loads(out.read_text())
    alpha = next(p for p in data["plugins"] if p["source"].endswith("/alpha"))
    assert alpha["name"] == "alpha-mirror"


def test_write_gemini_extension_at_root(manifests, fake_root):
    plugins = manifests.load_plugins(fake_root)
    out = manifests.write_gemini_extension(plugins, fake_root)
    assert out == fake_root / "gemini-extension.json"

    data = json.loads(out.read_text())
    assert data["name"] == "cc-thingz"
    assert data["version"] == "1.0.0"
    assert data["contextFileName"] == "AGENTS.md"
    assert "description" in data


def test_ensure_gemini_symlinks_creates_links(manifests, fake_root):
    created = manifests.ensure_gemini_symlinks(fake_root)
    assert (fake_root / "skills").is_symlink()
    assert (fake_root / "agents").is_symlink()
    assert (fake_root / "hooks").is_symlink()
    assert os.readlink(fake_root / "skills") == "dist/gemini/skills"
    assert os.readlink(fake_root / "agents") == "dist/gemini/agents"
    assert os.readlink(fake_root / "hooks") == "dist/gemini/hooks"
    assert len(created) == 3


def test_ensure_gemini_symlinks_idempotent(manifests, fake_root):
    manifests.ensure_gemini_symlinks(fake_root)
    second = manifests.ensure_gemini_symlinks(fake_root)
    # Second call returns no newly-created symlinks but leaves them in place.
    assert second == []
    assert os.readlink(fake_root / "skills") == "dist/gemini/skills"


def test_ensure_gemini_symlinks_replaces_stale(manifests, fake_root):
    (fake_root / "skills").symlink_to("somewhere/else")
    manifests.ensure_gemini_symlinks(fake_root)
    assert os.readlink(fake_root / "skills") == "dist/gemini/skills"


def test_ensure_gemini_symlinks_refuses_non_symlink(manifests, fake_root):
    (fake_root / "skills").mkdir()
    with pytest.raises(FileExistsError):
        manifests.ensure_gemini_symlinks(fake_root)


def test_write_claude_plugin_manifests_basic(manifests, fake_root):
    plugins = manifests.load_plugins(fake_root)
    written = manifests.write_claude_plugin_manifests(plugins, fake_root)
    assert len(written) == 2
    alpha = json.loads(
        (
            fake_root
            / "dist"
            / "claude"
            / "plugins"
            / "alpha"
            / ".claude-plugin"
            / "plugin.json"
        ).read_text()
    )
    assert alpha["name"] == "alpha"
    assert alpha["version"] == "1.0.0"
    assert alpha["description"] == "Alpha plugin"
    assert alpha["keywords"] == ["alpha-kw"]
    assert "author" not in alpha  # no global owner set in this fixture


def test_write_claude_plugin_manifests_inherits_global_owner(manifests, fake_root):
    (fake_root / "src" / "plugins" / "marketplace.yaml").write_text(
        "owner:\n  name: Test Owner\n  email: t@example.com\n"
        "homepage: https://example.com\n"
        "license: MIT\n"
    )
    plugins = manifests.load_plugins(fake_root)
    manifests.write_claude_plugin_manifests(plugins, fake_root)
    alpha = json.loads(
        (
            fake_root
            / "dist"
            / "claude"
            / "plugins"
            / "alpha"
            / ".claude-plugin"
            / "plugin.json"
        ).read_text()
    )
    assert alpha["author"] == {"name": "Test Owner", "email": "t@example.com"}
    assert alpha["homepage"] == "https://example.com"
    assert alpha["license"] == "MIT"


def test_write_claude_plugin_manifests_skips_missing_dist(manifests, fake_root):
    import shutil

    shutil.rmtree(fake_root / "dist" / "claude" / "plugins" / "beta")
    plugins = manifests.load_plugins(fake_root)
    written = manifests.write_claude_plugin_manifests(plugins, fake_root)
    assert [p.parent.parent.name for p in written] == ["alpha"]


def test_write_codex_plugin_manifests_basic_and_hooks(manifests, fake_root):
    # Add a codex hooks manifest for alpha so we get the hooks pointer.
    hooks_dir = fake_root / "dist" / "codex" / "plugins" / "alpha" / "hooks"
    hooks_dir.mkdir(parents=True, exist_ok=True)
    (hooks_dir / "codex.hooks.json").write_text("{}\n")

    plugins = manifests.load_plugins(fake_root)
    written = manifests.write_codex_plugin_manifests(plugins, fake_root)
    assert len(written) == 2
    alpha = json.loads(
        (
            fake_root
            / "dist"
            / "codex"
            / "plugins"
            / "alpha"
            / ".codex-plugin"
            / "plugin.json"
        ).read_text()
    )
    assert alpha["name"] == "alpha"
    assert alpha["skills"] == "./skills"
    assert alpha["hooks"] == "./hooks/codex.hooks.json"
    beta = json.loads(
        (
            fake_root
            / "dist"
            / "codex"
            / "plugins"
            / "beta"
            / ".codex-plugin"
            / "plugin.json"
        ).read_text()
    )
    assert beta["skills"] == "./skills"
    assert "hooks" not in beta


def test_write_all_full_run(manifests, fake_root):
    out = manifests.write_all(fake_root)
    assert out["claude"].is_file()
    assert out["codex"].is_file()
    assert out["gemini"].is_file()
    assert len(out["claude_plugins"]) == 2
    assert len(out["codex_plugins"]) == 2
    assert all(p.is_symlink() for p in out["symlinks"])


def test_write_all_idempotent_no_diff(manifests, fake_root):
    """Two runs produce byte-identical manifests and the same symlink layout."""
    manifests.write_all(fake_root)
    snap1 = {
        path.relative_to(fake_root): path.read_bytes()
        for path in [
            fake_root / ".claude-plugin" / "marketplace.json",
            fake_root / ".agents" / "plugins" / "marketplace.json",
            fake_root / "gemini-extension.json",
        ]
    }
    manifests.write_all(fake_root)
    snap2 = {
        path.relative_to(fake_root): path.read_bytes()
        for path in [
            fake_root / ".claude-plugin" / "marketplace.json",
            fake_root / ".agents" / "plugins" / "marketplace.json",
            fake_root / "gemini-extension.json",
        ]
    }
    assert snap1 == snap2


def test_resolve_version_falls_back_to_zero(manifests, tmp_path):
    """Empty plugin list with no global meta still produces a stable version."""
    out = manifests.write_gemini_extension([], tmp_path)
    data = json.loads(out.read_text())
    assert data["version"] == "0.0.0"
