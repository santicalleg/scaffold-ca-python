"""Tests for gpipe / generate-pipeline command (T066)."""

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
# github provider
# ---------------------------------------------------------------------------


def test_github_creates_workflow_file(project_root: Path) -> None:
    result = runner.invoke(app, ["gpipe", "--provider", "github"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / ".github" / "workflows" / "ci.yml").exists()


def test_github_workflow_contains_ruff(project_root: Path) -> None:
    runner.invoke(app, ["gpipe", "--provider", "github"], catch_exceptions=False)
    content = (project_root / ".github" / "workflows" / "ci.yml").read_text()
    assert "ruff" in content


def test_github_workflow_contains_mypy(project_root: Path) -> None:
    runner.invoke(app, ["gpipe", "--provider", "github"], catch_exceptions=False)
    content = (project_root / ".github" / "workflows" / "ci.yml").read_text()
    assert "mypy" in content


def test_github_workflow_contains_pytest(project_root: Path) -> None:
    runner.invoke(app, ["gpipe", "--provider", "github"], catch_exceptions=False)
    content = (project_root / ".github" / "workflows" / "ci.yml").read_text()
    assert "pytest" in content


# ---------------------------------------------------------------------------
# azure provider
# ---------------------------------------------------------------------------


def test_azure_creates_pipeline_file(project_root: Path) -> None:
    result = runner.invoke(app, ["gpipe", "--provider", "azure"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "azure-pipelines.yml").exists()


def test_azure_pipeline_contains_ruff(project_root: Path) -> None:
    runner.invoke(app, ["gpipe", "--provider", "azure"], catch_exceptions=False)
    content = (project_root / "azure-pipelines.yml").read_text()
    assert "ruff" in content


def test_azure_pipeline_contains_mypy(project_root: Path) -> None:
    runner.invoke(app, ["gpipe", "--provider", "azure"], catch_exceptions=False)
    content = (project_root / "azure-pipelines.yml").read_text()
    assert "mypy" in content


def test_azure_pipeline_contains_pytest(project_root: Path) -> None:
    runner.invoke(app, ["gpipe", "--provider", "azure"], catch_exceptions=False)
    content = (project_root / "azure-pipelines.yml").read_text()
    assert "pytest" in content


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------


def test_dry_run_github_writes_nothing(project_root: Path) -> None:
    result = runner.invoke(
        app, ["gpipe", "--provider", "github", "--dry-run"], catch_exceptions=False
    )
    assert result.exit_code == 0
    assert not (project_root / ".github" / "workflows" / "ci.yml").exists()


def test_dry_run_github_prints_path(project_root: Path) -> None:
    result = runner.invoke(
        app, ["gpipe", "--provider", "github", "--dry-run"], catch_exceptions=False
    )
    assert result.exit_code == 0
    assert "ci.yml" in result.output


def test_dry_run_azure_writes_nothing(project_root: Path) -> None:
    result = runner.invoke(
        app, ["gpipe", "--provider", "azure", "--dry-run"], catch_exceptions=False
    )
    assert result.exit_code == 0
    assert not (project_root / "azure-pipelines.yml").exists()


# ---------------------------------------------------------------------------
# Validation errors
# ---------------------------------------------------------------------------


def test_missing_provider_exits_1(project_root: Path) -> None:
    result = runner.invoke(app, ["gpipe"], catch_exceptions=False)
    assert result.exit_code == 1


def test_missing_provider_error_hints_providers(project_root: Path) -> None:
    result = runner.invoke(app, ["gpipe"], catch_exceptions=False)
    assert "github" in result.output
    assert "azure" in result.output


def test_unknown_provider_exits_1(project_root: Path) -> None:
    result = runner.invoke(app, ["gpipe", "--provider", "jenkins"], catch_exceptions=False)
    assert result.exit_code == 1


def test_unknown_provider_error_message(project_root: Path) -> None:
    result = runner.invoke(app, ["gpipe", "--provider", "jenkins"], catch_exceptions=False)
    assert "jenkins" in result.output.lower()


def test_duplicate_github_exits_1(project_root: Path) -> None:
    runner.invoke(app, ["gpipe", "--provider", "github"], catch_exceptions=False)
    result = runner.invoke(app, ["gpipe", "--provider", "github"], catch_exceptions=False)
    assert result.exit_code == 1


def test_duplicate_github_error_message(project_root: Path) -> None:
    runner.invoke(app, ["gpipe", "--provider", "github"], catch_exceptions=False)
    result = runner.invoke(app, ["gpipe", "--provider", "github"], catch_exceptions=False)
    assert "already exists" in result.output


def test_no_project_root_exits_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["gpipe", "--provider", "github"], catch_exceptions=False)
    assert result.exit_code == 1


def test_no_project_root_error_message(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["gpipe", "--provider", "github"], catch_exceptions=False)
    assert "scaffold ca" in result.output.lower()


# ---------------------------------------------------------------------------
# US2: gpipe --help epilog
# ---------------------------------------------------------------------------


def test_gpipe_help_shows_provider_descriptions() -> None:
    result = runner.invoke(app, ["gpipe", "--help"])
    assert result.exit_code == 0
    assert "GitHub Actions" in result.output


def test_gpipe_help_notes_provider_required() -> None:
    result = runner.invoke(app, ["gpipe", "--help"])
    assert result.exit_code == 0
    assert "--provider is required" in result.output


def test_gpipe_help_contains_examples_section() -> None:
    result = runner.invoke(app, ["gpipe", "--help"])
    assert result.exit_code == 0
    assert "Examples" in result.output
