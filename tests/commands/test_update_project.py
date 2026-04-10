"""Tests for up / update-project command (T074)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

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
# Dry-run: prints commands, does NOT call subprocess
# ---------------------------------------------------------------------------


def test_dry_run_exits_0(project_root: Path) -> None:
    with patch("scaffold_ca_python.commands.update_project.subprocess.run") as mock_run:
        result = runner.invoke(app, ["up", "--dry-run"], catch_exceptions=False)
        assert result.exit_code == 0
        mock_run.assert_not_called()


def test_dry_run_prints_uv_lock(project_root: Path) -> None:
    with patch("scaffold_ca_python.commands.update_project.subprocess.run"):
        result = runner.invoke(app, ["up", "--dry-run"], catch_exceptions=False)
        assert "uv lock" in result.output


def test_dry_run_prints_uv_sync(project_root: Path) -> None:
    with patch("scaffold_ca_python.commands.update_project.subprocess.run"):
        result = runner.invoke(app, ["up", "--dry-run"], catch_exceptions=False)
        assert "uv sync" in result.output


# ---------------------------------------------------------------------------
# Success: calls subprocess with correct args (no shell=True)
# ---------------------------------------------------------------------------


def test_success_calls_uv_lock_upgrade(project_root: Path) -> None:
    with patch("scaffold_ca_python.commands.update_project.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        runner.invoke(app, ["up"], catch_exceptions=False)
        calls = mock_run.call_args_list
        first_call_args = calls[0][0][0]
        assert "uv" in first_call_args
        assert "lock" in first_call_args
        assert "--upgrade" in first_call_args


def test_success_calls_uv_sync(project_root: Path) -> None:
    with patch("scaffold_ca_python.commands.update_project.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        runner.invoke(app, ["up"], catch_exceptions=False)
        calls = mock_run.call_args_list
        second_call_args = calls[1][0][0]
        assert "uv" in second_call_args
        assert "sync" in second_call_args


def test_success_does_not_use_shell(project_root: Path) -> None:
    with patch("scaffold_ca_python.commands.update_project.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        runner.invoke(app, ["up"], catch_exceptions=False)
        for call in mock_run.call_args_list:
            assert not call.kwargs.get("shell", False)


def test_success_exits_0(project_root: Path) -> None:
    with patch("scaffold_ca_python.commands.update_project.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        result = runner.invoke(app, ["up"], catch_exceptions=False)
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Error: uv not on PATH
# ---------------------------------------------------------------------------


def test_uv_not_found_exits_1(project_root: Path) -> None:
    with patch(
        "scaffold_ca_python.commands.update_project.subprocess.run",
        side_effect=FileNotFoundError,
    ):
        result = runner.invoke(app, ["up"], catch_exceptions=False)
        assert result.exit_code == 1


def test_uv_not_found_error_message(project_root: Path) -> None:
    with patch(
        "scaffold_ca_python.commands.update_project.subprocess.run",
        side_effect=FileNotFoundError,
    ):
        result = runner.invoke(app, ["up"], catch_exceptions=False)
        assert "uv" in result.output.lower()


# ---------------------------------------------------------------------------
# Error: uv lock fails (non-zero exit)
# ---------------------------------------------------------------------------


def test_uv_lock_failure_exits_2(project_root: Path) -> None:
    import subprocess

    with patch(
        "scaffold_ca_python.commands.update_project.subprocess.run",
        side_effect=subprocess.CalledProcessError(1, ["uv", "lock", "--upgrade"]),
    ):
        result = runner.invoke(app, ["up"], catch_exceptions=False)
        assert result.exit_code == 2


# ---------------------------------------------------------------------------
# Error: no project root
# ---------------------------------------------------------------------------


def test_no_project_root_exits_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["up"], catch_exceptions=False)
    assert result.exit_code == 1


def test_no_project_root_error_message(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["up"], catch_exceptions=False)
    assert "scaffold ca" in result.output.lower()


# ---------------------------------------------------------------------------
# US3: no-args → help (T020)
# ---------------------------------------------------------------------------


def test_up_no_args_exits_0(project_root: Path) -> None:
    with __import__("unittest.mock", fromlist=["patch"]).patch(
        "scaffold_ca_python.commands.update_project.subprocess.run"
    ):
        result = runner.invoke(app, ["up"], catch_exceptions=False)
    assert result.exit_code == 0
