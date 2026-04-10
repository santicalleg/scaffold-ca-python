"""Tests for gep / generate-entry-point command (T050)."""

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
    """Bootstrap a minimal CA project root inside tmp_path."""
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["ca", "--name", "MyApp"], catch_exceptions=False)
    project_dir = tmp_path / "my_app"
    monkeypatch.chdir(project_dir)
    return project_dir


@pytest.fixture()
def swagger_file(tmp_path: Path) -> Path:
    """A minimal valid OpenAPI YAML file for --swagger tests."""
    spec_path = tmp_path / "spec.yaml"
    spec_path.write_text(
        "openapi: '3.0.0'\n"
        "info:\n"
        "  title: Test API\n"
        "  version: '1.0.0'\n"
        "paths:\n"
        "  /users:\n"
        "    get:\n"
        "      summary: List users\n"
        "      responses:\n"
        "        '200':\n"
        "          description: OK\n"
        "  /orders:\n"
        "    post:\n"
        "      summary: Create order\n"
        "      responses:\n"
        "        '201':\n"
        "          description: Created\n"
    )
    return spec_path


# ---------------------------------------------------------------------------
# restapi type
# ---------------------------------------------------------------------------


def test_restapi_creates_init(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "restapi" / "__init__.py"
    ).exists()


def test_restapi_creates_main(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "restapi" / "main.py"
    ).exists()


def test_restapi_creates_router(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "restapi" / "router.py"
    ).exists()


def test_restapi_creates_health(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "restapi" / "health.py"
    ).exists()


def test_restapi_creates_schemas(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "restapi" / "schemas.py"
    ).exists()


def test_restapi_creates_test(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "tests" / "infrastructure" / "entry_points" / "restapi" / "test_router.py"
    ).exists()


def test_restapi_main_contains_fastapi(project_root: Path) -> None:
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    content = (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "restapi" / "main.py"
    ).read_text()
    assert "FastAPI" in content or "fastapi" in content


# ---------------------------------------------------------------------------
# restapi + --swagger
# ---------------------------------------------------------------------------


def test_swagger_injects_routes(project_root: Path, swagger_file: Path) -> None:
    result = runner.invoke(
        app, ["gep", "--type", "restapi", "--swagger", str(swagger_file)],
        catch_exceptions=False,
    )
    assert result.exit_code == 0


def test_swagger_schemas_contains_routes(project_root: Path, swagger_file: Path) -> None:
    runner.invoke(
        app, ["gep", "--type", "restapi", "--swagger", str(swagger_file)],
        catch_exceptions=False,
    )
    content = (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "restapi" / "schemas.py"
    ).read_text()
    # routes from OpenAPI spec should be mentioned
    assert "/users" in content or "/orders" in content or "routes" in content.lower()


# ---------------------------------------------------------------------------
# agent type
# ---------------------------------------------------------------------------


def test_agent_creates_init(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "agent"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "agent" / "__init__.py"
    ).exists()


def test_agent_creates_agent_file(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "agent"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "agent" / "agent.py"
    ).exists()


def test_agent_creates_card_file(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "agent"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "agent" / "card.py"
    ).exists()


def test_agent_creates_test(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "agent"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "tests" / "infrastructure" / "entry_points" / "agent" / "test_agent.py"
    ).exists()


def test_agent_with_enable_kafka(project_root: Path) -> None:
    result = runner.invoke(
        app, ["gep", "--type", "agent", "--enable-kafka"], catch_exceptions=False
    )
    assert result.exit_code == 0
    content = (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "agent" / "agent.py"
    ).read_text()
    assert "kafka" in content.lower() or "Kafka" in content


def test_agent_with_enable_mcp_client(project_root: Path) -> None:
    result = runner.invoke(
        app, ["gep", "--type", "agent", "--enable-mcp-client"], catch_exceptions=False
    )
    assert result.exit_code == 0
    content = (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "agent" / "agent.py"
    ).read_text()
    assert "mcp" in content.lower() or "MCP" in content


# ---------------------------------------------------------------------------
# mcp type
# ---------------------------------------------------------------------------


def test_mcp_creates_init(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "mcp"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root
        / "src"
        / "my_app"
        / "infrastructure"
        / "entry_points"
        / "mcp_server"
        / "__init__.py"
    ).exists()


def test_mcp_creates_server(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "mcp"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root
        / "src"
        / "my_app"
        / "infrastructure"
        / "entry_points"
        / "mcp_server"
        / "server.py"
    ).exists()


def test_mcp_creates_test(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "mcp"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root
        / "tests"
        / "infrastructure"
        / "entry_points"
        / "mcp_server"
        / "test_server.py"
    ).exists()


# ---------------------------------------------------------------------------
# generic type
# ---------------------------------------------------------------------------


def test_generic_creates_init(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "generic"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "generic" / "__init__.py"
    ).exists()


def test_generic_creates_handler(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "generic"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "generic" / "entry_point.py"
    ).exists()


def test_generic_creates_test(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "generic"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "tests" / "infrastructure" / "entry_points" / "generic" / "test_entry_point.py"
    ).exists()


# ---------------------------------------------------------------------------
# Alias
# ---------------------------------------------------------------------------


def test_generate_entry_point_alias_works(project_root: Path) -> None:
    result = runner.invoke(
        app, ["generate-entry-point", "--type", "restapi"], catch_exceptions=False
    )
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------


def test_dry_run_writes_nothing(project_root: Path) -> None:
    result = runner.invoke(
        app, ["gep", "--type", "restapi", "--dry-run"], catch_exceptions=False
    )
    assert result.exit_code == 0
    assert not (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "restapi" / "main.py"
    ).exists()


def test_dry_run_prints_paths(project_root: Path) -> None:
    result = runner.invoke(
        app, ["gep", "--type", "restapi", "--dry-run"], catch_exceptions=False
    )
    assert "restapi" in result.output


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_unknown_type_exits_1(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "graphql"])
    assert result.exit_code == 1
    assert "graphql" in result.output.lower() or "Unknown" in result.output


def test_swagger_without_restapi_exits_1(project_root: Path, swagger_file: Path) -> None:
    result = runner.invoke(
        app, ["gep", "--type", "agent", "--swagger", str(swagger_file)]
    )
    assert result.exit_code == 1
    assert "--swagger" in result.output


def test_swagger_missing_file_exits_1(project_root: Path) -> None:
    result = runner.invoke(
        app, ["gep", "--type", "restapi", "--swagger", "/nonexistent/spec.yaml"]
    )
    assert result.exit_code == 1
    assert "not found" in result.output.lower() or "spec.yaml" in result.output


def test_enable_mcp_client_with_mcp_type_exits_1(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "mcp", "--enable-mcp-client"])
    assert result.exit_code == 1
    assert "--enable-mcp-client" in result.output


def test_duplicate_entry_point_exits_1(project_root: Path) -> None:
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    result = runner.invoke(app, ["gep", "--type", "restapi"])
    assert result.exit_code == 1


def test_no_project_root_exits_1(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["gep", "--type", "restapi"])
    assert result.exit_code == 1


# ---------------------------------------------------------------------------
# US3: main.py overwritten + warning
# ---------------------------------------------------------------------------


def test_restapi_overwrites_main_py(project_root: Path) -> None:
    main_py = project_root / "src" / "my_app" / "main.py"
    assert main_py.exists(), "scaffold ca must create main.py first"
    original = main_py.read_text()
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    updated = main_py.read_text()
    assert updated != original
    assert "uvicorn" in updated


def test_agent_overwrites_main_py(project_root: Path) -> None:
    main_py = project_root / "src" / "my_app" / "main.py"
    runner.invoke(app, ["gep", "--type", "agent"], catch_exceptions=False)
    content = main_py.read_text()
    assert "def main" in content
    assert "asyncio" in content


def test_mcp_overwrites_main_py(project_root: Path) -> None:
    main_py = project_root / "src" / "my_app" / "main.py"
    runner.invoke(app, ["gep", "--type", "mcp"], catch_exceptions=False)
    content = main_py.read_text()
    assert "def main" in content
    assert "asyncio" in content


def test_generic_overwrites_main_py(project_root: Path) -> None:
    main_py = project_root / "src" / "my_app" / "main.py"
    runner.invoke(app, ["gep", "--type", "generic"], catch_exceptions=False)
    content = main_py.read_text()
    assert "def main" in content
    assert "asyncio" in content


def test_gep_prints_main_py_warning(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert "main.py" in result.output


def test_dry_run_does_not_overwrite_main_py(project_root: Path) -> None:
    main_py = project_root / "src" / "my_app" / "main.py"
    original = main_py.read_text()
    runner.invoke(app, ["gep", "--type", "restapi", "--dry-run"], catch_exceptions=False)
    assert main_py.read_text() == original


# ---------------------------------------------------------------------------
# US4: Auto-inject dependencies
# ---------------------------------------------------------------------------


def test_restapi_injects_fastapi_and_uvicorn(project_root: Path) -> None:
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    content = (project_root / "pyproject.toml").read_text()
    assert "fastapi" in content
    assert "uvicorn" in content


def test_agent_injects_a2a_sdk(project_root: Path) -> None:
    runner.invoke(app, ["gep", "--type", "agent"], catch_exceptions=False)
    content = (project_root / "pyproject.toml").read_text()
    assert "a2a-sdk" in content


def test_mcp_injects_mcp(project_root: Path) -> None:
    runner.invoke(app, ["gep", "--type", "mcp"], catch_exceptions=False)
    content = (project_root / "pyproject.toml").read_text()
    assert "mcp" in content


def test_restapi_inject_is_idempotent(project_root: Path) -> None:
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    # Remove both src and test dirs so gep can execute a second time
    import shutil
    shutil.rmtree(project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "restapi")
    shutil.rmtree(project_root / "tests" / "infrastructure" / "entry_points" / "restapi", ignore_errors=True)
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    content = (project_root / "pyproject.toml").read_text()
    assert content.count("fastapi") == 1


def test_dry_run_does_not_inject_deps(project_root: Path) -> None:
    original = (project_root / "pyproject.toml").read_text()
    runner.invoke(app, ["gep", "--type", "restapi", "--dry-run"], catch_exceptions=False)
    assert (project_root / "pyproject.toml").read_text() == original


def test_dry_run_prints_deps_to_inject(project_root: Path) -> None:
    result = runner.invoke(
        app, ["gep", "--type", "restapi", "--dry-run"], catch_exceptions=False
    )
    assert "fastapi" in result.output or "uvicorn" in result.output


# ---------------------------------------------------------------------------
# SC-005 / FR-015: Idempotency integration test (T042)
# ---------------------------------------------------------------------------


def test_gep_restapi_twice_has_exactly_one_fastapi_entry(project_root: Path) -> None:
    """Running gep --type restapi twice must not duplicate fastapi in pyproject.toml."""
    import shutil

    # First run
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    # Remove generated dirs so gep can run again without hitting the duplicate guard
    shutil.rmtree(project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "restapi")
    shutil.rmtree(
        project_root / "tests" / "infrastructure" / "entry_points" / "restapi",
        ignore_errors=True,
    )
    # Second run
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)

    content = (project_root / "pyproject.toml").read_text()
    assert content.count("fastapi") == 1


# ---------------------------------------------------------------------------
# US2: gep --help epilog
# ---------------------------------------------------------------------------


def test_gep_help_shows_type_descriptions() -> None:
    result = runner.invoke(app, ["gep", "--help"])
    assert result.exit_code == 0
    assert "FastAPI" in result.output


def test_gep_help_flags_agent_type_only() -> None:
    result = runner.invoke(app, ["gep", "--help"])
    assert result.exit_code == 0
    assert "agent type only" in result.output


def test_gep_help_contains_examples_section() -> None:
    result = runner.invoke(app, ["gep", "--help"])
    assert result.exit_code == 0
    assert "Examples" in result.output


# ---------------------------------------------------------------------------
# US3: no-args → help (T019)
# ---------------------------------------------------------------------------


def test_gep_no_args_exits_0() -> None:
    result = runner.invoke(app, ["gep"])
    assert result.exit_code == 0


def test_gep_no_args_shows_type_option() -> None:
    result = runner.invoke(app, ["gep"])
    assert "--type" in result.output


# ---------------------------------------------------------------------------
# US3 (feature 008): compatibility guard — T005/T006/T007/T008
# ---------------------------------------------------------------------------


def test_gep_restapi_blocked_when_mcp_server_exists(
    project_root: Path,
) -> None:
    """FR-009: exit 1 when mcp_server/ dir already exists; no api/v1/ created."""
    conflict = project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "mcp_server"
    conflict.mkdir(parents=True)

    result = runner.invoke(app, ["gep", "--type", "restapi"])

    assert result.exit_code == 1
    assert not (project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "api").exists()
    assert "mcp_server" in result.output


def test_gep_restapi_blocked_when_agent_exists(
    project_root: Path,
) -> None:
    """FR-010: exit 1 when agent/ dir already exists; no api/v1/ created."""
    conflict = project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "agent"
    conflict.mkdir(parents=True)

    result = runner.invoke(app, ["gep", "--type", "restapi"])

    assert result.exit_code == 1
    assert not (project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "api").exists()
    assert "agent" in result.output


def test_gep_restapi_proceeds_when_no_incompatible_entry_point(
    project_root: Path,
) -> None:
    """FR-009/FR-010: clean project — guard must NOT block generation."""
    result = runner.invoke(app, ["gep", "--type", "restapi"])

    assert result.exit_code == 0


def test_gep_restapi_dry_run_still_reports_mcp_conflict(
    project_root: Path,
) -> None:
    """FR-013: --dry-run does not bypass the compatibility guard."""
    conflict = project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "mcp_server"
    conflict.mkdir(parents=True)

    result = runner.invoke(app, ["gep", "--type", "restapi", "--dry-run"])

    assert result.exit_code == 1
    assert not (project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "api").exists()
    assert "mcp_server" in result.output
