"""EntryPointRestApi factory implementation (T015)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scaffold_ca_python.core.project_detector import resolve_tests_root
from scaffold_ca_python.factory import ModuleFactory

if TYPE_CHECKING:
    from scaffold_ca_python.core.module_builder import ModuleBuilder


class EntryPointRestApi(ModuleFactory):
    """Factory for REST API entry-point type."""

    def build(self, builder: ModuleBuilder) -> None:
        """Build REST API entry-point files and dependencies.

        Queues files:
        - src/application/app.py (application factory)
        - src/infrastructure/entry_points/api/v1/__init__.py
        - src/infrastructure/entry_points/api/v1/rest_controller.py
        - src/infrastructure/entry_points/api/v1/exception_handler.py
        - src/server.py (entrypoint)
        - tests/application/test_app.py
        - tests/infrastructure/entry_points/api/v1/test_rest_controller.py
        - tests/infrastructure/entry_points/api/v1/test_server.py
        - tests/infrastructure/entry_points/api/v1/test_exception_handler.py

        Deletes:
        - src/main.py

        Injects:
        - fastapi[standard]>=0.135.2
        - uvicorn[standard]>=0.20
        - dependency-injector>=4.49.0
        - pydantic-settings>=2.13.1
        """
        project_root = builder.project_root
        pkg = builder.project_ctx.python_package

        # Setup directory paths
        src_dir = project_root / "src" / pkg / "infrastructure" / "entry_points" / "api" / "v1"
        test_dir = resolve_tests_root(project_root) / "infrastructure" / "entry_points" / "api" / "v1"
        app_py_path = project_root / "src" / pkg / "application" / "app.py"
        server_path = project_root / "src" / pkg / "server.py"
        test_app_path = resolve_tests_root(project_root) / "application" / "test_app.py"
        main_py = project_root / "src" / pkg / "main.py"

        # Template base path for entry_point/restapi
        base = "entry_point/restapi"

        # Build context dict from module context
        ctx_dict = {
            **builder.module_ctx.model_dump(),
        } if builder.module_ctx else {}

        # Add source files
        builder.add_file(app_py_path, builder.render(f"{base}/app.py.jinja2", ctx_dict), template_name=f"{base}/app.py.jinja2")
        builder.add_file(src_dir / "__init__.py", builder.render(f"{base}/__init__.py.jinja2", ctx_dict), template_name=f"{base}/__init__.py.jinja2")
        builder.add_file(src_dir / "rest_controller.py", builder.render(f"{base}/rest_controller.py.jinja2", ctx_dict), template_name=f"{base}/rest_controller.py.jinja2")
        builder.add_file(src_dir / "exception_handler.py", builder.render(f"{base}/exception_handler.py.jinja2", ctx_dict), template_name=f"{base}/exception_handler.py.jinja2")
        builder.add_file(server_path, builder.render(f"{base}/server.py.jinja2", ctx_dict), template_name=f"{base}/server.py.jinja2")

        # Add test files
        builder.add_file(test_dir / "test_rest_controller.py", builder.render(f"{base}/test_rest_controller.py.jinja2", ctx_dict), template_name=f"{base}/test_rest_controller.py.jinja2", is_test=True)
        builder.add_file(test_dir / "test_server.py", builder.render(f"{base}/test_server.py.jinja2", ctx_dict), template_name=f"{base}/test_server.py.jinja2", is_test=True)
        builder.add_file(test_dir / "test_exception_handler.py", builder.render(f"{base}/test_exception_handler.py.jinja2", ctx_dict), template_name=f"{base}/test_exception_handler.py.jinja2", is_test=True)
        builder.add_file(test_app_path, builder.render(f"{base}/test_app.py.jinja2", ctx_dict), template_name=f"{base}/test_app.py.jinja2", is_test=True)

        # Delete main.py
        builder.delete_file(main_py)

        # Add dependencies
        deps = [
            "fastapi[standard]>=0.135.2",
            "uvicorn[standard]>=0.20",
            "dependency-injector>=4.49.0",
            "pydantic-settings>=2.13.1",
        ]
        for dep in deps:
            builder.add_dependency(dep)

        # Set scripts param to indicate main.py was removed and scripts need updating
        builder.add_param("scripts_entry", True)
