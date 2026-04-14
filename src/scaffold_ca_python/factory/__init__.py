"""Factory contracts for scaffold module generation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from scaffold_ca_python.core.module_builder import ModuleBuilder


@runtime_checkable
class ModuleFactory(Protocol):
    """Contract for type-specific module generators."""

    def build(self, builder: ModuleBuilder) -> None:
        """Populate *builder* with file/dependency operations for this module type."""

