"""EntryPointAgent factory implementation (T017)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scaffold_ca_python.core.project_detector import resolve_tests_root
from scaffold_ca_python.factory import ModuleFactory

if TYPE_CHECKING:
    from scaffold_ca_python.core.module_builder import ModuleBuilder


class EntryPointAgent(ModuleFactory):
    """Factory for Agent entry-point type."""

    def build(self, builder: ModuleBuilder) -> None:
        """Build Agent entry-point files and dependencies.

        Queues files:
        - src/infrastructure/entry_points/agent/__init__.py
        - src/infrastructure/entry_points/agent/agent.py
        - src/infrastructure/entry_points/agent/card.py
        - tests/infrastructure/entry_points/agent/test_agent.py

        Overwrites:
        - src/main.py (if exists)

        Injects:
        - a2a-sdk>=0.1
        """
        project_root = builder.project_root
        pkg = builder.project_ctx.python_package

        # Setup directory paths
        src_dir = project_root / "src" / pkg / "infrastructure" / "entry_points" / "agent"
        test_dir = resolve_tests_root(project_root) / "infrastructure" / "entry_points" / "agent"
        main_py = project_root / "src" / pkg / "main.py"

        # Template base path for entry_point/agent
        base = "entry_point/agent"

        # Build context dict from module context and params
        ctx_dict = {}
        if builder.module_ctx:
            ctx_dict.update(builder.module_ctx.model_dump())
        
        # Add enable_kafka and enable_mcp_client if present in params
        if builder.get_param("enable_kafka"):
            ctx_dict["enable_kafka"] = True
        if builder.get_param("enable_mcp_client"):
            ctx_dict["enable_mcp_client"] = True

        # Add source files
        builder.add_file(src_dir / "__init__.py", builder.render(f"{base}/__init__.py.jinja2", ctx_dict), template_name=f"{base}/__init__.py.jinja2")
        builder.add_file(src_dir / "agent.py", builder.render(f"{base}/agent.py.jinja2", ctx_dict), template_name=f"{base}/agent.py.jinja2")
        builder.add_file(src_dir / "card.py", builder.render(f"{base}/card.py.jinja2", ctx_dict), template_name=f"{base}/card.py.jinja2")

        # Add test files
        builder.add_file(test_dir / "test_agent.py", builder.render(f"{base}/test_agent.py.jinja2", ctx_dict), template_name=f"{base}/test_agent.py.jinja2", is_test=True)

        # Overwrite main.py
        builder.add_file(main_py, builder.render(f"{base}/entrypoint_main.py.jinja2", ctx_dict), template_name=f"{base}/entrypoint_main.py.jinja2", overwrite=True)

        # Add dependency
        builder.add_dependency("a2a-sdk>=0.1")
