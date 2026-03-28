"""Template rendering tests for helper/ group (T088)."""

import importlib.resources

from scaffold_ca_python.core.template_renderer import TemplateRenderer
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer

renderer = TemplateRenderer()


def _project() -> ProjectContext:
    return ProjectContext(name="MyApp")


def _ctx() -> ModuleContext:
    return ModuleContext(name="DateUtils", layer=Layer.HELPERS, project=_project())


def _tmpl(name: str) -> str:
    return (
        importlib.resources.files("scaffold_ca_python.templates")
        .joinpath(name)
        .read_text(encoding="utf-8")
    )


def test_helper_class_name_present() -> None:
    out = renderer.render_string(_tmpl("helper/helper.py.jinja2"), _ctx().model_dump())
    assert "DateUtils" in out


def test_helper_has_pass_body() -> None:
    out = renderer.render_string(_tmpl("helper/helper.py.jinja2"), _ctx().model_dump())
    assert "pass" in out


def test_helper_init_contains_docstring() -> None:
    out = renderer.render_string(_tmpl("helper/__init__.py.jinja2"), _ctx().model_dump())
    assert "DateUtils" in out


def test_test_helper_imports_class() -> None:
    out = renderer.render_string(_tmpl("helper/test_helper.py.jinja2"), _ctx().model_dump())
    assert "DateUtils" in out


def test_test_helper_has_test_function() -> None:
    out = renderer.render_string(_tmpl("helper/test_helper.py.jinja2"), _ctx().model_dump())
    assert "def test_" in out
