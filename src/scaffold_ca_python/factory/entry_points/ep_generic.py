"""EntryPointGeneric factory implementation (T021)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scaffold_ca_python.core.project_detector import resolve_tests_root
from scaffold_ca_python.factory import ModuleFactory

if TYPE_CHECKING:
    from scaffold_ca_python.core.module_builder import ModuleBuilder


class EntryPointGeneric(ModuleFactory):
    """Factory for Generic entry-point type."""

    def build(self, builder: ModuleBuilder) -> None:
        """Build Generic entry-point files.

        Queues files:
        - src/infrastructure/entry_points/generic/__init__.py
        - src/infrastructure/entry_points/generic/entry_point.py
        - tests/infrastructure/entry_points/generic/test_entry_point.py

        Overwrites:
        - src/main.py (if exists)

        No dependencies injected for generic type.
        """
        project_root = builder.project_root
        pkg = builder.project_ctx.python_package

        # Setup directory paths
        src_dir = project_root / "src" / pkg / "infrastructure" / "entry_points" / "generic"
        test_dir = resolve_tests_root(project_root) / "infrastructure" / "entry_points" / "generic"
        main_py = project_root / "src" / pkg / "main.py"

        # Template base path for entry_point/generic
        base = "entry_point/generic"

        # Build context dict from module context
        ctx_dict = {}
        if builder.module_ctx:
            ctx_dict.update(builder.module_ctx.model_dump())

        # Add source files
        def tpl(f: str) -> str:
            return f"{base}/{f}"

        builder.add_file(
            src_dir / "__init__.py",
            builder.render(f"{base}/__init__.py.jinja2", ctx_dict),
            template_name=tpl("__init__.py.jinja2"),
        )
        builder.add_file(
            src_dir / "entry_point.py",
            builder.render(f"{base}/handler.py.jinja2", ctx_dict),
            template_name=tpl("handler.py.jinja2"),
        )

        # Add test files
        builder.add_file(
            test_dir / "test_entry_point.py",
            builder.render(f"{base}/test_handler.py.jinja2", ctx_dict),
            template_name=tpl("test_handler.py.jinja2"),
            is_test=True,
        )

        # Overwrite main.py
        builder.add_file(
            main_py,
            builder.render(f"{base}/entrypoint_main.py.jinja2", ctx_dict),
            template_name=tpl("entrypoint_main.py.jinja2"),
            overwrite=True,
        )
