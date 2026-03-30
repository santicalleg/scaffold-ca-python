"""Template rendering tests for DI config templates (T022)."""

import importlib.resources

from scaffold_ca_python.core.template_renderer import TemplateRenderer
from scaffold_ca_python.models.context import ProjectContext

renderer = TemplateRenderer()


def _ctx() -> ProjectContext:
    return ProjectContext(name="OrderService")


def _tmpl(name: str) -> str:
    return (
        importlib.resources.files("scaffold_ca_python.templates")
        .joinpath(name)
        .read_text(encoding="utf-8")
    )


def _render(filename: str) -> str:
    return renderer.render_string(
        _tmpl(f"project/application/config/{filename}.py.jinja2"),
        _ctx().model_dump(),
    )


# --- __init__.py -----------------------------------------------------------

def test_init_renders_docstring() -> None:
    out = _render("__init__")
    assert "DI configuration package" in out


# --- config.py -------------------------------------------------------------

def test_config_has_settings_class() -> None:
    out = _render("config")
    assert "Settings" in out


def test_config_has_base_settings() -> None:
    out = _render("config")
    assert "BaseSettings" in out


def test_config_has_settings_singleton() -> None:
    out = _render("config")
    assert "settings = Settings()" in out


# --- driven_adapters_container.py -----------------------------------------

def test_da_container_class_name() -> None:
    out = _render("driven_adapters_container")
    assert "DAContainer" in out


def test_da_container_uses_declarative_container() -> None:
    out = _render("driven_adapters_container")
    assert "DeclarativeContainer" in out


# --- usecases_container.py ------------------------------------------------

def test_usecase_container_class_name() -> None:
    out = _render("usecases_container")
    assert "UseCaseContainer" in out


def test_usecase_container_has_dependencies_container() -> None:
    out = _render("usecases_container")
    assert "DependenciesContainer" in out


def test_usecase_container_imports_da_container() -> None:
    out = _render("usecases_container")
    assert "DAContainer" in out


def test_usecase_container_uses_python_package() -> None:
    ctx = _ctx()
    out = renderer.render_string(
        _tmpl("project/application/config/usecases_container.py.jinja2"),
        ctx.model_dump(),
    )
    assert ctx.python_package in out


# --- container.py ---------------------------------------------------------

def test_container_class_name() -> None:
    out = _render("container")
    assert "class Container" in out


def test_container_wires_da_container() -> None:
    out = _render("container")
    assert "providers.Container(DAContainer)" in out


def test_container_wires_usecase_container() -> None:
    out = _render("container")
    assert "providers.Container(" in out
    assert "UseCaseContainer" in out


def test_container_uses_python_package() -> None:
    ctx = _ctx()
    out = renderer.render_string(
        _tmpl("project/application/config/container.py.jinja2"),
        ctx.model_dump(),
    )
    assert ctx.python_package in out
