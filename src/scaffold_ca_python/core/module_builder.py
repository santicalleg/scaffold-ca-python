"""ModuleBuilder orchestration layer for factory-based module generation."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from scaffold_ca_python.core.file_writer import FileWriter
from scaffold_ca_python.core.pyproject_writer import (
    dry_run_inject,
    dry_run_scripts_update,
    inject_dependencies,
    update_project_scripts,
)
from scaffold_ca_python.core.template_renderer import TemplateRenderer
from scaffold_ca_python.models.file_operation import CreateFile, DeleteFile, FileOperation, GeneratedFile

if TYPE_CHECKING:
    from scaffold_ca_python.models.context import ModuleContext, ProjectContext


class ModuleBuilder:
    """Collect and persist module generation operations.

    Factory implementations should only interact with this class, not with lower-level
    infrastructure helpers such as FileWriter/TemplateRenderer/pyproject_writer.
    """

    def __init__(
        self,
        *,
        project_root: Path,
        project_ctx: ProjectContext,
        module_ctx: ModuleContext | None = None,
        dry_run: bool = False,
        file_writer: FileWriter | None = None,
        template_renderer: TemplateRenderer | None = None,
    ) -> None:
        self.project_root = project_root
        self.project_ctx = project_ctx
        self.module_ctx = module_ctx
        self.dry_run = dry_run

        self._file_writer = file_writer or FileWriter()
        self._renderer = template_renderer or TemplateRenderer()

        self._operations: list[FileOperation] = []
        self._dependencies: list[str] = []
        self._params: dict[str, object] = {}

    def add_file(
        self,
        path: Path,
        content: str,
        *,
        template_name: str,
        is_test: bool = False,
        overwrite: bool = False,
    ) -> None:
        """Queue a file creation operation."""
        self._operations.append(
            CreateFile(
                file=GeneratedFile(
                    path=path,
                    content=content,
                    template_name=template_name,
                    is_test=is_test,
                    overwrite=overwrite,
                )
            )
        )

    def delete_file(self, path: Path) -> None:
        """Queue a file deletion operation."""
        self._operations.append(DeleteFile(path=path))

    def render(self, template_name: str, context: BaseModel | dict[str, Any]) -> str:
        """Render a template through the shared renderer."""
        return self._renderer.render(template_name, context)

    def add_dependency(self, package: str) -> None:
        """Queue a package dependency to inject into pyproject.toml."""
        self._dependencies.append(package)

    def add_param(self, key: str, value: object) -> None:
        """Store an ad-hoc value used by factories/commands."""
        self._params[key] = value

    def get_param(self, key: str, default: object | None = None) -> object | None:
        """Read a previously stored parameter value."""
        return self._params.get(key, default)

    def persist(self) -> list[Path]:
        """Persist queued file and dependency operations.

        In dry-run mode no writes occur; the method returns the paths that would be
        affected by file operations.
        """
        paths = self._file_writer.execute(self._operations, dry_run=self.dry_run)

        if self._dependencies:
            if self.dry_run:
                dry_run_inject(self.project_root, self._dependencies)
            else:
                inject_dependencies(self.project_root, self._dependencies)

        # Optional script update hook used by entry-point factory implementations.
        if bool(self._params.get("scripts_entry", False)):
            pkg = self.project_ctx
            entry_fn: str = str(self._params.get("scripts_entry_fn", "start_server"))
            if self.dry_run:
                dry_run_scripts_update(self.project_root, pkg, entry_fn)
            else:
                update_project_scripts(self.project_root, pkg, entry_fn)

        return paths
