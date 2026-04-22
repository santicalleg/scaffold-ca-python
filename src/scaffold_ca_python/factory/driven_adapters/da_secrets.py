"""DrivenAdapterSecrets factory implementation (T027)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from scaffold_ca_python.core.project_detector import resolve_tests_root
from scaffold_ca_python.factory import ModuleFactory

if TYPE_CHECKING:
    from scaffold_ca_python.core.module_builder import ModuleBuilder


class DrivenAdapterSecrets(ModuleFactory):
    """Factory for Secrets driven-adapter type."""

    def build(self, builder: ModuleBuilder) -> None:
        """Build Secrets driven-adapter files and dependencies.

        Queues files:
        - src/infrastructure/driven_adapters/secrets/__init__.py
        - src/infrastructure/driven_adapters/secrets/secrets_adapter.py
        - tests/infrastructure/driven_adapters/secrets/test_secrets_adapter.py

        Injects:
        - boto3>=1.34
        """
        project_root = builder.project_root
        pkg = builder.project_ctx.python_package

        # Setup directory paths
        src_dir = project_root / "src" / pkg / "infrastructure" / "driven_adapters" / "secrets"
        test_dir = resolve_tests_root(project_root) / "infrastructure" / "driven_adapters" / "secrets"

        # Template base path for driven_adapter/secrets
        base = "driven_adapter/secrets"

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
            src_dir / "secrets_adapter.py",
            builder.render(f"{base}/secrets_adapter.py.jinja2", ctx_dict),
            template_name=f"{base}/secrets_adapter.py.jinja2",
        )

        # Add test files
        builder.add_file(
            test_dir / "test_secrets_adapter.py",
            builder.render(f"{base}/test_secrets_adapter.py.jinja2", ctx_dict),
            template_name=f"{base}/test_secrets_adapter.py.jinja2",
            is_test=True,
        )

        # Add dependency
        builder.add_dependency("boto3>=1.34")
