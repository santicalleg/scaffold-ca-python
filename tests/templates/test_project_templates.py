"""Template rendering tests for project/ group (T083)."""

import importlib.resources

from scaffold_ca_python.core.template_renderer import TemplateRenderer
from scaffold_ca_python.models.context import ProjectContext

renderer = TemplateRenderer()


def _ctx() -> ProjectContext:
    return ProjectContext(name="MyApp")


def _tmpl(name: str) -> str:
    return importlib.resources.files("scaffold_ca_python.templates").joinpath(name).read_text(encoding="utf-8")


def test_pyproject_toml_has_scaffold_section() -> None:
    out = renderer.render_string(_tmpl("project/pyproject_toml.jinja2"), _ctx().model_dump())
    assert "[tool.scaffold-ca-python]" in out


def test_pyproject_toml_has_correct_package_name() -> None:
    out = renderer.render_string(_tmpl("project/pyproject_toml.jinja2"), _ctx().model_dump())
    assert "my_app" in out


def test_pyproject_toml_has_python_313_target() -> None:
    out = renderer.render_string(_tmpl("project/pyproject_toml.jinja2"), _ctx().model_dump())
    assert "3.13" in out


def test_pyproject_toml_has_ruff_lint_section() -> None:
    out = renderer.render_string(_tmpl("project/pyproject_toml.jinja2"), _ctx().model_dump())
    assert "[tool.ruff.lint]" in out


def test_pyproject_toml_has_per_file_ignores() -> None:
    out = renderer.render_string(_tmpl("project/pyproject_toml.jinja2"), _ctx().model_dump())
    assert "per-file-ignores" in out


def test_pyproject_toml_no_standalone_package_key() -> None:
    out = renderer.render_string(_tmpl("project/pyproject_toml.jinja2"), _ctx().model_dump())
    # Ensure there's no bare `package = "..."` key (only python_package is acceptable)
    import re

    assert not re.search(r'(?<![a-z_])package = "', out)


def test_python_version_renders_313() -> None:
    out = renderer.render_string(_tmpl("project/python_version.jinja2"), _ctx().model_dump())
    assert "3.13" in out


def test_readme_contains_project_name() -> None:
    out = renderer.render_string(_tmpl("project/README.jinja2"), _ctx().model_dump())
    assert "MyApp" in out


def test_pyproject_template_testpaths_is_src_tests() -> None:
    out = renderer.render_string(_tmpl("project/pyproject_toml.jinja2"), _ctx().model_dump())
    assert 'testpaths = ["src/tests"]' in out


def test_pyproject_template_coverage_uses_package_variable() -> None:
    out = renderer.render_string(_tmpl("project/pyproject_toml.jinja2"), _ctx().model_dump())
    assert "mcp_server_code_review" not in out
    assert "ms_test" not in out
    assert 'source = ["my_app"]' in out


def test_gitignore_contains_venv() -> None:
    out = renderer.render_string(_tmpl("project/gitignore.jinja2"), _ctx().model_dump())
    assert ".venv" in out


def test_layer_init_renders() -> None:
    out = renderer.render_string(_tmpl("project/layer_init.jinja2"), _ctx().model_dump())
    assert isinstance(out, str)


def test_project_resource_container_has_declarative_container() -> None:
    out = renderer.render_string(
        _tmpl("project/application/config/resource_container.py.jinja2"),
        _ctx().model_dump(),
    )
    assert "DeclarativeContainer" in out
    assert "pydantic_settings" in out
