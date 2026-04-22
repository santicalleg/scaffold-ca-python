"""Template rendering tests for driven_adapter/ group — all 3 types (T086)."""

import importlib.resources

from scaffold_ca_python.core.template_renderer import TemplateRenderer
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer

renderer = TemplateRenderer()


def _project() -> ProjectContext:
    return ProjectContext(name="my-app")


def _ctx(name: str = "my-adapter") -> ModuleContext:
    return ModuleContext(name=name, layer=Layer.DRIVEN_ADAPTERS, project=_project())


def _tmpl(name: str) -> str:
    return importlib.resources.files("scaffold_ca_python.templates").joinpath(name).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# rest-consumer
# ---------------------------------------------------------------------------


def test_rest_consumer_has_httpx_import() -> None:
    out = renderer.render_string(_tmpl("driven_adapter/rest_consumer/rest_consumer.py.jinja2"), _ctx().model_dump())
    assert "httpx" in out


def test_rest_consumer_has_async_client() -> None:
    out = renderer.render_string(_tmpl("driven_adapter/rest_consumer/rest_consumer.py.jinja2"), _ctx().model_dump())
    assert "AsyncClient" in out


def test_rest_consumer_has_async_get() -> None:
    out = renderer.render_string(_tmpl("driven_adapter/rest_consumer/rest_consumer.py.jinja2"), _ctx().model_dump())
    assert "async def get" in out


# ---------------------------------------------------------------------------
# secrets
# ---------------------------------------------------------------------------


def test_secrets_has_get_secret() -> None:
    out = renderer.render_string(_tmpl("driven_adapter/secrets/secrets_adapter.py.jinja2"), _ctx().model_dump())
    assert "get_secret" in out


def test_secrets_has_async_methods() -> None:
    out = renderer.render_string(_tmpl("driven_adapter/secrets/secrets_adapter.py.jinja2"), _ctx().model_dump())
    assert "async def" in out


# ---------------------------------------------------------------------------
# generic
# ---------------------------------------------------------------------------


def test_generic_class_name_present() -> None:
    ctx = _ctx("payment-gateway")
    out = renderer.render_string(_tmpl("driven_adapter/generic/adapter.py.jinja2"), ctx.model_dump())
    assert "PaymentGateway" in out


def test_generic_has_adapter_suffix() -> None:
    ctx = _ctx("payment-gateway")
    out = renderer.render_string(_tmpl("driven_adapter/generic/adapter.py.jinja2"), ctx.model_dump())
    assert "PaymentGatewayAdapter" in out


def test_generic_has_async_execute() -> None:
    out = renderer.render_string(_tmpl("driven_adapter/generic/adapter.py.jinja2"), _ctx().model_dump())
    assert "async def execute" in out
