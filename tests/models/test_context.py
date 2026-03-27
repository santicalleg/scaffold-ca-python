"""Tests for ProjectContext and ModuleContext Pydantic models (T010)."""

import pytest
from pydantic import ValidationError

from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer


# ---------------------------------------------------------------------------
# ProjectContext
# ---------------------------------------------------------------------------

def test_project_context_valid() -> None:
    ctx = ProjectContext(name="MyProject", package="com.example")
    assert ctx.name == "MyProject"
    assert ctx.package == "com.example"


def test_project_context_python_package_derived_from_name() -> None:
    ctx = ProjectContext(name="MyProject", package="com.example")
    assert ctx.python_package == "my_project"


def test_project_context_python_package_with_numbers() -> None:
    ctx = ProjectContext(name="Project2025", package="com.example")
    assert ctx.python_package == "project2025"


def test_project_context_name_must_start_with_letter() -> None:
    with pytest.raises(ValidationError):
        ProjectContext(name="1Invalid", package="com.example")


def test_project_context_name_rejects_spaces() -> None:
    with pytest.raises(ValidationError):
        ProjectContext(name="My Project", package="com.example")


def test_project_context_name_rejects_hyphens() -> None:
    with pytest.raises(ValidationError):
        ProjectContext(name="my-project", package="com.example")


def test_project_context_name_rejects_empty() -> None:
    with pytest.raises(ValidationError):
        ProjectContext(name="", package="com.example")


def test_project_context_name_allows_underscores() -> None:
    ctx = ProjectContext(name="My_Project", package="com.example")
    assert ctx.name == "My_Project"


# ---------------------------------------------------------------------------
# ModuleContext
# ---------------------------------------------------------------------------

def _make_project() -> ProjectContext:
    return ProjectContext(name="MyProject", package="com.example")


def test_module_context_valid() -> None:
    ctx = ModuleContext(name="Order", layer=Layer.DOMAIN_MODEL, project=_make_project())
    assert ctx.name == "Order"
    assert ctx.layer == Layer.DOMAIN_MODEL


def test_module_context_class_name_is_pascal_case() -> None:
    ctx = ModuleContext(name="my_order", layer=Layer.DOMAIN_MODEL, project=_make_project())
    assert ctx.class_name == "MyOrder"


def test_module_context_module_name_is_snake_case() -> None:
    ctx = ModuleContext(name="MyOrder", layer=Layer.DOMAIN_MODEL, project=_make_project())
    assert ctx.module_name == "my_order"


def test_module_context_subtype_defaults_to_none() -> None:
    ctx = ModuleContext(name="Order", layer=Layer.DOMAIN_MODEL, project=_make_project())
    assert ctx.subtype is None


def test_module_context_subtype_can_be_set() -> None:
    ctx = ModuleContext(
        name="RestAdapter",
        layer=Layer.DRIVEN_ADAPTERS,
        subtype="rest-consumer",
        project=_make_project(),
    )
    assert ctx.subtype == "rest-consumer"


def test_module_context_name_must_start_with_letter() -> None:
    with pytest.raises(ValidationError):
        ModuleContext(name="1Order", layer=Layer.DOMAIN_MODEL, project=_make_project())


def test_module_context_name_rejects_spaces() -> None:
    with pytest.raises(ValidationError):
        ModuleContext(name="My Order", layer=Layer.DOMAIN_MODEL, project=_make_project())
