"""HelperFactory implementation (T037)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scaffold_ca_python.core.name_utils import to_snake_case
from scaffold_ca_python.core.project_detector import resolve_tests_root
from scaffold_ca_python.factory import ModuleFactory

if TYPE_CHECKING:
    from scaffold_ca_python.core.module_builder import ModuleBuilder


class HelperFactory(ModuleFactory):
    """Factory for helper utility generation."""

    def build(self, builder: ModuleBuilder) -> None:
        """Build helper utility files.

        Queues files:
        - src/infrastructure/helpers/{snake_name}/__init__.py
        - src/infrastructure/helpers/{snake_name}/{snake_name}.py
        - tests/infrastructure/helpers/{snake_name}/test_{snake_name}.py

        No dependencies injected.
        """
        project_root = builder.project_root
        pkg = builder.project_ctx.python_package

        # Get helper name from module context and convert to snake_case
        helper_name = builder.module_ctx.name if builder.module_ctx else "Helper"
        snake_name = to_snake_case(helper_name)

        # Setup directory paths
        src_dir = project_root / "src" / pkg / "infrastructure" / "helpers" / snake_name
        test_dir = resolve_tests_root(project_root) / "infrastructure" / "helpers" / snake_name

        # Template base path
        base = "helper"

        # Build context dict from module context
        ctx_dict = {}
        if builder.module_ctx:
            ctx_dict.update(builder.module_ctx.model_dump())

        # Add __init__ file
        builder.add_file(
            src_dir / "__init__.py",
            builder.render(f"{base}/__init__.py.jinja2", ctx_dict),
            template_name=f"{base}/__init__.py.jinja2",
        )

        # Add helper implementation file
        builder.add_file(
            src_dir / f"{snake_name}.py",
            builder.render(f"{base}/helper.py.jinja2", ctx_dict),
            template_name=f"{base}/helper.py.jinja2",
        )

        # Add test file
        builder.add_file(
            test_dir / f"test_{snake_name}.py",
            builder.render(f"{base}/test_helper.py.jinja2", ctx_dict),
            template_name=f"{base}/test_helper.py.jinja2",
            is_test=True,
        )
