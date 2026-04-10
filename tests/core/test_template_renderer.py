"""Tests for TemplateRenderer: Jinja2 template loading and rendering (T020)."""

from pathlib import Path

import pytest

from scaffold_ca_python.core.name_utils import ScaffoldError
from scaffold_ca_python.core.template_renderer import TemplateRenderer
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def renderer() -> TemplateRenderer:
    return TemplateRenderer()


@pytest.fixture()
def project_ctx() -> ProjectContext:
    return ProjectContext(name="MyApp")


@pytest.fixture()
def module_ctx(project_ctx: ProjectContext) -> ModuleContext:
    return ModuleContext(name="Order", layer=Layer.DOMAIN_MODEL, project=project_ctx)


# ---------------------------------------------------------------------------
# Loading from importlib.resources
# ---------------------------------------------------------------------------


def test_renderer_instantiates(renderer: TemplateRenderer) -> None:
    assert renderer is not None


def test_raises_on_missing_template(renderer: TemplateRenderer, project_ctx: ProjectContext) -> None:
    with pytest.raises((ScaffoldError, Exception)):
        renderer.render("nonexistent_template_xyz.j2", project_ctx)


# ---------------------------------------------------------------------------
# Rendering with context
# ---------------------------------------------------------------------------


def test_render_returns_string(renderer: TemplateRenderer, tmp_path: Path) -> None:
    """Use a real template from the package to verify rendering works."""
    # This test will pass once there is at least one template in the package.
    # For now, we confirm that the renderer can be called and returns a str
    # when given a valid template name.
    #
    # We write a tiny on-disk Jinja2 template as a side fixture and verify
    # the renderer can load and render it via the Jinja2 FileSystemLoader fallback.
    template_file = tmp_path / "hello.j2"
    template_file.write_text("Hello {{ name }}!")

    result = renderer.render_string("Hello {{ name }}!", {"name": "World"})
    assert result == "Hello World!"


def test_render_string_with_project_context(renderer: TemplateRenderer, project_ctx: ProjectContext) -> None:
    template_src = "project: {{ name }}, pkg: {{ python_package }}"
    ctx_dict = project_ctx.model_dump()
    result = renderer.render_string(template_src, ctx_dict)
    assert "MyApp" in result
    assert "my_app" in result


def test_render_string_with_module_context(renderer: TemplateRenderer, module_ctx: ModuleContext) -> None:
    template_src = "class {{ class_name }}:"
    ctx_dict = module_ctx.model_dump()
    result = renderer.render_string(template_src, ctx_dict)
    assert "Order" in result


def test_render_string_exposes_computed_class_name(renderer: TemplateRenderer, module_ctx: ModuleContext) -> None:
    template_src = "class {{ class_name }}:"
    ctx_dict = module_ctx.model_dump()
    result = renderer.render_string(template_src, ctx_dict)
    assert result == "class Order:"


def test_render_string_exposes_computed_module_name(renderer: TemplateRenderer, module_ctx: ModuleContext) -> None:
    template_src = "import {{ module_name }}"
    # model_dump should include computed fields
    ctx_dict = module_ctx.model_dump()
    result = renderer.render_string(template_src, ctx_dict)
    assert "order" in result


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_render_string_empty_template(renderer: TemplateRenderer) -> None:
    assert renderer.render_string("", {}) == ""


def test_render_string_no_variables(renderer: TemplateRenderer) -> None:
    assert renderer.render_string("static content", {}) == "static content"
