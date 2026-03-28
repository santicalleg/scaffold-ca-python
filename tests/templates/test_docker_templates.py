"""Template rendering tests for Docker-related templates (T014)."""

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


def test_dockerfile_has_base_image() -> None:
    out = renderer.render_string(_tmpl("project/dockerfile.jinja2"), _ctx().model_dump())
    assert "FROM python:3.13-slim" in out


def test_dockerfile_uses_python_package_in_cmd() -> None:
    ctx = _ctx()
    out = renderer.render_string(_tmpl("project/dockerfile.jinja2"), ctx.model_dump())
    assert ctx.python_package in out


def test_dockerfile_installs_uv() -> None:
    out = renderer.render_string(_tmpl("project/dockerfile.jinja2"), _ctx().model_dump())
    assert "uv" in out


def test_dockerignore_has_venv() -> None:
    out = renderer.render_string(_tmpl("project/dockerignore.jinja2"), _ctx().model_dump())
    assert ".venv" in out


def test_dockerignore_has_pycache() -> None:
    out = renderer.render_string(_tmpl("project/dockerignore.jinja2"), _ctx().model_dump())
    assert "__pycache__" in out


def test_dockerignore_has_git() -> None:
    out = renderer.render_string(_tmpl("project/dockerignore.jinja2"), _ctx().model_dump())
    assert ".git" in out
