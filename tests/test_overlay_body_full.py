"""Tests for `scripts.build.overlay` body full-replacement detection."""

from __future__ import annotations

import textwrap

import pytest


@pytest.fixture(scope="module")
def ov(load_script):
    return load_script("build/overlay.py")


def _md(s: str) -> str:
    return textwrap.dedent(s).lstrip("\n")


def test_full_replacement_when_top_header_differs(ov) -> None:
    """Overlay topic differs entirely from base — no header paths overlap."""
    base = _md(
        """
        # Playwright Browser Automation

        base intro

        ## Path resolution

        base body
        """
    )
    overlay = _md(
        """
        # Playwright Helper for Pi

        overlay intro

        ## Path resolution

        overlay body
        """
    )
    out = ov.apply_body_overlay(base, overlay)
    assert out == overlay
    assert "base intro" not in out
    assert "base body" not in out


def test_full_replacement_when_overlay_has_no_headers(ov) -> None:
    """Plain-prose overlay (no headers at all) replaces base entirely."""
    base = "# Top\n\nbase body\n"
    overlay = "use this exact text instead\n"
    out = ov.apply_body_overlay(base, overlay)
    assert out == overlay


def test_empty_overlay_returns_base_unchanged(ov) -> None:
    base = "# Top\n\nhello\n"
    assert ov.apply_body_overlay(base, "") == base
    assert ov.apply_body_overlay(base, "   \n\n") == base


def test_mirror_mode_when_top_header_matches(ov) -> None:
    base = _md(
        """
        # Top

        ## A

        base-a

        ## B

        base-b
        """
    )
    overlay = _md(
        """
        # Top

        ## A

        overlay-a
        """
    )
    out = ov.apply_body_overlay(base, overlay)
    assert "overlay-a" in out
    assert "base-a" not in out
    assert "base-b" in out


def test_mirror_mode_when_any_suffix_present(ov) -> None:
    """Append/prepend suffix anywhere forces mirror mode (no full-replace)."""
    base = _md(
        """
        # Different Base

        ## Workflow

        base-workflow
        """
    )
    overlay = _md(
        """
        # Different Base

        ## Workflow (_+)

        appended
        """
    )
    out = ov.apply_body_overlay(base, overlay)
    assert "base-workflow" in out
    assert "appended" in out
    assert out.find("base-workflow") < out.find("appended")


def test_mixed_mode_resolves_to_mirror(ov) -> None:
    """Some overlay headers match base, others don't → mirror mode.

    Documented behavior: any path overlap forces mirror; non-matching overlay
    headers are added as new subsections under their parent.
    """
    base = _md(
        """
        # Top

        ## Existing

        base-existing
        """
    )
    overlay = _md(
        """
        # Top

        ## Existing

        overlay-existing

        ## Brand new

        overlay-new
        """
    )
    out = ov.apply_body_overlay(base, overlay)
    assert "overlay-existing" in out
    assert "base-existing" not in out
    assert "Brand new" in out
    assert "overlay-new" in out


def test_full_replacement_when_only_deep_header_collides_by_title(ov) -> None:
    """Subsection title collision is not a path match — full replacement.

    Path match uses the full header chain. Same `## Path resolution` under a
    different top header is a different path.
    """
    base = _md(
        """
        # Base Topic

        ## Path resolution

        base path
        """
    )
    overlay = _md(
        """
        # Overlay Topic

        ## Path resolution

        overlay path
        """
    )
    out = ov.apply_body_overlay(base, overlay)
    assert out == overlay
    assert "base path" not in out


def test_full_replacement_preserves_exact_overlay_text(ov) -> None:
    """Trailing newlines, spacing, and formatting in overlay are preserved."""
    base = "# Top\n\nbase\n"
    overlay = "# Other\n\n- bullet\n- bullet\n\n```bash\necho hi\n```\n"
    out = ov.apply_body_overlay(base, overlay)
    assert out == overlay


def test_mirror_path_match_at_any_depth(ov) -> None:
    """Mirror mode triggers when overlay shares a deep path with base."""
    base = _md(
        """
        # Top

        ## A

        ### Detail

        base-detail
        """
    )
    overlay = _md(
        """
        # Top

        ## A

        ### Detail

        overlay-detail
        """
    )
    out = ov.apply_body_overlay(base, overlay)
    assert "overlay-detail" in out
    assert "base-detail" not in out
