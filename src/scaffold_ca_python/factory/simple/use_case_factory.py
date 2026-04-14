"""UseCaseFactory implementation (T035)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scaffold_ca_python.core.name_utils import to_snake_case
from scaffold_ca_python.core.project_detector import resolve_tests_root
from scaffold_ca_python.factory import ModuleFactory

if TYPE_CHECKING:
    from scaffold_ca_python.core.module_builder import ModuleBuilder


class UseCaseFactory(ModuleFactory):
    """Factory for domain use case generation."""

    def build(self, builder: ModuleBuilder) -> None:
        """Build domain use case files.

        Queues files:
        - src/domain/usecase/{snake_name}.py
        - tests/domain/usecase/test_{snake_name}.py

        No dependencies injected (async/await are built-in).
        """
        project_root = builder.project_root
        pkg = builder.project_ctx.python_package

        # Get use case name from module context and convert to snake_case
        usecase_name = builder.module_ctx.name if builder.module_ctx else "UseCase"
        snake_name = to_snake_case(usecase_name)

        # Setup directory paths
        src_dir = project_root / "src" / pkg / "domain" / "usecase"
        test_dir = resolve_tests_root(project_root) / "domain" / "usecase"

        # Template base path
        base = "use_case"

        # Build context dict from module context
        ctx_dict = {}
        if builder.module_ctx:
            ctx_dict.update(builder.module_ctx.model_dump())

        # Add source file
        builder.add_file(
            src_dir / f"{snake_name}.py",
            builder.render(f"{base}/use_case.py.jinja2", ctx_dict),
            template_name=f"{base}/use_case.py.jinja2",
        )

        # Add test file
        builder.add_file(
            test_dir / f"test_{snake_name}.py",
            builder.render(f"{base}/test_use_case.py.jinja2", ctx_dict),
            template_name=f"{base}/test_use_case.py.jinja2",
            is_test=True,
        )
