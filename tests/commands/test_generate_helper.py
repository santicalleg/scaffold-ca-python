"""Tests for gh / generate-helper command (T062)."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from scaffold_ca_python.cli import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Bootstrap a minimal CA project root inside tmp_path."""
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["ca", "--name", "MyApp"], catch_exceptions=False)
    project_dir = tmp_path / "my_app"
    monkeypatch.chdir(project_dir)
    return project_dir


# ---------------------------------------------------------------------------
# Success path: creates all three files
# ---------------------------------------------------------------------------


def test_creates_init(project_root: Path) -> None:
    result = runner.invoke(app, ["gh", "--name", "DateUtils"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "my_app" / "infrastructure" / "helpers" / "date_utils" / "__init__.py").exists()


def test_creates_implementation_file(project_root: Path) -> None:
    result = runner.invoke(app, ["gh", "--name", "DateUtils"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "my_app" / "infrastructure" / "helpers" / "date_utils" / "date_utils.py").exists()


def test_creates_test_file(project_root: Path) -> None:
    result = runner.invoke(app, ["gh", "--name", "DateUtils"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "tests" / "infrastructure" / "helpers" / "date_utils" / "test_date_utils.py").exists()


def test_implementation_contains_class(project_root: Path) -> None:
    runner.invoke(app, ["gh", "--name", "DateUtils"], catch_exceptions=False)
    impl = (project_root / "src" / "my_app" / "infrastructure" / "helpers" / "date_utils" / "date_utils.py").read_text()
    assert "class DateUtils" in impl


def test_test_file_imports_class(project_root: Path) -> None:
    runner.invoke(app, ["gh", "--name", "DateUtils"], catch_exceptions=False)
    test_src = (project_root / "tests" / "infrastructure" / "helpers" / "date_utils" / "test_date_utils.py").read_text()
    assert "DateUtils" in test_src


def test_success_exit_code(project_root: Path) -> None:
    result = runner.invoke(app, ["gh", "--name", "LogHelper"], catch_exceptions=False)
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Dry-run: prints file paths, writes nothing
# ---------------------------------------------------------------------------


def test_dry_run_writes_nothing(project_root: Path) -> None:
    result = runner.invoke(app, ["gh", "--name", "DateUtils", "--dry-run"], catch_exceptions=False)
    assert result.exit_code == 0
    assert not (project_root / "src" / "my_app" / "infrastructure" / "helpers" / "date_utils").exists()


def test_dry_run_prints_paths(project_root: Path) -> None:
    result = runner.invoke(app, ["gh", "--name", "DateUtils", "--dry-run"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "date_utils" in result.output


# ---------------------------------------------------------------------------
# Duplicate guard
# ---------------------------------------------------------------------------


def test_duplicate_exits_1(project_root: Path) -> None:
    runner.invoke(app, ["gh", "--name", "DateUtils"], catch_exceptions=False)
    result = runner.invoke(app, ["gh", "--name", "DateUtils"], catch_exceptions=False)
    assert result.exit_code == 1


def test_duplicate_error_message(project_root: Path) -> None:
    runner.invoke(app, ["gh", "--name", "DateUtils"], catch_exceptions=False)
    result = runner.invoke(app, ["gh", "--name", "DateUtils"], catch_exceptions=False)
    assert "already exists" in result.output


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------


def test_invalid_name_exits_1(project_root: Path) -> None:
    result = runner.invoke(app, ["gh", "--name", "123bad"], catch_exceptions=False)
    assert result.exit_code == 1


def test_invalid_name_error_message(project_root: Path) -> None:
    result = runner.invoke(app, ["gh", "--name", "123bad"], catch_exceptions=False)
    assert "invalid" in result.output.lower()


def test_no_project_root_exits_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["gh", "--name", "MyHelper"], catch_exceptions=False)
    assert result.exit_code == 1


def test_no_project_root_error_message(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["gh", "--name", "MyHelper"], catch_exceptions=False)
    assert "scaffold ca" in result.output.lower()


# ---------------------------------------------------------------------------
# US3: no-args → help (T020)
# ---------------------------------------------------------------------------


def test_gh_no_args_exits_0() -> None:
    result = runner.invoke(app, ["gh"])
    assert result.exit_code == 0


def test_gh_no_args_shows_name_option() -> None:
    result = runner.invoke(app, ["gh"])
    assert "--name" in result.output
