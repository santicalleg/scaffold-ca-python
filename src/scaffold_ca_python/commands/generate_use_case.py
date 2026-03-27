"""generate_use_case: scaffold an async use case class and test stub (T042)."""

from __future__ import annotations

import importlib.resources
import tomllib
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.tree import Tree

from scaffold_ca_python.core.file_writer import FileWriter
from scaffold_ca_python.core.name_utils import ScaffoldError, to_snake_case, validate_name
from scaffold_ca_python.core.project_detector import find_project_root
from scaffold_ca_python.core.template_renderer import TemplateRenderer
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.file_operation import CreateFile, FileOperation, GeneratedFile
from scaffold_ca_python.models.layer import Layer

console = Console()
renderer = TemplateRenderer()
writer = FileWriter()


def _generate_use_case_impl(name: str, dry_run: bool) -> None:
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
    module_ctx = ModuleContext(name=name, layer=Layer.DOMAIN_USECASE, project=project_ctx)

    snake = to_snake_case(name)
    src_path = (
        project_root
        / "src"
        / project_ctx.python_package
        / "domain"
        / "usecase"
        / f"{snake}.py"
    )
    test_path = (
        project_root
        / "tests"
        / "domain"
        / "usecase"
        / f"test_{snake}.py"
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
            content=renderer.render_string(_tmpl("use_case/use_case.py.jinja2"), ctx_dict),
            template_name="use_case/use_case.py.jinja2",
        )),
        CreateFile(file=GeneratedFile(
            path=test_path,
            content=renderer.render_string(_tmpl("use_case/test_use_case.py.jinja2"), ctx_dict),
            template_name="use_case/test_use_case.py.jinja2",
            is_test=True,
        )),
    ]

    if dry_run:
        preview = writer.execute(operations, dry_run=True)
        tree = Tree(f"[bold]{snake}[/bold] (dry run)")
        for p in sorted(preview):
            tree.add(str(p.relative_to(project_root)))
        console.print(tree)
        return

    created = writer.execute(operations, dry_run=False)
    console.print(
        f"[green]✓[/green] Use case [bold]{module_ctx.class_name}UseCase[/bold] created. "
        f"Created {len(created)} file(s)."
    )


def register(app: typer.Typer) -> None:
    """Register guc / generate-use-case commands onto *app*."""

    @app.command(
        "generate-use-case",
        help="Scaffold an async use case class and test stub.",
        epilog="Example: scaffold guc --name CreateOrder",
    )
    def generate_use_case(
        name: Annotated[str, typer.Option("--name", help="Use case name (PascalCase).", rich_help_panel="Required")],
        dry_run: Annotated[bool, typer.Option("--dry-run/--no-dry-run", help="Preview without writing.", rich_help_panel="Options", show_default=True)] = False,
    ) -> None:
        """Scaffold an async use case inside domain/usecase/."""
        _generate_use_case_impl(name, dry_run)

    @app.command("guc", hidden=True, help="Alias for generate-use-case.")
    def guc(
        name: Annotated[str, typer.Option("--name", help="Use case name.")],
        dry_run: Annotated[bool, typer.Option("--dry-run/--no-dry-run")] = False,
    ) -> None:
        """Alias for generate-use-case."""
        _generate_use_case_impl(name, dry_run)


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
        package=section.get("package", "com.example"),
    )


def _tmpl(name: str) -> str:
    ref = importlib.resources.files("scaffold_ca_python.templates").joinpath(name)
    return ref.read_text(encoding="utf-8")
