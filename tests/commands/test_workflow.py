"""End-to-end workflow tests (T080 + T082).

Covers the full quickstart.md workflow:
  ca → gm → guc → gda → gep → gh → gpipe → vs → dm --confirm → up --dry-run
Every step must exit 0.
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from scaffold_ca_python.cli import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# T080: quickstart.md workflow (ca → gm → guc → gda → gep → gpipe → vs)
# ---------------------------------------------------------------------------


@pytest.fixture()
def workflow_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["ca", "--name", "OrderService"], catch_exceptions=False)
    assert result.exit_code == 0, f"ca failed: {result.output}"
    project_dir = tmp_path / "order_service"
    monkeypatch.chdir(project_dir)
    return project_dir


def test_workflow_ca_creates_project(workflow_root: Path) -> None:
    assert (workflow_root / "pyproject.toml").exists()


def test_workflow_gm_creates_model(workflow_root: Path) -> None:
    result = runner.invoke(app, ["gm", "--name", "Order"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (workflow_root / "src" / "order_service" / "domain" / "model" / "order.py").exists()


def test_workflow_guc_creates_use_case(workflow_root: Path) -> None:
    result = runner.invoke(app, ["guc", "--name", "CreateOrder"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (workflow_root / "src" / "order_service" / "domain" / "usecase" / "create_order.py").exists()


def test_workflow_gda_creates_adapter(workflow_root: Path) -> None:
    result = runner.invoke(app, ["gda", "--type", "rest-consumer"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        workflow_root / "src" / "order_service" / "infrastructure" / "driven_adapters" / "rest_consumer" / "__init__.py"
    ).exists()


def test_workflow_gep_creates_entry_point(workflow_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        workflow_root / "src" / "order_service" / "infrastructure" / "entry_points" / "api" / "v1" / "__init__.py"
    ).exists()


def test_workflow_gpipe_creates_pipeline(workflow_root: Path) -> None:
    result = runner.invoke(app, ["gpipe", "--provider", "github"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (workflow_root / ".github" / "workflows" / "ci.yml").exists()


def test_workflow_vs_exits_0_on_clean_project(workflow_root: Path) -> None:
    result = runner.invoke(app, ["vs"], catch_exceptions=False)
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# T082: Full walkthrough (adds gh, dm --confirm, up --dry-run)
# ---------------------------------------------------------------------------


@pytest.fixture()
def full_walkthrough_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["ca", "--name", "MyApp"], catch_exceptions=False)
    project_dir = tmp_path / "my_app"
    monkeypatch.chdir(project_dir)
    return project_dir


def test_full_walkthrough_complete(full_walkthrough_root: Path) -> None:
    steps = [
        (["gm", "--name", "Product"], "gm"),
        (["guc", "--name", "CreateProduct"], "guc"),
        (["gda", "--type", "rest-consumer"], "gda"),
        (["gep", "--type", "restapi"], "gep"),
        (["gh", "--name", "LogHelper"], "gh"),
        (["gpipe", "--provider", "azure"], "gpipe"),
        (["vs"], "vs"),
        (["dm", "--name", "Product", "--confirm"], "dm"),
    ]
    for args, label in steps:
        result = runner.invoke(app, args, catch_exceptions=False)
        assert result.exit_code == 0, f"Step '{label}' failed:\n{result.output}"

    # up --dry-run: patch subprocess to avoid actually calling uv
    with patch("scaffold_ca_python.commands.update_project.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = runner.invoke(app, ["up", "--dry-run"], catch_exceptions=False)
        assert result.exit_code == 0, f"up --dry-run failed:\n{result.output}"
        mock_run.assert_not_called()
