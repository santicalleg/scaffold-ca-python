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
    runner.invoke(app, ["ca", "--name", "my-app"], catch_exceptions=False)
    project_dir = tmp_path / "my-app"
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


# ---------------------------------------------------------------------------
# US1 — application/app.py emitted (T002)
# ---------------------------------------------------------------------------


def test_restapi_creates_app_py(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "my_app" / "application" / "app.py").exists()


# ---------------------------------------------------------------------------
# US2 — server.py is thin wrapper (T010)
# ---------------------------------------------------------------------------


def test_restapi_server_py_is_thin_wrapper(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert result.exit_code == 0
    content = (project_root / "src" / "my_app" / "server.py").read_text()
    assert "FastAPI" not in content
    meaningful_lines = [ln for ln in content.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    assert len(meaningful_lines) <= 5


# ---------------------------------------------------------------------------
# US3 — no main.py emitted for restapi (T015, T016, T016c)
# ---------------------------------------------------------------------------


def test_restapi_no_main_py(project_root: Path) -> None:
    # main.py is created by scaffold ca; gep --type restapi must not create it if absent
    (project_root / "src" / "my_app" / "main.py").unlink(missing_ok=True)
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert not (project_root / "src" / "my_app" / "main.py").exists()


def test_restapi_dry_run_includes_app_py_not_main(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi", "--dry-run"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "app.py" in result.output
    # main.py must not appear as a *created* file — it appears as a deletion notice (FR-004)
    assert "Would delete" in result.output
    # dry-run must NOT actually delete the file
    assert (project_root / "src" / "my_app" / "main.py").exists()


def test_restapi_gep_twice_does_not_overwrite_app_py(project_root: Path) -> None:
    import shutil

    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    app_py = project_root / "src" / "my_app" / "application" / "app.py"
    original_content = app_py.read_text()

    # Clean up so gep can run a second time
    shutil.rmtree(project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "api")
    shutil.rmtree(project_root / "src" / "tests" / "infrastructure" / "entry_points" / "api", ignore_errors=True)
    (project_root / "src" / "my_app" / "server.py").unlink(missing_ok=True)
    (project_root / "src" / "tests" / "application" / "test_app.py").unlink(missing_ok=True)
    app_py.unlink(missing_ok=True)

    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert app_py.read_text() == original_content


# ---------------------------------------------------------------------------
# US4 — test files emitted by gep --type restapi (T018–T021)
# ---------------------------------------------------------------------------


def test_restapi_creates_test_app(project_root: Path) -> None:
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert (project_root / "src" / "tests" / "application" / "test_app.py").exists()


def test_restapi_creates_test_server(project_root: Path) -> None:
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert (
        project_root / "src" / "tests" / "infrastructure" / "entry_points" / "api" / "v1" / "test_server.py"
    ).exists()


def test_restapi_creates_test_exception_handler(project_root: Path) -> None:
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert (
        project_root / "src" / "tests" / "infrastructure" / "entry_points" / "api" / "v1" / "test_exception_handler.py"
    ).exists()


# ---------------------------------------------------------------------------
# Existing file-existence tests
# ---------------------------------------------------------------------------


def test_restapi_creates_init(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "api" / "v1" / "__init__.py").exists()


def test_restapi_creates_rest_controller(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "api" / "v1" / "rest_controller.py"
    ).exists()


def test_restapi_creates_exception_handler(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "api" / "v1" / "exception_handler.py"
    ).exists()


def test_restapi_creates_server_py(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "my_app" / "server.py").exists()


def test_restapi_creates_test(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "tests" / "infrastructure" / "entry_points" / "api" / "v1" / "test_rest_controller.py"
    ).exists()


def test_restapi_main_contains_fastapi(project_root: Path) -> None:
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    content = (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "api" / "v1" / "rest_controller.py"
    ).read_text()
    assert "FastAPI" in content or "APIRouter" in content


def test_restapi_dry_run_lists_all_planned_files_and_writes_nothing(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi", "--dry-run"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "rest_controller.py" in result.output
    assert "exception_handler.py" in result.output
    assert "server.py" in result.output
    assert not (project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "api").exists()


# ---------------------------------------------------------------------------
# restapi + --swagger
# ---------------------------------------------------------------------------


def test_swagger_injects_routes(project_root: Path, swagger_file: Path) -> None:
    result = runner.invoke(
        app,
        ["gep", "--type", "restapi", "--swagger", str(swagger_file)],
        catch_exceptions=False,
    )
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# agent type
# ---------------------------------------------------------------------------


def test_agent_creates_init(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "agent"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "agent" / "__init__.py").exists()


def test_agent_creates_agent_file(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "agent"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "agent" / "agent.py").exists()


def test_agent_creates_card_file(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "agent"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "agent" / "card.py").exists()


def test_agent_creates_test(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "agent"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "tests" / "infrastructure" / "entry_points" / "agent" / "test_agent.py").exists()


def test_agent_with_enable_kafka(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "agent", "--enable-kafka"], catch_exceptions=False)
    assert result.exit_code == 0
    content = (project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "agent" / "agent.py").read_text()
    assert "kafka" in content.lower() or "Kafka" in content


def test_agent_with_enable_mcp_client(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "agent", "--enable-mcp-client"], catch_exceptions=False)
    assert result.exit_code == 0
    content = (project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "agent" / "agent.py").read_text()
    assert "mcp" in content.lower() or "MCP" in content


# ---------------------------------------------------------------------------
# mcp type
# ---------------------------------------------------------------------------


def test_mcp_creates_init(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "mcp"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "mcp_server" / "__init__.py").exists()


def test_mcp_creates_tools_py(project_root: Path) -> None:
    """T009: base mcp run creates tools.py (replacing old monolithic server.py)."""
    result = runner.invoke(app, ["gep", "--type", "mcp"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "mcp_server" / "tools.py").exists()


def test_mcp_no_monolithic_server_py_in_mcp_server(project_root: Path) -> None:
    """T009: old monolithic server.py must NOT exist inside mcp_server/ after restructure."""
    runner.invoke(app, ["gep", "--type", "mcp"], catch_exceptions=False)
    server_py = project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "mcp_server" / "server.py"
    assert not server_py.exists()


def test_mcp_creates_test_tools(project_root: Path) -> None:
    """T009: base mcp run creates test_tools.py (replacing old test_server.py)."""
    result = runner.invoke(app, ["gep", "--type", "mcp"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "tests" / "infrastructure" / "entry_points" / "mcp_server" / "test_tools.py"
    ).exists()


def test_mcp_with_resources_creates_resources_py(project_root: Path) -> None:
    """T009: --with-resources creates resources.py in mcp_server/."""
    result = runner.invoke(app, ["gep", "--type", "mcp", "--with-resources"], catch_exceptions=False)
    assert result.exit_code == 0
    resources_py = project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "mcp_server" / "resources.py"
    assert resources_py.exists()


def test_mcp_with_resources_creates_test_resources_py(project_root: Path) -> None:
    """T009: --with-resources also creates test_resources.py."""
    result = runner.invoke(app, ["gep", "--type", "mcp", "--with-resources"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "tests" / "infrastructure" / "entry_points" / "mcp_server" / "test_resources.py"
    ).exists()


def test_mcp_without_resources_no_resources_py(project_root: Path) -> None:
    """T009: without --with-resources no resources.py is created."""
    runner.invoke(app, ["gep", "--type", "mcp"], catch_exceptions=False)
    resources_py = project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "mcp_server" / "resources.py"
    assert not resources_py.exists()


def test_mcp_with_prompts_creates_prompts_py(project_root: Path) -> None:
    """T009: --with-prompts creates prompts.py in mcp_server/."""
    result = runner.invoke(app, ["gep", "--type", "mcp", "--with-prompts"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "mcp_server" / "prompts.py").exists()


def test_mcp_with_prompts_creates_test_prompts_py(project_root: Path) -> None:
    """T009: --with-prompts also creates test_prompts.py."""
    result = runner.invoke(app, ["gep", "--type", "mcp", "--with-prompts"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "tests" / "infrastructure" / "entry_points" / "mcp_server" / "test_prompts.py"
    ).exists()


def test_mcp_without_prompts_no_prompts_py(project_root: Path) -> None:
    """T009: without --with-prompts no prompts.py is created."""
    runner.invoke(app, ["gep", "--type", "mcp"], catch_exceptions=False)
    prompts_py = project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "mcp_server" / "prompts.py"
    assert not prompts_py.exists()


def test_mcp_with_all_flags_creates_all_primitive_files(project_root: Path) -> None:
    """T009 / SC-002: --with-resources --with-prompts generates all three primitive files."""
    result = runner.invoke(app, ["gep", "--type", "mcp", "--with-resources", "--with-prompts"], catch_exceptions=False)
    assert result.exit_code == 0
    mcp_dir = project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "mcp_server"
    assert (mcp_dir / "tools.py").exists()
    assert (mcp_dir / "resources.py").exists()
    assert (mcp_dir / "prompts.py").exists()


def test_mcp_flags_rejected_for_restapi_type(project_root: Path) -> None:
    """T009 / FR-012: --with-resources with non-mcp type exits 1 with hint."""
    result = runner.invoke(app, ["gep", "--type", "restapi", "--with-resources"])
    assert result.exit_code == 1
    assert "only valid with --type mcp" in result.output


def test_mcp_prompts_flag_rejected_for_agent_type(project_root: Path) -> None:
    """T009 / FR-012: --with-prompts with non-mcp type exits 1 with hint."""
    result = runner.invoke(app, ["gep", "--type", "agent", "--with-prompts"])
    assert result.exit_code == 1
    assert "only valid with --type mcp" in result.output


# ---------------------------------------------------------------------------
# generic type
# ---------------------------------------------------------------------------


def test_generic_creates_init(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "generic"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "generic" / "__init__.py").exists()


def test_generic_creates_handler(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "generic"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "generic" / "entry_point.py").exists()


def test_generic_creates_test(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "generic"], catch_exceptions=False)
    assert result.exit_code == 0
    assert (
        project_root / "src" / "tests" / "infrastructure" / "entry_points" / "generic" / "test_entry_point.py"
    ).exists()


# ---------------------------------------------------------------------------
# Alias
# ---------------------------------------------------------------------------


def test_generate_entry_point_alias_works(project_root: Path) -> None:
    result = runner.invoke(app, ["generate-entry-point", "--type", "restapi"], catch_exceptions=False)
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Dry-run
# ---------------------------------------------------------------------------


def test_dry_run_writes_nothing(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi", "--dry-run"], catch_exceptions=False)
    assert result.exit_code == 0
    assert not (
        project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "api" / "v1" / "rest_controller.py"
    ).exists()


def test_dry_run_prints_paths(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi", "--dry-run"], catch_exceptions=False)
    assert "api" in result.output or "v1" in result.output or "server.py" in result.output


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------


def test_unknown_type_exits_1(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "graphql"])
    assert result.exit_code == 1
    assert "graphql" in result.output.lower() or "Unknown" in result.output


def test_swagger_without_restapi_exits_1(project_root: Path, swagger_file: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "agent", "--swagger", str(swagger_file)])
    assert result.exit_code == 1
    assert "--swagger" in result.output


def test_swagger_missing_file_exits_1(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi", "--swagger", "/nonexistent/spec.yaml"])
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
# US3: main.py overwritten (agent / mcp / generic only)
# ---------------------------------------------------------------------------


def test_agent_overwrites_main_py(project_root: Path) -> None:
    main_py = project_root / "src" / "my_app" / "main.py"
    runner.invoke(app, ["gep", "--type", "agent"], catch_exceptions=False)
    content = main_py.read_text()
    assert "def main" in content
    assert "asyncio" in content


def test_mcp_overwrites_main_py(project_root: Path) -> None:
    """Phase 4 / T025: gep --type mcp writes server.py at the package root.

    When T025 is implemented, ep_mcp.py will:
      - add server.py.jinja2 at <pkg>/server.py (uvicorn entrypoint)
      - set scripts_entry=True so pyproject.toml [project.scripts] is updated

    Until then this test must remain xfail (strict) so it is visible as a
    Phase 4 obligation.
    """
    server_py = project_root / "src" / "my_app" / "server.py"
    runner.invoke(app, ["gep", "--type", "mcp"], catch_exceptions=False)
    assert server_py.exists(), "server.py must exist after gep --type mcp (Phase 4)"
    content = server_py.read_text()
    assert "uvicorn" in content


def test_generic_overwrites_main_py(project_root: Path) -> None:
    main_py = project_root / "src" / "my_app" / "main.py"
    runner.invoke(app, ["gep", "--type", "generic"], catch_exceptions=False)
    content = main_py.read_text()
    assert "def main" in content
    assert "asyncio" in content


def test_dry_run_does_not_create_main_py(project_root: Path) -> None:
    # gep --type restapi never creates main.py, even in real run — confirm dry-run also skips it
    (project_root / "src" / "my_app" / "main.py").unlink(missing_ok=True)
    runner.invoke(app, ["gep", "--type", "restapi", "--dry-run"], catch_exceptions=False)
    assert not (project_root / "src" / "my_app" / "main.py").exists()


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
    # Remove both src and test dirs, server.py, app.py, and test_app.py so gep can execute a second time
    import shutil

    shutil.rmtree(project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "api")
    shutil.rmtree(project_root / "src" / "tests" / "infrastructure" / "entry_points" / "api", ignore_errors=True)
    (project_root / "src" / "my_app" / "server.py").unlink(missing_ok=True)
    (project_root / "src" / "my_app" / "application" / "app.py").unlink(missing_ok=True)
    (project_root / "src" / "tests" / "application" / "test_app.py").unlink(missing_ok=True)
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    content = (project_root / "pyproject.toml").read_text()
    assert content.count("fastapi") == 1


def test_dry_run_does_not_inject_deps(project_root: Path) -> None:
    original = (project_root / "pyproject.toml").read_text()
    runner.invoke(app, ["gep", "--type", "restapi", "--dry-run"], catch_exceptions=False)
    assert (project_root / "pyproject.toml").read_text() == original


def test_dry_run_prints_deps_to_inject(project_root: Path) -> None:
    result = runner.invoke(app, ["gep", "--type", "restapi", "--dry-run"], catch_exceptions=False)
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
    shutil.rmtree(project_root / "src" / "my_app" / "infrastructure" / "entry_points" / "api")
    shutil.rmtree(
        project_root / "src" / "tests" / "infrastructure" / "entry_points" / "api",
        ignore_errors=True,
    )
    (project_root / "src" / "my_app" / "server.py").unlink(missing_ok=True)
    (project_root / "src" / "my_app" / "application" / "app.py").unlink(missing_ok=True)
    (project_root / "src" / "tests" / "application" / "test_app.py").unlink(missing_ok=True)
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


# ---------------------------------------------------------------------------
# Feature 011 — US1: gep --type restapi deletes main.py (FR-001)
# ---------------------------------------------------------------------------


def test_restapi_deletes_main_py(project_root: Path) -> None:
    """T010: main.py created by scaffold ca must be removed after gep --type restapi."""
    main_py = project_root / "src" / "my_app" / "main.py"
    assert main_py.exists(), "fixture must create main.py via scaffold ca"
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert not main_py.exists()


def test_restapi_second_run_exits_with_duplicate_error(project_root: Path) -> None:
    """T010b: second gep --type restapi must fail on duplicate guard; main.py still absent."""
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    main_py = project_root / "src" / "my_app" / "main.py"
    # Second run — duplicate guard fires because src_dir already exists
    result = runner.invoke(app, ["gep", "--type", "restapi"])
    assert result.exit_code != 0
    assert not main_py.exists()


def test_restapi_gep_ok_when_main_py_already_absent(project_root: Path) -> None:
    """T011: silent no-op delete — command must succeed even if main.py is already gone."""
    (project_root / "src" / "my_app" / "main.py").unlink(missing_ok=True)
    result = runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    assert result.exit_code == 0


def test_restapi_dry_run_reports_would_delete_main_py(project_root: Path) -> None:
    """T012: dry-run must mention main.py in output; the file must NOT be deleted."""
    main_py = project_root / "src" / "my_app" / "main.py"
    assert main_py.exists()
    result = runner.invoke(app, ["gep", "--type", "restapi", "--dry-run"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "main.py" in result.output
    assert main_py.exists()


# ---------------------------------------------------------------------------
# Feature 011 — US2: gep --type restapi updates [project.scripts] (FR-002)
# ---------------------------------------------------------------------------


def test_restapi_updates_project_scripts(project_root: Path) -> None:
    """T015: [project.scripts] entry must read <pkg>.server:start_server after gep restapi."""
    import tomllib

    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    with (project_root / "pyproject.toml").open("rb") as fh:
        data = tomllib.load(fh)
    assert data["project"]["scripts"]["my-app"] == "my_app.server:start_server"


def test_restapi_dry_run_reports_scripts_update(project_root: Path) -> None:
    """T016: dry-run reports the scripts update; pyproject.toml must remain unchanged."""
    import tomllib

    result = runner.invoke(app, ["gep", "--type", "restapi", "--dry-run"], catch_exceptions=False)
    assert result.exit_code == 0
    assert "server:start_server" in result.output
    with (project_root / "pyproject.toml").open("rb") as fh:
        data = tomllib.load(fh)
    assert data["project"]["scripts"]["my-app"] == "my_app.main:main"


def test_agent_does_not_change_project_scripts(project_root: Path) -> None:
    """T017: gep --type agent must NOT modify [project.scripts]."""
    import tomllib

    runner.invoke(app, ["gep", "--type", "agent"], catch_exceptions=False)
    with (project_root / "pyproject.toml").open("rb") as fh:
        data = tomllib.load(fh)
    assert data["project"]["scripts"]["my-app"] == "my_app.main:main"


def test_mcp_updates_pyproject_scripts_to_server_main(project_root: Path) -> None:
    """Phase 4 / T023: gep --type mcp must update [project.scripts] to <pkg>.server:main."""
    import tomllib

    runner.invoke(app, ["gep", "--type", "mcp"], catch_exceptions=False)
    with (project_root / "pyproject.toml").open("rb") as fh:
        data = tomllib.load(fh)
    assert data["project"]["scripts"]["my-app"] == "my_app.server:main"


def test_mcp_creates_server_py_at_package_root(project_root: Path) -> None:
    """Phase 4 / T023: gep --type mcp must create server.py at <pkg> root."""
    runner.invoke(app, ["gep", "--type", "mcp"], catch_exceptions=False)
    server_py = project_root / "src" / "my_app" / "server.py"
    assert server_py.exists(), "server.py must be created at the package root"
    assert "uvicorn" in server_py.read_text()


def test_mcp_deletes_main_py(project_root: Path) -> None:
    """Phase 4 / T023: gep --type mcp must delete main.py after creating server.py."""
    main_py = project_root / "src" / "my_app" / "main.py"
    assert main_py.exists(), "fixture must provide main.py"
    runner.invoke(app, ["gep", "--type", "mcp"], catch_exceptions=False)
    assert not main_py.exists(), "main.py must be deleted after gep --type mcp"


def test_generic_does_not_change_project_scripts(project_root: Path) -> None:
    """T018b: gep --type generic must NOT modify [project.scripts]."""
    import tomllib

    runner.invoke(app, ["gep", "--type", "generic"], catch_exceptions=False)
    with (project_root / "pyproject.toml").open("rb") as fh:
        data = tomllib.load(fh)
    assert data["project"]["scripts"]["my-app"] == "my_app.main:main"


# ---------------------------------------------------------------------------
# Bidirectional exclusivity — restapi <-> mcp/agent (T024-T026)
# ---------------------------------------------------------------------------


def test_gep_mcp_blocked_when_restapi_exists(project_root: Path) -> None:
    """T024: mcp must be blocked when restapi entry point already exists."""
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    result = runner.invoke(app, ["gep", "--type", "mcp"])
    assert result.exit_code == 1
    assert "restapi" in result.output


def test_gep_agent_blocked_when_restapi_exists(project_root: Path) -> None:
    """T025: agent must be blocked when restapi entry point already exists."""
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    result = runner.invoke(app, ["gep", "--type", "agent"])
    assert result.exit_code == 1
    assert "restapi" in result.output


def test_gep_generic_not_blocked_when_restapi_exists(project_root: Path) -> None:
    """T026: generic is always allowed regardless of existing entry points."""
    runner.invoke(app, ["gep", "--type", "restapi"], catch_exceptions=False)
    result = runner.invoke(app, ["gep", "--type", "generic"], catch_exceptions=False)
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Phase 5 / T029 — application/app.py composition root (US3)
# ---------------------------------------------------------------------------


def test_mcp_creates_app_py(project_root: Path) -> None:
    """T029: gep --type mcp must create application/app.py."""
    runner.invoke(app, ["gep", "--type", "mcp"], catch_exceptions=False)
    app_py = project_root / "src" / "my_app" / "application" / "app.py"
    assert app_py.exists(), "application/app.py must be created by gep --type mcp"


def test_mcp_app_py_with_resources_contains_bind_resources(project_root: Path) -> None:
    """T029: gep --type mcp --with-resources must include bind_resources in app.py."""
    runner.invoke(app, ["gep", "--type", "mcp", "--with-resources"], catch_exceptions=False)
    app_py = project_root / "src" / "my_app" / "application" / "app.py"
    assert app_py.exists()
    assert "bind_resources" in app_py.read_text(encoding="utf-8")
