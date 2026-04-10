"""Tests for gda / generate-driven-adapter command (T044)."""

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
# rest-consumer type
# ---------------------------------------------------------------------------


def test_rest_consumer_creates_init(project_root: Path) -> None:
    result = runner.invoke(app, ["gda", "--type", "rest-consumer"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "my_app" / "infrastructure" / "driven_adapters" / "rest_consumer" / "__init__.py"
    ).exists()


def test_rest_consumer_creates_impl(project_root: Path) -> None:
    result = runner.invoke(app, ["gda", "--type", "rest-consumer"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "my_app" / "infrastructure" / "driven_adapters" / "rest_consumer" / "rest_consumer.py"
    ).exists()


def test_rest_consumer_creates_test(project_root: Path) -> None:
    result = runner.invoke(app, ["gda", "--type", "rest-consumer"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "tests" / "infrastructure" / "driven_adapters" / "rest_consumer" / "test_rest_consumer.py"
    ).exists()


def test_rest_consumer_impl_contains_httpx(project_root: Path) -> None:
    runner.invoke(app, ["gda", "--type", "rest-consumer"], catch_exceptions=False)
    content = (
        project_root / "src" / "my_app" / "infrastructure" / "driven_adapters" / "rest_consumer" / "rest_consumer.py"
    ).read_text()
    assert "httpx" in content


# ---------------------------------------------------------------------------
# secrets type
# ---------------------------------------------------------------------------


def test_secrets_creates_init(project_root: Path) -> None:
    result = runner.invoke(app, ["gda", "--type", "secrets"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "my_app" / "infrastructure" / "driven_adapters" / "secrets" / "__init__.py").exists()


def test_secrets_creates_impl(project_root: Path) -> None:
    result = runner.invoke(app, ["gda", "--type", "secrets"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "my_app" / "infrastructure" / "driven_adapters" / "secrets" / "secrets_adapter.py"
    ).exists()


def test_secrets_creates_test(project_root: Path) -> None:
    result = runner.invoke(app, ["gda", "--type", "secrets"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "tests" / "infrastructure" / "driven_adapters" / "secrets" / "test_secrets_adapter.py"
    ).exists()


# ---------------------------------------------------------------------------
# generic type
# ---------------------------------------------------------------------------


def test_generic_creates_init(project_root: Path) -> None:
    result = runner.invoke(app, ["gda", "--type", "generic", "--name", "CacheStore"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "my_app" / "infrastructure" / "driven_adapters" / "cache_store" / "__init__.py"
    ).exists()


def test_generic_creates_impl(project_root: Path) -> None:
    result = runner.invoke(app, ["gda", "--type", "generic", "--name", "CacheStore"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root
        / "src"
        / "my_app"
        / "infrastructure"
        / "driven_adapters"
        / "cache_store"
        / "cache_store_adapter.py"
    ).exists()


def test_generic_creates_test(project_root: Path) -> None:
    result = runner.invoke(app, ["gda", "--type", "generic", "--name", "CacheStore"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "tests" / "infrastructure" / "driven_adapters" / "cache_store" / "test_cache_store_adapter.py"
    ).exists()


def test_generic_impl_contains_class_name(project_root: Path) -> None:
    runner.invoke(app, ["gda", "--type", "generic", "--name", "CacheStore"], catch_exceptions=False)
    content = (
        project_root
        / "src"
        / "my_app"
        / "infrastructure"
        / "driven_adapters"
        / "cache_store"
        / "cache_store_adapter.py"
    ).read_text()
    assert "CacheStore" in content


# ---------------------------------------------------------------------------
# Alias
# ---------------------------------------------------------------------------


def test_generate_driven_adapter_alias_works(project_root: Path) -> None:
    result = runner.invoke(app, ["generate-driven-adapter", "--type", "rest-consumer"], catch_exceptions=False)
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------


def test_dry_run_writes_nothing_rest_consumer(project_root: Path) -> None:
    result = runner.invoke(app, ["gda", "--type", "rest-consumer", "--dry-run"], catch_exceptions=False)
    assert result.exit_code == 0
    assert not (
        project_root / "src" / "my_app" / "infrastructure" / "driven_adapters" / "rest_consumer" / "rest_consumer.py"
    ).exists()


def test_dry_run_prints_paths(project_root: Path) -> None:
    result = runner.invoke(app, ["gda", "--type", "rest-consumer", "--dry-run"], catch_exceptions=False)
    assert "rest_consumer" in result.output


def test_dry_run_generic_writes_nothing(project_root: Path) -> None:
    result = runner.invoke(
        app,
        ["gda", "--type", "generic", "--name", "CacheStore", "--dry-run"],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    assert not (
        project_root
        / "src"
        / "my_app"
        / "infrastructure"
        / "driven_adapters"
        / "cache_store"
        / "cache_store_adapter.py"
    ).exists()


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_generic_without_name_exits_1(project_root: Path) -> None:
    result = runner.invoke(app, ["gda", "--type", "generic"])
    assert result.exit_code == 1
    assert "--name" in result.output


def test_unknown_type_exits_1(project_root: Path) -> None:
    result = runner.invoke(app, ["gda", "--type", "kafka"])
    assert result.exit_code == 1
    assert "kafka" in result.output.lower() or "Unknown" in result.output


def test_duplicate_adapter_dir_exits_1(project_root: Path) -> None:
    runner.invoke(app, ["gda", "--type", "rest-consumer"], catch_exceptions=False)
    result = runner.invoke(app, ["gda", "--type", "rest-consumer"])
    assert result.exit_code == 1


def test_invalid_name_exits_1(project_root: Path) -> None:
    result = runner.invoke(app, ["gda", "--type", "generic", "--name", "2bad"])
    assert result.exit_code != 0


def test_no_project_root_exits_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["gda", "--type", "rest-consumer"])
    assert result.exit_code == 1


# ---------------------------------------------------------------------------
# US4: Auto-inject dependencies
# ---------------------------------------------------------------------------


def test_rest_consumer_injects_httpx(project_root: Path) -> None:
    runner.invoke(app, ["gda", "--type", "rest-consumer"], catch_exceptions=False)
    content = (project_root / "pyproject.toml").read_text()
    assert "httpx" in content


def test_secrets_injects_boto3(project_root: Path) -> None:
    runner.invoke(app, ["gda", "--type", "secrets"], catch_exceptions=False)
    content = (project_root / "pyproject.toml").read_text()
    assert "boto3" in content


def test_generic_injects_nothing(project_root: Path) -> None:
    original = (project_root / "pyproject.toml").read_text()
    runner.invoke(app, ["gda", "--type", "generic", "--name", "CacheStore"], catch_exceptions=False)
    assert (project_root / "pyproject.toml").read_text() == original


def test_rest_consumer_inject_is_idempotent(project_root: Path) -> None:
    runner.invoke(app, ["gda", "--type", "rest-consumer"], catch_exceptions=False)
    import shutil

    shutil.rmtree(project_root / "src" / "my_app" / "infrastructure" / "driven_adapters" / "rest_consumer")
    shutil.rmtree(
        project_root / "tests" / "infrastructure" / "driven_adapters" / "rest_consumer",
        ignore_errors=True,
    )
    runner.invoke(app, ["gda", "--type", "rest-consumer"], catch_exceptions=False)
    content = (project_root / "pyproject.toml").read_text()
    assert content.count("httpx") == 1


def test_dry_run_does_not_inject_deps(project_root: Path) -> None:
    original = (project_root / "pyproject.toml").read_text()
    runner.invoke(app, ["gda", "--type", "rest-consumer", "--dry-run"], catch_exceptions=False)
    assert (project_root / "pyproject.toml").read_text() == original


def test_dry_run_prints_deps_to_inject(project_root: Path) -> None:
    result = runner.invoke(app, ["gda", "--type", "rest-consumer", "--dry-run"], catch_exceptions=False)
    assert "httpx" in result.output


# ---------------------------------------------------------------------------
# US2: gda --help epilog
# ---------------------------------------------------------------------------


def test_gda_help_shows_type_descriptions() -> None:
    result = runner.invoke(app, ["gda", "--help"])
    assert result.exit_code == 0
    assert "httpx" in result.output


def test_gda_help_notes_name_required_for_generic() -> None:
    result = runner.invoke(app, ["gda", "--help"])
    assert result.exit_code == 0
    assert "--name required" in result.output


def test_gda_help_contains_custom_adapter_description() -> None:
    result = runner.invoke(app, ["gda", "--help"])
    assert result.exit_code == 0
    assert "Custom adapter" in result.output


# ---------------------------------------------------------------------------
# US3: no-args → help (T019)
# ---------------------------------------------------------------------------


def test_gda_no_args_exits_0() -> None:
    result = runner.invoke(app, ["gda"])
    assert result.exit_code == 0


def test_gda_no_args_shows_type_option() -> None:
    result = runner.invoke(app, ["gda"])
    assert "--type" in result.output
