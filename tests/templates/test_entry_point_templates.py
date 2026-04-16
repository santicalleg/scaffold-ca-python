"""Template rendering tests for entry_point/ group — all 4 types (T087)."""

import importlib.resources

from scaffold_ca_python.core.template_renderer import TemplateRenderer
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer

renderer = TemplateRenderer()


def _project() -> ProjectContext:
    return ProjectContext(name="my-app")


def _ctx(name: str = "my-app", subtype: str | None = None) -> ModuleContext:
    return ModuleContext(name=name, layer=Layer.ENTRY_POINTS, project=_project(), subtype=subtype)


def _tmpl(name: str) -> str:
    return importlib.resources.files("scaffold_ca_python.templates").joinpath(name).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# restapi
# ---------------------------------------------------------------------------


def test_entry_point_restapi_rest_controller_has_apirouter() -> None:
    out = renderer.render_string(_tmpl("entry_point/restapi/rest_controller.py.jinja2"), _ctx().model_dump())
    assert "APIRouter" in out
    assert "async def" in out
    assert "/health" in out


def test_entry_point_restapi_exception_handler_has_http_exception() -> None:
    out = renderer.render_string(_tmpl("entry_point/restapi/exception_handler.py.jinja2"), _ctx().model_dump())
    assert "HTTPException" in out
    assert "RequestValidationError" in out


def test_entry_point_restapi_server_has_start_server() -> None:
    out = renderer.render_string(_tmpl("entry_point/restapi/server.py.jinja2"), _ctx().model_dump())
    assert "start_server" in out


# ---------------------------------------------------------------------------
# restapi — server.py thin wrapper (US2 / T011–T012)
# ---------------------------------------------------------------------------


def test_entry_point_restapi_server_is_thin_wrapper() -> None:
    out = renderer.render_string(_tmpl("entry_point/restapi/server.py.jinja2"), _ctx().model_dump())
    assert "FastAPI" not in out
    assert "Container" not in out


def test_entry_point_restapi_server_imports_start_server() -> None:
    out = renderer.render_string(_tmpl("entry_point/restapi/server.py.jinja2"), _ctx().model_dump())
    assert "application.app import start_server" in out


# ---------------------------------------------------------------------------
# restapi — app.py template (US1 / T003–T006)
# ---------------------------------------------------------------------------


def test_entry_point_restapi_app_has_create_app_factory() -> None:
    out = renderer.render_string(_tmpl("entry_point/restapi/app.py.jinja2"), _ctx().model_dump())
    assert "create_app" in out


def test_entry_point_restapi_app_has_lifespan() -> None:
    out = renderer.render_string(_tmpl("entry_point/restapi/app.py.jinja2"), _ctx().model_dump())
    assert "lifespan" in out
    assert "asynccontextmanager" in out


def test_entry_point_restapi_app_has_container_wiring() -> None:
    out = renderer.render_string(_tmpl("entry_point/restapi/app.py.jinja2"), _ctx().model_dump())
    assert "Container" in out
    assert "wire(" in out


def test_entry_point_restapi_app_factory_path_uses_application_app() -> None:
    out = renderer.render_string(_tmpl("entry_point/restapi/app.py.jinja2"), _ctx().model_dump())
    assert "application.app:create_app" in out


# ---------------------------------------------------------------------------
# restapi — test file templates (US4 / T022–T025)
# ---------------------------------------------------------------------------


def test_entry_point_restapi_test_app_template_has_create_app_assertion() -> None:
    out = renderer.render_string(_tmpl("entry_point/restapi/test_app.py.jinja2"), _ctx().model_dump())
    assert "create_app" in out
    assert "FastAPI" in out


def test_entry_point_restapi_test_server_template_references_start_server() -> None:
    out = renderer.render_string(_tmpl("entry_point/restapi/test_server.py.jinja2"), _ctx().model_dump())
    assert "start_server" in out


def test_entry_point_restapi_test_exception_handler_template_has_status_codes() -> None:
    out = renderer.render_string(_tmpl("entry_point/restapi/test_exception_handler.py.jinja2"), _ctx().model_dump())
    assert "422" in out or "HTTPException" in out


# ---------------------------------------------------------------------------
# restapi — test_rest_controller.py template correctness (T004, T005)
# ---------------------------------------------------------------------------


def test_generated_test_rest_controller_imports_application_app() -> None:
    out = renderer.render_string(_tmpl("entry_point/restapi/test_rest_controller.py.jinja2"), _ctx().model_dump())
    assert "application.app" in out
    assert "server import" not in out


def test_generated_test_rest_controller_has_no_duplicate_docstring() -> None:
    out = renderer.render_string(_tmpl("entry_point/restapi/test_rest_controller.py.jinja2"), _ctx().model_dump())
    assert out.count('"""Tests') == 1


# ---------------------------------------------------------------------------
# agent
# ---------------------------------------------------------------------------


def test_agent_has_class_name() -> None:
    ctx = _ctx("my-app")
    out = renderer.render_string(_tmpl("entry_point/agent/agent.py.jinja2"), ctx.model_dump())
    assert "Agent" in out


def test_agent_has_async_run() -> None:
    out = renderer.render_string(_tmpl("entry_point/agent/agent.py.jinja2"), _ctx().model_dump())
    assert "async def run" in out


def test_agent_with_kafka_flag_includes_stub() -> None:
    ctx_dict = _ctx().model_dump()
    ctx_dict["enable_kafka"] = True
    out = renderer.render_string(_tmpl("entry_point/agent/agent.py.jinja2"), ctx_dict)
    assert "kafka" in out.lower()


def test_agent_without_kafka_flag_excludes_stub() -> None:
    ctx_dict = _ctx().model_dump()
    ctx_dict["enable_kafka"] = False
    out = renderer.render_string(_tmpl("entry_point/agent/agent.py.jinja2"), ctx_dict)
    assert "AIOKafkaConsumer" not in out


# ---------------------------------------------------------------------------
# mcp — tools.py template (T006)
# ---------------------------------------------------------------------------


def test_mcp_tools_has_bind_tools() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/tools.py.jinja2"), _ctx().model_dump())
    assert "bind_tools" in out


def test_mcp_tools_has_inject_decorator() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/tools.py.jinja2"), _ctx().model_dump())
    assert "@inject" in out


def test_mcp_tools_has_fastmcp_import() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/tools.py.jinja2"), _ctx().model_dump())
    assert "from mcp.server.fastmcp import FastMCP" in out


def test_mcp_tools_is_async() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/tools.py.jinja2"), _ctx().model_dump())
    assert "async def bind_tools" in out


# ---------------------------------------------------------------------------
# mcp — resources.py template (T007)
# ---------------------------------------------------------------------------


def test_mcp_resources_has_bind_resources() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/resources.py.jinja2"), _ctx().model_dump())
    assert "bind_resources" in out


def test_mcp_resources_has_inject_decorator() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/resources.py.jinja2"), _ctx().model_dump())
    assert "@inject" in out


def test_mcp_resources_has_fastmcp_import() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/resources.py.jinja2"), _ctx().model_dump())
    assert "from mcp.server.fastmcp import FastMCP" in out


def test_mcp_resources_is_async() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/resources.py.jinja2"), _ctx().model_dump())
    assert "async def bind_resources" in out


# ---------------------------------------------------------------------------
# mcp — prompts.py template (T007)
# ---------------------------------------------------------------------------


def test_mcp_prompts_has_bind_prompts() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/prompts.py.jinja2"), _ctx().model_dump())
    assert "bind_prompts" in out


def test_mcp_prompts_has_inject_decorator() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/prompts.py.jinja2"), _ctx().model_dump())
    assert "@inject" in out


def test_mcp_prompts_has_fastmcp_import() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/prompts.py.jinja2"), _ctx().model_dump())
    assert "from mcp.server.fastmcp import FastMCP" in out


def test_mcp_prompts_is_sync_not_async() -> None:
    """bind_prompts is intentionally sync (unlike bind_tools/bind_resources)."""
    out = renderer.render_string(_tmpl("entry_point/mcp/prompts.py.jinja2"), _ctx().model_dump())
    assert "def bind_prompts" in out
    assert "async def bind_prompts" not in out


# ---------------------------------------------------------------------------
# mcp — server.py (uvicorn entrypoint) — Phase 4 / T021
# ---------------------------------------------------------------------------


def test_mcp_server_has_main_function() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/server.py.jinja2"), _ctx().model_dump())
    assert "def main" in out


def test_mcp_server_has_uvicorn_run() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/server.py.jinja2"), _ctx().model_dump())
    assert "uvicorn.run" in out


def test_mcp_server_imports_app() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/server.py.jinja2"), _ctx().model_dump())
    assert "import app" in out


# ---------------------------------------------------------------------------
# mcp — app.py (composition root) — Phase 5 / T026–T027
# ---------------------------------------------------------------------------

def _app_ctx(*, with_resources: bool = False, with_prompts: bool = False) -> dict[str, object]:
    return {**_ctx().model_dump(), "with_resources": with_resources, "with_prompts": with_prompts}


def test_mcp_app_has_fastmcp_instance() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/app.py.jinja2"), _app_ctx())
    assert "FastMCP" in out


def test_mcp_app_has_start_server() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/app.py.jinja2"), _app_ctx())
    assert "start_server" in out


def test_mcp_app_has_lifespan() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/app.py.jinja2"), _app_ctx())
    assert "lifespan" in out
    assert "asynccontextmanager" in out


def test_mcp_app_has_streamable_http_app() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/app.py.jinja2"), _app_ctx())
    assert "streamable_http_app" in out


def test_mcp_app_with_resources_includes_bind_resources() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/app.py.jinja2"), _app_ctx(with_resources=True))
    assert "bind_resources" in out


def test_mcp_app_without_resources_excludes_bind_resources() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/app.py.jinja2"), _app_ctx(with_resources=False))
    assert "bind_resources" not in out


def test_mcp_app_with_prompts_includes_bind_prompts() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/app.py.jinja2"), _app_ctx(with_prompts=True))
    assert "bind_prompts" in out


def test_mcp_app_without_prompts_excludes_bind_prompts() -> None:
    out = renderer.render_string(_tmpl("entry_point/mcp/app.py.jinja2"), _app_ctx(with_prompts=False))
    assert "bind_prompts" not in out


# ---------------------------------------------------------------------------
# generic
# ---------------------------------------------------------------------------


def test_generic_has_entry_point_class() -> None:
    out = renderer.render_string(_tmpl("entry_point/generic/handler.py.jinja2"), _ctx().model_dump())
    assert "EntryPoint" in out


def test_generic_has_async_run() -> None:
    out = renderer.render_string(_tmpl("entry_point/generic/handler.py.jinja2"), _ctx().model_dump())
    assert "async def run" in out


# ---------------------------------------------------------------------------
# restapi — test template (US2 / T019)
# ---------------------------------------------------------------------------


def test_entry_point_restapi_test_rest_controller_has_testclient() -> None:
    out = renderer.render_string(_tmpl("entry_point/restapi/test_rest_controller.py.jinja2"), _ctx().model_dump())
    assert "TestClient" in out
    assert "/v1/health" in out
    assert "assert response.status_code == 200" in out
