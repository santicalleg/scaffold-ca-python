"""Template rendering tests for pipeline/ group — both providers (T089)."""

import importlib.resources

from scaffold_ca_python.core.template_renderer import TemplateRenderer
from scaffold_ca_python.models.context import ProjectContext

renderer = TemplateRenderer()


def _project() -> ProjectContext:
    return ProjectContext(name="my-app")


def _tmpl(name: str) -> str:
    return importlib.resources.files("scaffold_ca_python.templates").joinpath(name).read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# github
# ---------------------------------------------------------------------------


def test_github_has_ruff_step() -> None:
    out = renderer.render_string(_tmpl("pipeline/github/ci.yml.jinja2"), _project().model_dump())
    assert "ruff" in out


def test_github_has_mypy_step() -> None:
    out = renderer.render_string(_tmpl("pipeline/github/ci.yml.jinja2"), _project().model_dump())
    assert "mypy" in out


def test_github_has_pytest_with_coverage() -> None:
    out = renderer.render_string(_tmpl("pipeline/github/ci.yml.jinja2"), _project().model_dump())
    assert "pytest" in out
    assert "cov" in out


def test_github_has_coverage_gate_80() -> None:
    out = renderer.render_string(_tmpl("pipeline/github/ci.yml.jinja2"), _project().model_dump())
    assert "80" in out


# ---------------------------------------------------------------------------
# azure
# ---------------------------------------------------------------------------


def test_azure_has_ruff_step() -> None:
    out = renderer.render_string(_tmpl("pipeline/azure/azure_pipelines.yml.jinja2"), _project().model_dump())
    assert "ruff" in out


def test_azure_has_mypy_step() -> None:
    out = renderer.render_string(_tmpl("pipeline/azure/azure_pipelines.yml.jinja2"), _project().model_dump())
    assert "mypy" in out


def test_azure_has_pytest_with_coverage() -> None:
    out = renderer.render_string(_tmpl("pipeline/azure/azure_pipelines.yml.jinja2"), _project().model_dump())
    assert "pytest" in out
    assert "cov" in out


def test_azure_has_coverage_gate_80() -> None:
    out = renderer.render_string(_tmpl("pipeline/azure/azure_pipelines.yml.jinja2"), _project().model_dump())
    assert "80" in out
