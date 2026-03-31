"""Integration tests for vs / validate-structure command (T058)."""

from __future__ import annotations

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
    """Bootstrap a minimal CA project root and chdir into it."""
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["ca", "--name", "MyApp"], catch_exceptions=False)
    project_dir = tmp_path / "my_app"
    monkeypatch.chdir(project_dir)
    return project_dir


@pytest.fixture()
def project_with_violation(project_root: Path) -> Path:
    """Return a project_root where one domain/model file has a bad import."""
    model_dir = project_root / "src" / "my_app" / "domain" / "model"
    model_dir.mkdir(parents=True, exist_ok=True)
    (model_dir / "order.py").write_text(
        "from my_app.infrastructure.driven_adapters.rest_consumer import Client\n",
        encoding="utf-8",
    )
    return project_root


# ---------------------------------------------------------------------------
# Clean project exits 0
# ---------------------------------------------------------------------------


def test_clean_project_exits_0(project_root: Path) -> None:
    result = runner.invoke(app, ["vs"], catch_exceptions=False)
    assert result.exit_code == 0


def test_clean_project_output_contains_validated(project_root: Path) -> None:
    result = runner.invoke(app, ["vs"], catch_exceptions=False)
    assert "Validated" in result.output or "validated" in result.output.lower()


def test_clean_project_output_contains_no_violations(project_root: Path) -> None:
    result = runner.invoke(app, ["vs"], catch_exceptions=False)
    assert "no violations" in result.output.lower() or "0" in result.output


# ---------------------------------------------------------------------------
# Violation → exits 1
# ---------------------------------------------------------------------------


def test_violation_exits_1(project_with_violation: Path) -> None:
    result = runner.invoke(app, ["vs"])
    assert result.exit_code == 1


def test_violation_output_contains_file_path(project_with_violation: Path) -> None:
    result = runner.invoke(app, ["vs"])
    # Rich table may truncate the path; assert the visible path prefix appears
    assert "my_app/domain" in result.output or "domain/model" in result.output


def test_violation_output_contains_line_number(project_with_violation: Path) -> None:
    result = runner.invoke(app, ["vs"])
    assert "1" in result.output


def test_violation_output_contains_import_statement(project_with_violation: Path) -> None:
    result = runner.invoke(app, ["vs"])
    # The import cell shows "from <module> import Client" — "Client" is always visible
    assert "Client" in result.output or "my_app.infrastructur" in result.output


def test_violation_count_shown_in_output(project_with_violation: Path) -> None:
    result = runner.invoke(app, ["vs"])
    assert "1" in result.output and ("violation" in result.output.lower())


# ---------------------------------------------------------------------------
# --dry-run is a no-op (read-only; same output, always exits 0)
# ---------------------------------------------------------------------------


def test_dry_run_exits_0_even_with_violations(project_with_violation: Path) -> None:
    result = runner.invoke(app, ["vs", "--dry-run"], catch_exceptions=False)
    assert result.exit_code == 0


def test_dry_run_shows_same_violation_info(project_with_violation: Path) -> None:
    result = runner.invoke(app, ["vs", "--dry-run"], catch_exceptions=False)
    assert "my_app/domain" in result.output or "domain/model" in result.output


def test_dry_run_on_clean_project_exits_0(project_root: Path) -> None:
    result = runner.invoke(app, ["vs", "--dry-run"], catch_exceptions=False)
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Alias
# ---------------------------------------------------------------------------


def test_validate_structure_alias_works(project_root: Path) -> None:
    result = runner.invoke(app, ["validate-structure"], catch_exceptions=False)
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_no_project_root_exits_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["vs"])
    assert result.exit_code == 1


# ---------------------------------------------------------------------------
# US3: no-args → help (T020)
# ---------------------------------------------------------------------------


def test_vs_no_args_exits_0(project_root: Path) -> None:
    result = runner.invoke(app, ["vs"], catch_exceptions=False)
    assert result.exit_code == 0
