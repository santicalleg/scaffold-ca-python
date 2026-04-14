"""DrivenAdapterGeneric factory implementation (T029)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scaffold_ca_python.core.name_utils import to_snake_case
from scaffold_ca_python.core.project_detector import resolve_tests_root
from scaffold_ca_python.factory import ModuleFactory

if TYPE_CHECKING:
    from scaffold_ca_python.core.module_builder import ModuleBuilder


class DrivenAdapterGeneric(ModuleFactory):
    """Factory for Generic driven-adapter type."""

    def build(self, builder: ModuleBuilder) -> None:
        """Build Generic driven-adapter files.

        Queues files:
        - src/infrastructure/driven_adapters/<snake_name>/__init__.py
        - src/infrastructure/driven_adapters/<snake_name>/<snake_name>_adapter.py
        - tests/infrastructure/driven_adapters/<snake_name>/test_<snake_name>_adapter.py

        No dependencies injected for generic type.
        """
        project_root = builder.project_root
        pkg = builder.project_ctx.python_package

        # Get adapter name from module context
        adapter_name = builder.module_ctx.name if builder.module_ctx else "CustomAdapter"
        snake_name = to_snake_case(adapter_name)

        # Setup directory paths
        src_dir = project_root / "src" / pkg / "infrastructure" / "driven_adapters" / snake_name
        test_dir = resolve_tests_root(project_root) / "infrastructure" / "driven_adapters" / snake_name

        # Template base path for driven_adapter/generic
        base = "driven_adapter/generic"

        # Build context dict from module context
        ctx_dict = {}
        if builder.module_ctx:
            ctx_dict.update(builder.module_ctx.model_dump())

        # Add source files
        builder.add_file(
            src_dir / "__init__.py",
            builder.render(f"{base}/__init__.py.jinja2", ctx_dict),
            template_name=f"{base}/__init__.py.jinja2",
        )
        builder.add_file(
            src_dir / f"{snake_name}_adapter.py",
            builder.render(f"{base}/adapter.py.jinja2", ctx_dict),
            template_name=f"{base}/adapter.py.jinja2",
        )

        # Add test files
        builder.add_file(
            test_dir / f"test_{snake_name}_adapter.py",
            builder.render(f"{base}/test_adapter.py.jinja2", ctx_dict),
            template_name=f"{base}/test_adapter.py.jinja2",
            is_test=True,
        )
