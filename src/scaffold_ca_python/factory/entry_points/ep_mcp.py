"""EntryPointMcp factory implementation."""

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

        Always queues:
        - src/infrastructure/entry_points/mcp_server/__init__.py
        - src/infrastructure/entry_points/mcp_server/tools.py
        - tests/infrastructure/entry_points/mcp_server/test_tools.py

        Conditionally queues (when builder params are True):
        - resources.py + test_resources.py  (with_resources=True)
        - prompts.py   + test_prompts.py    (with_prompts=True)

        Injects: mcp>=1.0, uvicorn[standard]>=0.20, starlette>=0.40,
                 dependency-injector>=4.49.0, pydantic-settings>=2.13.1

        Sets builder params: scripts_entry_fn="main"
        """
        project_root = builder.project_root
        pkg = builder.project_ctx.python_package

        with_resources: bool = bool(builder.get_param("with_resources", False))
        with_prompts: bool = bool(builder.get_param("with_prompts", False))

        src_dir = project_root / "src" / pkg / "infrastructure" / "entry_points" / "mcp_server"
        test_dir = resolve_tests_root(project_root) / "infrastructure" / "entry_points" / "mcp_server"

        base = "entry_point/mcp"

        ctx_dict: dict[str, object] = {}
        if builder.module_ctx:
            ctx_dict.update(builder.module_ctx.model_dump())

        # Always-generated files
        builder.add_file(
            src_dir / "__init__.py",
            builder.render(f"{base}/__init__.py.jinja2", ctx_dict),
            template_name=f"{base}/__init__.py.jinja2",
        )
        builder.add_file(
            src_dir / "tools.py",
            builder.render(f"{base}/tools.py.jinja2", ctx_dict),
            template_name=f"{base}/tools.py.jinja2",
        )
        builder.add_file(
            test_dir / "test_tools.py",
            builder.render(f"{base}/test_tools.py.jinja2", ctx_dict),
            template_name=f"{base}/test_tools.py.jinja2",
            is_test=True,
        )

        # Optional: resources
        if with_resources:
            builder.add_file(
                src_dir / "resources.py",
                builder.render(f"{base}/resources.py.jinja2", ctx_dict),
                template_name=f"{base}/resources.py.jinja2",
            )
            builder.add_file(
                test_dir / "test_resources.py",
                builder.render(f"{base}/test_resources.py.jinja2", ctx_dict),
                template_name=f"{base}/test_resources.py.jinja2",
                is_test=True,
            )

        # Optional: prompts
        if with_prompts:
            builder.add_file(
                src_dir / "prompts.py",
                builder.render(f"{base}/prompts.py.jinja2", ctx_dict),
                template_name=f"{base}/prompts.py.jinja2",
            )
            builder.add_file(
                test_dir / "test_prompts.py",
                builder.render(f"{base}/test_prompts.py.jinja2", ctx_dict),
                template_name=f"{base}/test_prompts.py.jinja2",
                is_test=True,
            )

        # server.py at package root — replaces main.py (Phase 4 / T025)
        server_path = project_root / "src" / pkg / "server.py"
        main_py = project_root / "src" / pkg / "main.py"
        builder.add_file(
            server_path,
            builder.render(f"{base}/server.py.jinja2", ctx_dict),
            template_name=f"{base}/server.py.jinja2",
            overwrite=True,
        )
        builder.delete_file(main_py)

        # app.py composition root (Phase 5 / T031) — no overwrite guard
        app_py_path = project_root / "src" / pkg / "application" / "app.py"
        app_ctx: dict[str, object] = {**ctx_dict, "with_resources": with_resources, "with_prompts": with_prompts}
        builder.add_file(
            app_py_path,
            builder.render(f"{base}/app.py.jinja2", app_ctx),
            template_name=f"{base}/app.py.jinja2",
        )

        # Dependencies
        builder.add_dependency("mcp>=1.0")
        builder.add_dependency("uvicorn[standard]>=0.20")
        builder.add_dependency("starlette>=0.40")
        builder.add_dependency("dependency-injector>=4.49.0")
        builder.add_dependency("pydantic-settings>=2.13.1")

        # Signal to module_builder.persist() to update pyproject.toml scripts
        builder.add_param("scripts_entry", True)
        builder.add_param("scripts_entry_fn", "main")

