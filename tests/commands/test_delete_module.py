"""Tests for dm / delete-module command (T071)."""

from pathlib import Path

import pytest
from typer.testing import CliRunner

from scaffold_ca_python.cli import app
from tests.conftest import strip_ansi

runner = CliRunner()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Bootstrap a minimal CA project root with a model module already created."""
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["ca", "--name", "my-app"], catch_exceptions=False)
    project_dir = tmp_path / "my-app"
    monkeypatch.chdir(project_dir)
    runner.invoke(app, ["gm", "--name", "order"], catch_exceptions=False)
    return project_dir


@pytest.fixture()
def project_root_with_helper(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Bootstrap a CA project root with a helper module already created."""
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["ca", "--name", "my-app"], catch_exceptions=False)
    project_dir = tmp_path / "my-app"
    monkeypatch.chdir(project_dir)
    runner.invoke(app, ["gh", "--name", "log-helper"], catch_exceptions=False)
    return project_dir


# ---------------------------------------------------------------------------
# Default (no --confirm): preview only, no deletions
# ---------------------------------------------------------------------------


def test_default_no_confirm_exits_0(project_root: Path) -> None:
    result = runner.invoke(app, ["dm", "--name", "order"], catch_exceptions=False)
    assert result.exit_code == 0


def test_default_no_confirm_writes_nothing(project_root: Path) -> None:
    model_file = project_root / "src" / "my_app" / "domain" / "model" / "order.py"
    assert model_file.exists()
    runner.invoke(app, ["dm", "--name", "order"], catch_exceptions=False)
    assert model_file.exists()


def test_default_no_confirm_prints_preview(project_root: Path) -> None:
    result = runner.invoke(app, ["dm", "--name", "order"], catch_exceptions=False)
    assert "order" in result.output.lower()
    assert "--confirm" in result.output


# ---------------------------------------------------------------------------
# --dry-run without --confirm: same as default (preview only)
# ---------------------------------------------------------------------------


def test_dry_run_without_confirm_writes_nothing(project_root: Path) -> None:
    model_file = project_root / "src" / "my_app" / "domain" / "model" / "order.py"
    runner.invoke(app, ["dm", "--name", "order", "--dry-run"], catch_exceptions=False)
    assert model_file.exists()


# ---------------------------------------------------------------------------
# --confirm: actually deletes
# ---------------------------------------------------------------------------


def test_confirm_deletes_model_file(project_root: Path) -> None:
    result = runner.invoke(app, ["dm", "--name", "order", "--confirm"], catch_exceptions=False)
    assert result.exit_code == 0
    assert not (project_root / "src" / "my_app" / "domain" / "model" / "order.py").exists()


def test_confirm_deletes_test_file(project_root: Path) -> None:
    runner.invoke(app, ["dm", "--name", "order", "--confirm"], catch_exceptions=False)
    assert not (project_root / "src" / "tests" / "domain" / "model" / "test_order.py").exists()


def test_confirm_prints_deleted(project_root: Path) -> None:
    result = runner.invoke(app, ["dm", "--name", "order", "--confirm"], catch_exceptions=False)
    assert "order" in result.output.lower()


# ---------------------------------------------------------------------------
# --dry-run + --confirm: dry-run takes precedence (preview only)
# ---------------------------------------------------------------------------


def test_dry_run_with_confirm_takes_precedence(project_root: Path) -> None:
    model_file = project_root / "src" / "my_app" / "domain" / "model" / "order.py"
    result = runner.invoke(app, ["dm", "--name", "order", "--confirm", "--dry-run"], catch_exceptions=False)
    assert result.exit_code == 0
    assert model_file.exists()


# ---------------------------------------------------------------------------
# Module in infrastructure/helpers directory (subdirectory, not single file)
# ---------------------------------------------------------------------------


def test_confirm_deletes_helper_dir(project_root_with_helper: Path) -> None:
    result = runner.invoke(app, ["dm", "--name", "log-helper", "--confirm"], catch_exceptions=False)
    assert result.exit_code == 0
    assert not (project_root_with_helper / "src" / "my_app" / "infrastructure" / "helpers" / "log_helper").exists()


def test_confirm_deletes_helper_test_file(project_root_with_helper: Path) -> None:
    runner.invoke(app, ["dm", "--name", "log-helper", "--confirm"], catch_exceptions=False)
    assert not (
        project_root_with_helper / "src" / "tests" / "infrastructure" / "helpers" / "log_helper" / "test_log_helper.py"
    ).exists()


# ---------------------------------------------------------------------------
# Error: module not found
# ---------------------------------------------------------------------------


def test_not_found_exits_1(project_root: Path) -> None:
    result = runner.invoke(app, ["dm", "--name", "ghost"], catch_exceptions=False)
    assert result.exit_code == 1


def test_not_found_error_message(project_root: Path) -> None:
    result = runner.invoke(app, ["dm", "--name", "ghost"], catch_exceptions=False)
    assert "ghost" in result.output.lower()


# ---------------------------------------------------------------------------
# Error: invalid name
# ---------------------------------------------------------------------------


def test_invalid_name_exits_1(project_root: Path) -> None:
    result = runner.invoke(app, ["dm", "--name", "123bad"], catch_exceptions=False)
    assert result.exit_code == 1


def test_invalid_name_error_message(project_root: Path) -> None:
    result = runner.invoke(app, ["dm", "--name", "123bad"], catch_exceptions=False)
    assert "invalid" in result.output.lower()


# ---------------------------------------------------------------------------
# Error: no project root
# ---------------------------------------------------------------------------


def test_no_project_root_exits_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["dm", "--name", "order"], catch_exceptions=False)
    assert result.exit_code == 1


def test_no_project_root_error_message(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["dm", "--name", "order"], catch_exceptions=False)
    assert "scaffold ca" in result.output.lower()


def test_pascal_case_name_exits_1(project_root: Path) -> None:
    result = runner.invoke(app, ["dm", "--name", "InvalidModule"])
    assert result.exit_code == 1
    assert "kebab-case" in result.output


# ---------------------------------------------------------------------------
# US3: no-args → help (T020)
# ---------------------------------------------------------------------------


def test_dm_no_args_exits_0() -> None:
    result = runner.invoke(app, ["dm"])
    assert result.exit_code == 0


def test_dm_no_args_shows_name_option() -> None:
    result = runner.invoke(app, ["dm"])
    print(result.output)
    assert "--name" in strip_ansi(result.output)
