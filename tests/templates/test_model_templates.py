"""Template rendering tests for model/ group (T084)."""

import importlib.resources

from scaffold_ca_python.core.template_renderer import TemplateRenderer
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer

renderer = TemplateRenderer()


def _project() -> ProjectContext:
    return ProjectContext(name="my-app")


def _ctx() -> ModuleContext:
    return ModuleContext(name="order", layer=Layer.DOMAIN_MODEL, project=_project())


def _tmpl(name: str) -> str:
    return importlib.resources.files("scaffold_ca_python.templates").joinpath(name).read_text(encoding="utf-8")


def test_model_class_name_present() -> None:
    ctx = _ctx()
    out = renderer.render_string(_tmpl("model/model.py.jinja2"), ctx.model_dump())
    assert "Order" in out


def test_model_has_base_model_import() -> None:
    out = renderer.render_string(_tmpl("model/model.py.jinja2"), _ctx().model_dump())
    assert "BaseModel" in out


def test_model_class_inherits_base_model() -> None:
    out = renderer.render_string(_tmpl("model/model.py.jinja2"), _ctx().model_dump())
    assert "class Order(BaseModel)" in out


def test_test_model_imports_class() -> None:
    out = renderer.render_string(_tmpl("model/test_model.py.jinja2"), _ctx().model_dump())
    assert "Order" in out
