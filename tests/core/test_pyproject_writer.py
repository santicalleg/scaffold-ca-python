"""Tests for pyproject_writer: inject_dependencies and dry_run_inject (T005)."""

import tomllib
from pathlib import Path

import pytest

from scaffold_ca_python.core.pyproject_writer import (
    dry_run_inject,
    dry_run_scripts_update,
    inject_dependencies,
    update_project_scripts,
)

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


# ---------------------------------------------------------------------------
# update_project_scripts — writes (T002–T004)
# ---------------------------------------------------------------------------


def _make_pyproject_with_scripts(tmp_path: Path, entry: str) -> Path:
    """Write a minimal pyproject.toml with a [project.scripts] entry."""
    content = f"""\
[project]
name = "my_app"

[project.scripts]
my_app = "{entry}"

[tool.scaffold-ca-python]
name = "MyApp"
python_package = "my_app"
"""
    path = tmp_path / "pyproject.toml"
    path.write_text(content, encoding="utf-8")
    return path


def _make_pyproject_without_scripts(tmp_path: Path) -> Path:
    """Write a minimal pyproject.toml with no [project.scripts] section."""
    content = """\
[project]
name = "my_app"

[tool.scaffold-ca-python]
name = "MyApp"
python_package = "my_app"
"""
    path = tmp_path / "pyproject.toml"
    path.write_text(content, encoding="utf-8")
    return path


def _read_scripts(pyproject: Path) -> dict[str, str]:
    with pyproject.open("rb") as fh:
        data = tomllib.load(fh)
    return data.get("project", {}).get("scripts", {})


def test_update_project_scripts_changes_entry(tmp_path: Path) -> None:
    """T002: updates main:main → server:start_server and returns True."""
    pyproject = _make_pyproject_with_scripts(tmp_path, "my_app.main:main")
    result = update_project_scripts(tmp_path, "my_app")
    assert result is True
    assert _read_scripts(pyproject)["my_app"] == "my_app.server:start_server"


def test_update_project_scripts_is_idempotent(tmp_path: Path) -> None:
    """T003: second call returns False and leaves entry unchanged."""
    pyproject = _make_pyproject_with_scripts(tmp_path, "my_app.server:start_server")
    result = update_project_scripts(tmp_path, "my_app")
    assert result is False
    assert _read_scripts(pyproject)["my_app"] == "my_app.server:start_server"


def test_update_project_scripts_creates_section_when_absent(tmp_path: Path) -> None:
    """T004: creates [project.scripts] when missing and writes correct entry."""
    pyproject = _make_pyproject_without_scripts(tmp_path)
    result = update_project_scripts(tmp_path, "my_app")
    assert result is True
    assert _read_scripts(pyproject)["my_app"] == "my_app.server:start_server"


# ---------------------------------------------------------------------------
# dry_run_scripts_update — never writes (T005–T007)
# ---------------------------------------------------------------------------


def test_dry_run_scripts_update_returns_true_when_change_needed(tmp_path: Path) -> None:
    """T005: returns True (change needed) but does NOT write to disk."""
    pyproject = _make_pyproject_with_scripts(tmp_path, "my_app.main:main")
    original = pyproject.read_bytes()
    result = dry_run_scripts_update(tmp_path, "my_app")
    assert result is True
    assert pyproject.read_bytes() == original


def test_dry_run_scripts_update_returns_false_when_already_correct(tmp_path: Path) -> None:
    """T006: returns False when entry already matches server:start_server."""
    _make_pyproject_with_scripts(tmp_path, "my_app.server:start_server")
    result = dry_run_scripts_update(tmp_path, "my_app")
    assert result is False


def test_dry_run_scripts_update_never_writes_to_disk(tmp_path: Path) -> None:
    """T007: raw file bytes are identical before and after the call."""
    pyproject = _make_pyproject_with_scripts(tmp_path, "my_app.main:main")
    before = pyproject.read_bytes()
    dry_run_scripts_update(tmp_path, "my_app")
    assert pyproject.read_bytes() == before
