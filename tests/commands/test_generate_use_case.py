"""Tests for guc / generate-use-case command (T039)."""

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
    """Bootstrap a minimal CA project root that generate-use-case can work inside."""
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["ca", "--name", "MyApp"], catch_exceptions=False)
    project_dir = tmp_path / "my_app"
    monkeypatch.chdir(project_dir)
    return project_dir


# ---------------------------------------------------------------------------
# Success path
# ---------------------------------------------------------------------------

def test_creates_use_case_file(project_root: Path) -> None:
    result = runner.invoke(app, ["guc", "--name", "CreateOrder"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "my_app" / "domain" / "usecase" / "create_order.py").exists()


def test_creates_test_mirror(project_root: Path) -> None:
    result = runner.invoke(app, ["guc", "--name", "CreateOrder"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "tests" / "domain" / "usecase" / "test_create_order.py").exists()


def test_use_case_file_contains_async_execute(project_root: Path) -> None:
    runner.invoke(app, ["guc", "--name", "PlaceOrder"], catch_exceptions=False)
    content = (project_root / "src" / "my_app" / "domain" / "usecase" / "place_order.py").read_text()
    assert "async def execute" in content


def test_use_case_file_contains_class(project_root: Path) -> None:
    runner.invoke(app, ["guc", "--name", "PlaceOrder"], catch_exceptions=False)
    content = (project_root / "src" / "my_app" / "domain" / "usecase" / "place_order.py").read_text()
    assert "PlaceOrder" in content


def test_test_file_contains_pytest_stub(project_root: Path) -> None:
    runner.invoke(app, ["guc", "--name", "PlaceOrder"], catch_exceptions=False)
    content = (project_root / "tests" / "domain" / "usecase" / "test_place_order.py").read_text()
    assert "def test_" in content


def test_generate_use_case_alias_works(project_root: Path) -> None:
    result = runner.invoke(app, ["generate-use-case", "--name", "CancelOrder"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "my_app" / "domain" / "usecase" / "cancel_order.py").exists()


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------

def test_dry_run_writes_nothing(project_root: Path) -> None:
    result = runner.invoke(app, ["guc", "--name", "CreateOrder", "--dry-run"], catch_exceptions=False)
    assert result.exit_code == 0
    assert not (project_root / "src" / "my_app" / "domain" / "usecase" / "create_order.py").exists()


def test_dry_run_prints_paths(project_root: Path) -> None:
    result = runner.invoke(app, ["guc", "--name", "CreateOrder", "--dry-run"], catch_exceptions=False)
    assert "create_order" in result.output.lower()


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_duplicate_use_case_exits_1(project_root: Path) -> None:
    runner.invoke(app, ["guc", "--name", "CreateOrder"], catch_exceptions=False)
    result = runner.invoke(app, ["guc", "--name", "CreateOrder"])
    assert result.exit_code == 1


def test_invalid_name_exits_nonzero(project_root: Path) -> None:
    result = runner.invoke(app, ["guc", "--name", "2Bad"])
    assert result.exit_code != 0


def test_no_project_root_exits_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["guc", "--name", "CreateOrder"])
    assert result.exit_code == 1
