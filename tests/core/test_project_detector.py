"""Tests for project_detector: find_project_root (T018), resolve_tests_root (T002-T004)."""

from pathlib import Path

import pytest

from scaffold_ca_python.core.name_utils import ScaffoldError
from scaffold_ca_python.core.project_detector import find_project_root, resolve_tests_root

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_pyproject(directory: Path, *, with_section: bool) -> Path:
    """Write a minimal pyproject.toml into *directory*."""
    content = "[project]\nname = 'test'\n"
    if with_section:
        content += "\n[tool.scaffold-ca-python]\n"
    p = directory / "pyproject.toml"
    p.write_text(content)
    return p


def _make_ca_layout(directory: Path) -> None:
    """Create canonical CA subdirectories inside *directory*."""
    for subdir in ("domain", "infrastructure", "application"):
        (directory / subdir).mkdir()


# ---------------------------------------------------------------------------
# Detection via [tool.scaffold-ca-python] section
# ---------------------------------------------------------------------------


def test_finds_root_in_cwd(tmp_path: Path) -> None:
    _make_pyproject(tmp_path, with_section=True)
    assert find_project_root(cwd=tmp_path) == tmp_path


def test_finds_root_in_parent(tmp_path: Path) -> None:
    _make_pyproject(tmp_path, with_section=True)
    child = tmp_path / "src" / "mypackage"
    child.mkdir(parents=True)
    assert find_project_root(cwd=child) == tmp_path


def test_ignores_pyproject_without_section(tmp_path: Path) -> None:
    """A pyproject.toml without the section should NOT count as the root via pyproject strategy."""
    _make_pyproject(tmp_path, with_section=False)
    # Also needs a fallback to CA layout or error
    with pytest.raises(ScaffoldError):
        find_project_root(cwd=tmp_path)


# ---------------------------------------------------------------------------
# Fallback to CA directory layout
# ---------------------------------------------------------------------------


def test_fallback_to_ca_directories(tmp_path: Path) -> None:
    # No pyproject.toml with section, but has CA directories
    _make_ca_layout(tmp_path)
    assert find_project_root(cwd=tmp_path) == tmp_path


def test_fallback_ca_directories_in_parent(tmp_path: Path) -> None:
    _make_ca_layout(tmp_path)
    child = tmp_path / "domain" / "model"
    child.mkdir(parents=True)
    assert find_project_root(cwd=child) == tmp_path


# ---------------------------------------------------------------------------
# Error case
# ---------------------------------------------------------------------------


def test_raises_when_neither_found(tmp_path: Path) -> None:
    # Empty directory, no pyproject.toml with section, no CA layout
    with pytest.raises(ScaffoldError, match="root"):
        find_project_root(cwd=tmp_path)


def test_raises_at_filesystem_boundary(tmp_path: Path) -> None:
    # Walk stops at filesystem root without finding anything
    # tmp_path is deep inside actual FS — use a plain empty dir
    empty = tmp_path / "deep" / "nested" / "path"
    empty.mkdir(parents=True)
    with pytest.raises(ScaffoldError):
        find_project_root(cwd=empty)


# ---------------------------------------------------------------------------
# resolve_tests_root (T002-T004)
# ---------------------------------------------------------------------------


def test_resolve_tests_root_returns_src_tests_when_src_tests_exists(tmp_path: Path) -> None:
    (tmp_path / "src" / "tests").mkdir(parents=True)
    assert resolve_tests_root(tmp_path) == tmp_path / "src" / "tests"


def test_resolve_tests_root_falls_back_to_root_tests(tmp_path: Path) -> None:
    (tmp_path / "tests").mkdir()
    assert resolve_tests_root(tmp_path) == tmp_path / "tests"


def test_resolve_tests_root_defaults_to_src_tests_when_neither_exists(tmp_path: Path) -> None:
    assert resolve_tests_root(tmp_path) == tmp_path / "src" / "tests"
