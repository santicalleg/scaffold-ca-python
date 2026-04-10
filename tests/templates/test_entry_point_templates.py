"""Template rendering tests for entry_point/ group — all 4 types (T087)."""

import importlib.resources

from scaffold_ca_python.core.template_renderer import TemplateRenderer
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer

renderer = TemplateRenderer()


def _project() -> ProjectContext:
    return ProjectContext(name="MyApp")


def _ctx(name: str = "MyApp", subtype: str | None = None) -> ModuleContext:
    return ModuleContext(name=name, layer=Layer.ENTRY_POINTS, project=_project(), subtype=subtype)


def _tmpl(name: str) -> str:
    return (
        importlib.resources.files("scaffold_ca_python.templates")
        .joinpath(name)
        .read_text(encoding="utf-8")
    )


# ---------------------------------------------------------------------------
# restapi
# ---------------------------------------------------------------------------


def test_restapi_main_has_fastapi_import() -> None:
    out = renderer.render_string(
        _tmpl("entry_point/restapi/main.py.jinja2"), _ctx().model_dump()
    )
    assert "FastAPI" in out


def test_restapi_main_has_create_app() -> None:
    out = renderer.render_string(
        _tmpl("entry_point/restapi/main.py.jinja2"), _ctx().model_dump()
    )
    assert "create_app" in out


def test_restapi_router_has_async_def() -> None:
    out = renderer.render_string(
        _tmpl("entry_point/restapi/router.py.jinja2"), _ctx().model_dump()
    )
    assert "async def" in out


def test_entry_point_restapi_rest_controller_has_apirouter() -> None:
    out = renderer.render_string(
        _tmpl("entry_point/restapi/rest_controller.py.jinja2"), _ctx().model_dump()
    )
    assert "APIRouter" in out
    assert "async def" in out
    assert "/health" in out


def test_entry_point_restapi_exception_handler_has_http_exception() -> None:
    out = renderer.render_string(
        _tmpl("entry_point/restapi/exception_handler.py.jinja2"), _ctx().model_dump()
    )
    assert "HTTPException" in out
    assert "RequestValidationError" in out


def test_entry_point_restapi_server_has_fastapi_factory() -> None:
    out = renderer.render_string(
        _tmpl("entry_point/restapi/server.py.jinja2"), _ctx().model_dump()
    )
    assert "FastAPI" in out
    assert "lifespan" in out
    assert "Container" in out
    assert "start_server" in out


# ---------------------------------------------------------------------------
# agent
# ---------------------------------------------------------------------------


def test_agent_has_class_name() -> None:
    ctx = _ctx("MyApp")
    out = renderer.render_string(
        _tmpl("entry_point/agent/agent.py.jinja2"), ctx.model_dump()
    )
    assert "Agent" in out


def test_agent_has_async_run() -> None:
    out = renderer.render_string(
        _tmpl("entry_point/agent/agent.py.jinja2"), _ctx().model_dump()
    )
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
# mcp
# ---------------------------------------------------------------------------


def test_mcp_server_has_list_tools() -> None:
    out = renderer.render_string(
        _tmpl("entry_point/mcp/server.py.jinja2"), _ctx().model_dump()
    )
    assert "list_tools" in out


def test_mcp_server_has_async_def() -> None:
    out = renderer.render_string(
        _tmpl("entry_point/mcp/server.py.jinja2"), _ctx().model_dump()
    )
    assert "async def" in out


# ---------------------------------------------------------------------------
# generic
# ---------------------------------------------------------------------------


def test_generic_has_entry_point_class() -> None:
    out = renderer.render_string(
        _tmpl("entry_point/generic/handler.py.jinja2"), _ctx().model_dump()
    )
    assert "EntryPoint" in out


def test_generic_has_async_run() -> None:
    out = renderer.render_string(
        _tmpl("entry_point/generic/handler.py.jinja2"), _ctx().model_dump()
    )
    assert "async def run" in out
