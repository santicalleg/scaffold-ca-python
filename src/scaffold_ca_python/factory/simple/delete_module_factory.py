"""DeleteModuleFactory implementation (T039)."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from scaffold_ca_python.core.name_utils import to_snake_case
from scaffold_ca_python.core.project_detector import resolve_tests_root
from scaffold_ca_python.factory import ModuleFactory

if TYPE_CHECKING:
    from scaffold_ca_python.core.module_builder import ModuleBuilder


class DeleteModuleFactory(ModuleFactory):
    """Factory for module deletion."""

    def build(self, builder: ModuleBuilder) -> None:
        """Build deletion operations for a module.

        Finds and deletes modules across:
        - domain/model/<snake>.py
        - domain/usecase/<snake>.py
        - infrastructure/driven_adapters/<snake>/
        - infrastructure/entry_points/<snake>/
        - infrastructure/helpers/<snake>/
        """
        project_root = builder.project_root
        pkg = builder.project_ctx.python_package

        # Get module name and convert to snake_case
        module_name = builder.module_ctx.name if builder.module_ctx else "Module"
        snake_name = to_snake_case(module_name)

        src_root = project_root / "src" / pkg
        tests_root = resolve_tests_root(project_root)

        # Build list of possible module locations
        candidates: list[tuple[Path, Path | None]] = []

        # Single-file layers (domain/model, domain/usecase)
        model_src = src_root / "domain" / "model" / f"{snake_name}.py"
        model_test = tests_root / "domain" / "model" / f"test_{snake_name}.py"
        usecase_src = src_root / "domain" / "usecase" / f"{snake_name}.py"
        usecase_test = tests_root / "domain" / "usecase" / f"test_{snake_name}.py"
        for src_rel, test_rel in [
            (model_src, model_test),
            (usecase_src, usecase_test),
        ]:
            if src_rel.exists():
                candidates.append((src_rel, test_rel if test_rel.exists() else None))

        # Directory-based layers (infrastructure sub-dirs)
        for src_rel, test_rel in [
            (
                src_root / "infrastructure" / "driven_adapters" / snake_name,
                tests_root / "infrastructure" / "driven_adapters" / snake_name,
            ),
            (
                src_root / "infrastructure" / "entry_points" / snake_name,
                tests_root / "infrastructure" / "entry_points" / snake_name,
            ),
            (
                src_root / "infrastructure" / "helpers" / snake_name,
                tests_root / "infrastructure" / "helpers" / snake_name,
            ),
        ]:
            if src_rel.exists():
                candidates.append((src_rel, test_rel if test_rel.exists() else None))

        # Delete all found modules
        if not builder.dry_run:
            for src_path, test_path in candidates:
                if src_path.is_file():
                    src_path.unlink()
                elif src_path.is_dir():
                    shutil.rmtree(src_path)

                if test_path:
                    if test_path.is_file():
                        test_path.unlink()
                    elif test_path.is_dir():
                        shutil.rmtree(test_path)
