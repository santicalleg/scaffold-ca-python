"""Tests for pyproject_writer: inject_dependencies and dry_run_inject (T005)."""

import tomllib
from pathlib import Path

import pytest

from scaffold_ca_python.core.pyproject_writer import dry_run_inject, inject_dependencies


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_pyproject(tmp_path: Path, deps: list[str] | None = None) -> Path:
    """Write a minimal pyproject.toml with optional pre-existing dependencies."""
    existing = deps if deps is not None else []
    deps_toml = "\n".join(f'    "{d}",' for d in existing)
    content = f"""\
[project]
name = "my-project"
dependencies = [
{deps_toml}
]

[tool.scaffold-ca-python]
name = "MyProject"
"""
    path = tmp_path / "pyproject.toml"
    path.write_text(content, encoding="utf-8")
    return path


def _make_pyproject_no_deps(tmp_path: Path) -> Path:
    """Write a pyproject.toml with no [project.dependencies] key at all."""
    content = """\
[project]
name = "my-project"

[tool.scaffold-ca-python]
name = "MyProject"
"""
    path = tmp_path / "pyproject.toml"
    path.write_text(content, encoding="utf-8")
    return path


def _read_deps(pyproject: Path) -> list[str]:
    with pyproject.open("rb") as fh:
        data = tomllib.load(fh)
    return data.get("project", {}).get("dependencies", [])


# ---------------------------------------------------------------------------
# inject_dependencies — writes
# ---------------------------------------------------------------------------

def test_inject_adds_new_package(tmp_path: Path) -> None:
    pyproject = _make_pyproject(tmp_path)
    added = inject_dependencies(tmp_path, ["fastapi>=0.100"])
    assert added == ["fastapi>=0.100"]
    assert any("fastapi" in d for d in _read_deps(pyproject))


def test_inject_adds_multiple_packages(tmp_path: Path) -> None:
    pyproject = _make_pyproject(tmp_path)
    added = inject_dependencies(tmp_path, ["fastapi>=0.100", "uvicorn[standard]>=0.20"])
    assert len(added) == 2
    deps = _read_deps(pyproject)
    assert any("fastapi" in d for d in deps)
    assert any("uvicorn" in d for d in deps)


def test_inject_skips_duplicate_by_name_prefix(tmp_path: Path) -> None:
    _make_pyproject(tmp_path, deps=["fastapi>=0.100"])
    added = inject_dependencies(tmp_path, ["fastapi>=0.100"])
    assert added == []
    # still only one fastapi entry
    assert sum(1 for d in _read_deps(tmp_path / "pyproject.toml") if "fastapi" in d) == 1


def test_inject_skips_duplicate_with_extras(tmp_path: Path) -> None:
    _make_pyproject(tmp_path, deps=["uvicorn[standard]>=0.20"])
    added = inject_dependencies(tmp_path, ["uvicorn[standard]>=0.20"])
    assert added == []


def test_inject_partial_list_only_adds_missing(tmp_path: Path) -> None:
    _make_pyproject(tmp_path, deps=["fastapi>=0.100"])
    added = inject_dependencies(tmp_path, ["fastapi>=0.100", "httpx>=0.27"])
    assert added == ["httpx>=0.27"]


def test_inject_returns_empty_when_all_present(tmp_path: Path) -> None:
    _make_pyproject(tmp_path, deps=["fastapi>=0.100", "httpx>=0.27"])
    added = inject_dependencies(tmp_path, ["fastapi>=0.100", "httpx>=0.27"])
    assert added == []


def test_inject_creates_dependencies_key_when_absent(tmp_path: Path) -> None:
    _make_pyproject_no_deps(tmp_path)
    added = inject_dependencies(tmp_path, ["httpx>=0.27"])
    assert added == ["httpx>=0.27"]
    assert any("httpx" in d for d in _read_deps(tmp_path / "pyproject.toml"))


def test_inject_with_empty_packages_list_returns_empty(tmp_path: Path) -> None:
    _make_pyproject(tmp_path)
    added = inject_dependencies(tmp_path, [])
    assert added == []


def test_inject_preserves_existing_dependencies(tmp_path: Path) -> None:
    _make_pyproject(tmp_path, deps=["pydantic>=2.0", "rich>=14.0"])
    inject_dependencies(tmp_path, ["httpx>=0.27"])
    deps = _read_deps(tmp_path / "pyproject.toml")
    assert any("pydantic" in d for d in deps)
    assert any("rich" in d for d in deps)
    assert any("httpx" in d for d in deps)


# ---------------------------------------------------------------------------
# dry_run_inject — never writes
# ---------------------------------------------------------------------------

def test_dry_run_returns_packages_that_would_be_added(tmp_path: Path) -> None:
    _make_pyproject(tmp_path)
    would_add = dry_run_inject(tmp_path, ["fastapi>=0.100", "uvicorn[standard]>=0.20"])
    assert would_add == ["fastapi>=0.100", "uvicorn[standard]>=0.20"]


def test_dry_run_never_writes_to_disk(tmp_path: Path) -> None:
    pyproject = _make_pyproject(tmp_path)
    original = pyproject.read_bytes()
    dry_run_inject(tmp_path, ["fastapi>=0.100"])
    assert pyproject.read_bytes() == original


def test_dry_run_skips_already_present_packages(tmp_path: Path) -> None:
    _make_pyproject(tmp_path, deps=["fastapi>=0.100"])
    would_add = dry_run_inject(tmp_path, ["fastapi>=0.100"])
    assert would_add == []


def test_dry_run_with_empty_packages_returns_empty(tmp_path: Path) -> None:
    _make_pyproject(tmp_path)
    would_add = dry_run_inject(tmp_path, [])
    assert would_add == []


# ---------------------------------------------------------------------------
# Error handling
# ---------------------------------------------------------------------------

def test_malformed_toml_raises_on_inject(tmp_path: Path) -> None:
    bad = tmp_path / "pyproject.toml"
    bad.write_text("this is not valid toml ][", encoding="utf-8")
    with pytest.raises(Exception):
        inject_dependencies(tmp_path, ["fastapi>=0.100"])


def test_missing_pyproject_raises_on_inject(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        inject_dependencies(tmp_path, ["fastapi>=0.100"])
