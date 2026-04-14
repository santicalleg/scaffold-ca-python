"""EntryPointMcp factory implementation (T019)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scaffold_ca_python.core.project_detector import resolve_tests_root
from scaffold_ca_python.factory import ModuleFactory

if TYPE_CHECKING:
    from scaffold_ca_python.core.module_builder import ModuleBuilder


class EntryPointMcp(ModuleFactory):
    """Factory for MCP entry-point type."""

    def build(self, builder: ModuleBuilder) -> None:
        """Build MCP entry-point files and dependencies.

        Queues files:
        - src/infrastructure/entry_points/mcp_server/__init__.py
        - src/infrastructure/entry_points/mcp_server/server.py
        - tests/infrastructure/entry_points/mcp_server/test_server.py

        Overwrites:
        - src/main.py (if exists)

        Injects:
        - mcp>=1.0
        """
        project_root = builder.project_root
        pkg = builder.project_ctx.python_package

        # Setup directory paths
        src_dir = project_root / "src" / pkg / "infrastructure" / "entry_points" / "mcp_server"
        test_dir = resolve_tests_root(project_root) / "infrastructure" / "entry_points" / "mcp_server"
        main_py = project_root / "src" / pkg / "main.py"

        # Template base path for entry_point/mcp
        base = "entry_point/mcp"

        # Build context dict from module context
        ctx_dict = {}
        if builder.module_ctx:
            ctx_dict.update(builder.module_ctx.model_dump())

        # Add source files
        builder.add_file(src_dir / "__init__.py", builder.render(f"{base}/__init__.py.jinja2", ctx_dict), template_name=f"{base}/__init__.py.jinja2")
        builder.add_file(src_dir / "server.py", builder.render(f"{base}/server.py.jinja2", ctx_dict), template_name=f"{base}/server.py.jinja2")

        # Add test files
        builder.add_file(test_dir / "test_server.py", builder.render(f"{base}/test_server.py.jinja2", ctx_dict), template_name=f"{base}/test_server.py.jinja2", is_test=True)

        # Overwrite main.py
        builder.add_file(main_py, builder.render(f"{base}/entrypoint_main.py.jinja2", ctx_dict), template_name=f"{base}/entrypoint_main.py.jinja2", overwrite=True)

        # Add dependency
        builder.add_dependency("mcp>=1.0")
