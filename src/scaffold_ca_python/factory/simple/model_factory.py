"""ModelFactory implementation (T033)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scaffold_ca_python.core.project_detector import resolve_tests_root
from scaffold_ca_python.factory import ModuleFactory

if TYPE_CHECKING:
    from scaffold_ca_python.core.module_builder import ModuleBuilder


class ModelFactory(ModuleFactory):
    """Factory for domain model generation."""

    def build(self, builder: ModuleBuilder) -> None:
        """Build domain model files.

        Queues files:
        - src/domain/model/{module_name}.py
        - tests/domain/model/test_{module_name}.py

        No dependencies injected (pydantic is already a project dependency).
        """
        project_root = builder.project_root
        pkg = builder.project_ctx.python_package

        # Get module name from module context
        module_name = builder.module_ctx.module_name if builder.module_ctx else "model"

        # Setup directory paths
        src_dir = project_root / "src" / pkg / "domain" / "model"
        test_dir = resolve_tests_root(project_root) / "domain" / "model"

        # Template base path
        base = "model"

        # Build context dict from module context
        ctx_dict = {}
        if builder.module_ctx:
            ctx_dict.update(builder.module_ctx.model_dump())

        # Add source file
        builder.add_file(
            src_dir / f"{module_name}.py",
            builder.render(f"{base}/model.py.jinja2", ctx_dict),
            template_name=f"{base}/model.py.jinja2",
        )

        # Add test file
        builder.add_file(
            test_dir / f"test_{module_name}.py",
            builder.render(f"{base}/test_model.py.jinja2", ctx_dict),
            template_name=f"{base}/test_model.py.jinja2",
            is_test=True,
        )
