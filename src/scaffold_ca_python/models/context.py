"""ProjectContext and ModuleContext Pydantic v2 models (T014)."""

import re

from pydantic import BaseModel, computed_field, field_validator

from scaffold_ca_python.models.layer import Layer

_NAME_RE = re.compile(r"^[a-z][a-z0-9]*([_-][a-z0-9]+)*$")


def _to_snake_case(name: str) -> str:
    """Convert PascalCase, kebab-case, or mixed name to snake_case."""
    name = name.replace("-", "_")
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


def _to_pascal_case(name: str) -> str:
    """Convert snake_case, kebab-case, or mixed name to PascalCase (preserves inner case)."""
    return "".join(word[0].upper() + word[1:] for word in re.split(r"[_\s-]+", name) if word)


class ProjectContext(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def _validate_name(cls, v: str) -> str:
        if not _NAME_RE.match(v):
            raise ValueError(
                f"Project name '{v}' is invalid. "
                "Use kebab-case (e.g., 'my-project') or snake_case (e.g., 'my_project')."
            )
        return v

    @computed_field  # type: ignore[prop-decorator]
    @property
    def python_package(self) -> str:
        """Derive the Python import root: snake_case of name."""
        return _to_snake_case(self.name)


class ModuleContext(BaseModel):
    name: str
    layer: Layer
    project: ProjectContext
    subtype: str | None = None

    @field_validator("name")
    @classmethod
    def _validate_name(cls, v: str) -> str:
        if not _NAME_RE.match(v):
            raise ValueError(
                f"Module name '{v}' is invalid. "
                "Use kebab-case (e.g., 'my-module') or snake_case (e.g., 'my_module')."
            )
        return v

    @computed_field  # type: ignore[prop-decorator]
    @property
    def class_name(self) -> str:
        """PascalCase class name derived from name."""
        return _to_pascal_case(self.name)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def module_name(self) -> str:
        """snake_case file name (without .py) derived from name."""
        return _to_snake_case(self.name)
