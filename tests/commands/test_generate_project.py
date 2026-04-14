"""Tests for ca / generate-project command (T025)."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from scaffold_ca_python.cli import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# Success path
# ---------------------------------------------------------------------------


def test_creates_project_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["ca", "--name", "MyProject"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (tmp_path / "my_project").is_dir()


def test_creates_all_layer_directories(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["ca", "--name", "MyProject"], catch_exceptions=False)
    assert result.exit_code == 0
    root = tmp_path / "my_project"
    assert (root / "src" / "my_project" / "application" / "__init__.py").exists()
    assert (root / "src" / "my_project" / "domain" / "model" / "__init__.py").exists()
    assert (root / "src" / "my_project" / "domain" / "usecase" / "__init__.py").exists()
    assert (root / "src" / "my_project" / "infrastructure" / "driven_adapters" / "__init__.py").exists()
    assert (root / "src" / "my_project" / "infrastructure" / "entry_points" / "__init__.py").exists()
    assert (root / "src" / "my_project" / "infrastructure" / "helpers" / "__init__.py").exists()


def test_creates_config_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["ca", "--name", "MyProject"], catch_exceptions=False)
    assert result.exit_code == 0
    root = tmp_path / "my_project"
    assert (root / "pyproject.toml").exists()
    assert (root / "README.md").exists()
    assert (root / ".gitignore").exists()
    assert (root / "mypy.ini").exists()
    # US1: Docker and Python version files
    assert (root / "Dockerfile").exists()
    assert (root / ".dockerignore").exists()
    assert (root / ".python-version").exists()
    # US1: No .ruff.toml
    assert not (root / ".ruff.toml").exists()


def test_python_version_file_contains_version(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["ca", "--name", "MyProject"], catch_exceptions=False)
    content = (tmp_path / "my_project" / ".python-version").read_text()
    assert "3.13" in content


def test_pyproject_has_ruff_lint_section(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["ca", "--name", "MyProject"], catch_exceptions=False)
    content = (tmp_path / "my_project" / "pyproject.toml").read_text()
    assert "[tool.ruff.lint]" in content


def test_creates_di_config_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["ca", "--name", "MyProject"], catch_exceptions=False)
    assert result.exit_code == 0
    cfg = tmp_path / "my_project" / "src" / "my_project" / "application" / "config"
    assert (cfg / "__init__.py").exists()
    assert (cfg / "config.py").exists()
    assert (cfg / "driven_adapters_container.py").exists()
    assert (cfg / "usecases_container.py").exists()
    assert (cfg / "container.py").exists()


def test_pyproject_has_di_dependencies(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["ca", "--name", "MyProject"], catch_exceptions=False)
    content = (tmp_path / "my_project" / "pyproject.toml").read_text()
    assert "dependency-injector" in content
    assert "pydantic-settings" in content


def test_creates_main_py(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["ca", "--name", "MyProject"], catch_exceptions=False)
    assert result.exit_code == 0
    main_py = tmp_path / "my_project" / "src" / "my_project" / "main.py"
    assert main_py.exists()
    content = main_py.read_text()
    assert "def main" in content


def test_pyproject_has_scripts_entry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["ca", "--name", "MyProject"], catch_exceptions=False)
    content = (tmp_path / "my_project" / "pyproject.toml").read_text()
    assert "[project.scripts]" in content
    assert "my_project.main:main" in content


def test_pyproject_contains_scaffold_section(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["ca", "--name", "MyProject"], catch_exceptions=False)
    content = (tmp_path / "my_project" / "pyproject.toml").read_text()
    assert "[tool.scaffold-ca-python]" in content
    assert "MyProject" in content


def test_package_flag_is_not_accepted(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["ca", "--name", "SimpleApp", "--package", "com.example"])
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# US1: clean-architecture command (T003)
# ---------------------------------------------------------------------------


def test_clean_architecture_creates_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["clean-architecture", "--name", "Demo"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (tmp_path / "demo").is_dir()


def test_clean_architecture_dry_run(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["clean-architecture", "--dry-run", "--name", "Demo"], catch_exceptions=False)
    assert result.exit_code == 0
    assert not (tmp_path / "demo").exists()


def test_clean_architecture_help_contains_options() -> None:
    result = runner.invoke(app, ["clean-architecture", "--help"])
    assert result.exit_code == 0
    assert "--name" in result.output
    assert "--dry-run" in result.output


def test_ca_help_identical_to_clean_architecture_help() -> None:
    """SC-004: ca --help must match clean-architecture --help in all content.

    The Usage line inherently shows the invoked command name (Typer behaviour),
    so we normalise that line before comparing.
    """
    r_ca = runner.invoke(app, ["ca", "--help"])
    r_clean = runner.invoke(app, ["clean-architecture", "--help"])

    def _normalise(output: str) -> str:
        lines = output.splitlines()
        return "\n".join(
            line.replace(" ca ", " <CMD> ").replace(" clean-architecture ", " <CMD> ").rstrip()
            if "Usage:" in line
            else line.rstrip()
            for line in lines
        )

    assert _normalise(r_ca.output) == _normalise(r_clean.output)


# ---------------------------------------------------------------------------
# US1: ca alias and generate-project tombstone (T004)
# ---------------------------------------------------------------------------


def test_ca_alias_creates_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["ca", "--name", "Demo"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (tmp_path / "demo").is_dir()


def test_generate_project_tombstone_exits_1() -> None:
    result = runner.invoke(app, ["generate-project", "--name", "Demo"])
    assert result.exit_code == 1
    assert "clean-architecture" in result.output


def test_generate_project_tombstone_exits_1_no_args() -> None:
    result = runner.invoke(app, ["generate-project"])
    assert result.exit_code == 1
    assert "clean-architecture" in result.output


def test_creates_tests_init(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["ca", "--name", "MyProject"], catch_exceptions=False)
    assert (tmp_path / "my_project" / "src" / "tests" / "__init__.py").exists()


def test_ca_creates_src_tests_init(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["ca", "--name", "MyProject"], catch_exceptions=False)
    assert (tmp_path / "my_project" / "src" / "tests" / "__init__.py").exists()
    assert not (tmp_path / "my_project" / "tests").exists()


def test_ca_dry_run_shows_src_tests_init(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["ca", "--name", "MyProject", "--dry-run"], catch_exceptions=False)
    assert "src/tests/__init__.py" in result.output
    assert result.output.count("tests/__init__.py") == result.output.count("src/tests/__init__.py")


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------


def test_dry_run_writes_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["ca", "--name", "DryProject", "--dry-run"], catch_exceptions=False)
    assert result.exit_code == 0
    assert not (tmp_path / "dry_project").exists()


def test_dry_run_prints_file_list(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["ca", "--name", "DryProject", "--dry-run"], catch_exceptions=False)
    assert "pyproject.toml" in result.output or "dry_project" in result.output


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_duplicate_project_exits_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["ca", "--name", "MyProject"], catch_exceptions=False)
    result = runner.invoke(app, ["ca", "--name", "MyProject"])
    assert result.exit_code == 1


def test_invalid_name_exits_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["ca", "--name", "1InvalidName"])
    assert result.exit_code != 0


def test_hyphen_in_name_exits_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["ca", "--name", "my-project"])
    assert result.exit_code != 0
