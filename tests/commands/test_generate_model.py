"""Tests for gm / generate-model command (T034)."""

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
    """Bootstrap a minimal CA project root that generate-model can work inside."""
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["ca", "--name", "MyApp"], catch_exceptions=False)
    assert result.exit_code == 0
    project_dir = tmp_path / "my_app"
    monkeypatch.chdir(project_dir)
    return project_dir


# ---------------------------------------------------------------------------
# Success path
# ---------------------------------------------------------------------------

def test_creates_model_file(project_root: Path) -> None:
    result = runner.invoke(app, ["gm", "--name", "Order"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "my_app" / "domain" / "model" / "order.py").exists()


def test_creates_test_mirror(project_root: Path) -> None:
    result = runner.invoke(app, ["gm", "--name", "Order"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "tests" / "domain" / "model" / "test_order.py").exists()


def test_model_file_contains_pydantic_basemodel(project_root: Path) -> None:
    runner.invoke(app, ["gm", "--name", "Product"], catch_exceptions=False)
    content = (project_root / "src" / "my_app" / "domain" / "model" / "product.py").read_text()
    assert "BaseModel" in content
    assert "Product" in content


def test_test_file_contains_pytest_stub(project_root: Path) -> None:
    runner.invoke(app, ["gm", "--name", "Product"], catch_exceptions=False)
    content = (project_root / "tests" / "domain" / "model" / "test_product.py").read_text()
    assert "def test_" in content


def test_generate_model_alias_works(project_root: Path) -> None:
    result = runner.invoke(app, ["generate-model", "--name", "Invoice"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "my_app" / "domain" / "model" / "invoice.py").exists()


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------

def test_dry_run_writes_nothing(project_root: Path) -> None:
    result = runner.invoke(app, ["gm", "--name", "Order", "--dry-run"], catch_exceptions=False)
    assert result.exit_code == 0
    assert not (project_root / "src" / "my_app" / "domain" / "model" / "order.py").exists()


def test_dry_run_prints_paths(project_root: Path) -> None:
    result = runner.invoke(app, ["gm", "--name", "Order", "--dry-run"], catch_exceptions=False)
    assert "order" in result.output.lower()


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

def test_duplicate_model_exits_1(project_root: Path) -> None:
    runner.invoke(app, ["gm", "--name", "Order"], catch_exceptions=False)
    result = runner.invoke(app, ["gm", "--name", "Order"])
    assert result.exit_code == 1


def test_invalid_name_exits_nonzero(project_root: Path) -> None:
    result = runner.invoke(app, ["gm", "--name", "1Bad"])
    assert result.exit_code != 0


def test_no_project_root_exits_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["gm", "--name", "Order"])
    assert result.exit_code == 1
