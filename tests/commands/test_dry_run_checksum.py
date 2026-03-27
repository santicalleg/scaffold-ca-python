"""Checksum-based dry-run verification tests (T090).

For each command, hashes the project directory tree before and after a
--dry-run invocation and asserts the digest is unchanged (SC-007).
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from scaffold_ca_python.cli import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _dir_hash(root: Path) -> str:
    """Stable SHA-256 of all file contents + relative paths under *root*."""
    h = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = str(path.relative_to(root))
            h.update(rel.encode())
            h.update(path.read_bytes())
    return h.hexdigest()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def project_root(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["ca", "--name", "MyApp"], catch_exceptions=False)
    project_dir = tmp_path / "my_app"
    monkeypatch.chdir(project_dir)
    return project_dir


@pytest.fixture()
def project_with_model(project_root: Path) -> Path:
    runner.invoke(app, ["gm", "--name", "Order"], catch_exceptions=False)
    return project_root


# ---------------------------------------------------------------------------
# ca --dry-run
# ---------------------------------------------------------------------------


def test_ca_dry_run_does_not_change_fs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    before = _dir_hash(tmp_path)
    runner.invoke(app, ["ca", "--name", "MyApp", "--dry-run"], catch_exceptions=False)
    after = _dir_hash(tmp_path)
    assert before == after


# ---------------------------------------------------------------------------
# gm --dry-run
# ---------------------------------------------------------------------------


def test_gm_dry_run_does_not_change_fs(project_root: Path) -> None:
    before = _dir_hash(project_root)
    runner.invoke(app, ["gm", "--name", "Product", "--dry-run"], catch_exceptions=False)
    after = _dir_hash(project_root)
    assert before == after


# ---------------------------------------------------------------------------
# guc --dry-run
# ---------------------------------------------------------------------------


def test_guc_dry_run_does_not_change_fs(project_root: Path) -> None:
    before = _dir_hash(project_root)
    runner.invoke(app, ["guc", "--name", "CreateOrder", "--dry-run"], catch_exceptions=False)
    after = _dir_hash(project_root)
    assert before == after


# ---------------------------------------------------------------------------
# gda --dry-run
# ---------------------------------------------------------------------------


def test_gda_dry_run_does_not_change_fs(project_root: Path) -> None:
    before = _dir_hash(project_root)
    runner.invoke(app, ["gda", "--type", "rest-consumer", "--dry-run"], catch_exceptions=False)
    after = _dir_hash(project_root)
    assert before == after


# ---------------------------------------------------------------------------
# gep --dry-run
# ---------------------------------------------------------------------------


def test_gep_dry_run_does_not_change_fs(project_root: Path) -> None:
    before = _dir_hash(project_root)
    runner.invoke(app, ["gep", "--type", "restapi", "--dry-run"], catch_exceptions=False)
    after = _dir_hash(project_root)
    assert before == after


# ---------------------------------------------------------------------------
# gh --dry-run
# ---------------------------------------------------------------------------


def test_gh_dry_run_does_not_change_fs(project_root: Path) -> None:
    before = _dir_hash(project_root)
    runner.invoke(app, ["gh", "--name", "LogHelper", "--dry-run"], catch_exceptions=False)
    after = _dir_hash(project_root)
    assert before == after


# ---------------------------------------------------------------------------
# gpipe --dry-run
# ---------------------------------------------------------------------------


def test_gpipe_dry_run_does_not_change_fs(project_root: Path) -> None:
    before = _dir_hash(project_root)
    runner.invoke(app, ["gpipe", "--provider", "github", "--dry-run"], catch_exceptions=False)
    after = _dir_hash(project_root)
    assert before == after


# ---------------------------------------------------------------------------
# vs --dry-run (read-only command, no-op)
# ---------------------------------------------------------------------------


def test_vs_dry_run_does_not_change_fs(project_root: Path) -> None:
    before = _dir_hash(project_root)
    runner.invoke(app, ["vs", "--dry-run"], catch_exceptions=False)
    after = _dir_hash(project_root)
    assert before == after


# ---------------------------------------------------------------------------
# dm --dry-run (without --confirm)
# ---------------------------------------------------------------------------


def test_dm_dry_run_does_not_change_fs(project_with_model: Path) -> None:
    before = _dir_hash(project_with_model)
    runner.invoke(app, ["dm", "--name", "Order", "--dry-run"], catch_exceptions=False)
    after = _dir_hash(project_with_model)
    assert before == after


# ---------------------------------------------------------------------------
# up --dry-run
# ---------------------------------------------------------------------------


def test_up_dry_run_does_not_change_fs(project_root: Path) -> None:
    before = _dir_hash(project_root)
    with patch("scaffold_ca_python.commands.update_project.subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        runner.invoke(app, ["up", "--dry-run"], catch_exceptions=False)
        mock_run.assert_not_called()
    after = _dir_hash(project_root)
    assert before == after
