"""generate_model: scaffold a domain model class and test stub (T037)."""

from __future__ import annotations

import importlib.resources
import tomllib
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.tree import Tree

from scaffold_ca_python.core.file_writer import FileWriter
from scaffold_ca_python.core.name_utils import ScaffoldError, validate_name
from scaffold_ca_python.core.project_detector import find_project_root
from scaffold_ca_python.core.template_renderer import TemplateRenderer
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.file_operation import CreateFile, FileOperation, GeneratedFile
from scaffold_ca_python.models.layer import Layer

console = Console()
renderer = TemplateRenderer()
writer = FileWriter()


def _generate_model_impl(name: str, dry_run: bool) -> None:
    try:
        validate_name(name)
    except ScaffoldError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from None

    try:
        project_root = find_project_root()
    except ScaffoldError:
        console.print(
            "[red]Error:[/red] No scaffold-ca-python project found. Run 'scaffold ca' first."
        )
        raise typer.Exit(code=1) from None

    project_ctx = _load_project_context(project_root)
    module_ctx = ModuleContext(name=name, layer=Layer.DOMAIN_MODEL, project=project_ctx)

    src_path = (
        project_root
        / "src"
        / project_ctx.python_package
        / "domain"
        / "model"
        / f"{module_ctx.module_name}.py"
    )
    test_path = (
        project_root
        / "tests"
        / "domain"
        / "model"
        / f"test_{module_ctx.module_name}.py"
    )

    if src_path.exists() or test_path.exists():
        existing = src_path if src_path.exists() else test_path
        console.print(
            f"[red]Error:[/red] File '{existing.relative_to(project_root)}' already exists. "
            "Use --force to overwrite.\n"
            "[dim]Hint:[/dim] Choose a different name or remove the existing file first."
        )
        raise typer.Exit(code=1)

    ctx_dict = module_ctx.model_dump()
    operations: list[FileOperation] = [
        CreateFile(file=GeneratedFile(
            path=src_path,
            content=renderer.render_string(_tmpl("model/model.py.jinja2"), ctx_dict),
            template_name="model/model.py.jinja2",
        )),
        CreateFile(file=GeneratedFile(
            path=test_path,
            content=renderer.render_string(_tmpl("model/test_model.py.jinja2"), ctx_dict),
            template_name="model/test_model.py.jinja2",
            is_test=True,
        )),
    ]

    if dry_run:
        preview = writer.execute(operations, dry_run=True)
        tree = Tree(f"[bold]{module_ctx.module_name}[/bold] (dry run)")
        for p in sorted(preview):
            tree.add(str(p.relative_to(project_root)))
        console.print(tree)
        return

    created = writer.execute(operations, dry_run=False)
    console.print(
        f"[green]✓[/green] Model [bold]{module_ctx.class_name}[/bold] created. "
        f"Created {len(created)} file(s)."
    )


def register(app: typer.Typer) -> None:
    """Register gm / generate-model commands onto *app*."""

    @app.command(
        "generate-model",
        help="Scaffold a Pydantic v2 domain model and test stub.",
        epilog="Example: scaffold gm --name Order",
    )
    def generate_model(
        name: Annotated[str, typer.Option("--name", help="Model name (PascalCase).", rich_help_panel="Required")],
        dry_run: Annotated[bool, typer.Option("--dry-run/--no-dry-run", help="Preview without writing.", rich_help_panel="Options", show_default=True)] = False,
    ) -> None:
        """Scaffold a domain model class inside domain/model/."""
        _generate_model_impl(name, dry_run)

    @app.command("gm", hidden=True, help="Alias for generate-model.")
    def gm(
        name: Annotated[str, typer.Option("--name", help="Model name.")],
        dry_run: Annotated[bool, typer.Option("--dry-run/--no-dry-run")] = False,
    ) -> None:
        """Alias for generate-model."""
        _generate_model_impl(name, dry_run)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_project_context(root: Path) -> ProjectContext:
    pyproject = root / "pyproject.toml"
    with pyproject.open("rb") as fh:
        data = tomllib.load(fh)
    section = data.get("tool", {}).get("scaffold-ca-python", {})
    return ProjectContext(
        name=section.get("name", root.name),
    )


def _tmpl(name: str) -> str:
    ref = importlib.resources.files("scaffold_ca_python.templates").joinpath(name)
    return ref.read_text(encoding="utf-8")
