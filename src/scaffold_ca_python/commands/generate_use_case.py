"""generate_use_case: scaffold an async use case class and test stub (T035)."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.tree import Tree

from scaffold_ca_python.core.module_builder import ModuleBuilder
from scaffold_ca_python.core.name_utils import ScaffoldError, to_snake_case, validate_name
from scaffold_ca_python.core.project_detector import find_project_root
from scaffold_ca_python.factory import ModuleFactory
from scaffold_ca_python.factory.simple.use_case_factory import UseCaseFactory
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer

console = Console()

_REGISTRY: dict[str, type[ModuleFactory]] = {
    "use_case": UseCaseFactory,
}
_GUC_HELP = "Scaffold a use case in domain/usecase/. Alias 'guc'."
_GUC_EPILOG = (
    "Example:\n\n"
    "  * scaffold guc --name CreateOrder\n\n"
    "  * scaffold generate-use-case --name CreateOrder\n\n"
)

def _generate_use_case_impl(name: str, dry_run: bool) -> None:
    # --- Validate name ---
    try:
        validate_name(name)
    except ScaffoldError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from None

    # --- Locate project root ---
    try:
        project_root = find_project_root()
    except ScaffoldError:
        console.print("[red]Error:[/red] No scaffold-ca-python project found. Run 'scaffold ca' first.")
        raise typer.Exit(code=1) from None

    project_ctx = _load_project_context(project_root)
    module_ctx = ModuleContext(name=name, layer=Layer.DOMAIN_USECASE, project=project_ctx)

    pkg = project_ctx.python_package
    snake = to_snake_case(name)
    src_path = project_root / "src" / pkg / "domain" / "usecase" / f"{snake}.py"

    # --- Duplicate guard ---
    if src_path.exists():
        console.print(
            f"[red]Error:[/red] File '{src_path.relative_to(project_root)}' already exists.\n"
            "[dim]Hint:[/dim] Choose a different name or remove the existing file first."
        )
        raise typer.Exit(code=1) from None

    # --- Create builder and get factory from registry ---
    builder = ModuleBuilder(
        project_root=project_root,
        project_ctx=project_ctx,
        module_ctx=module_ctx,
        dry_run=dry_run,
    )

    # Get factory class and instantiate
    factory_class = _REGISTRY["use_case"]
    factory = factory_class()

    # Invoke factory to build via ModuleBuilder
    factory.build(builder)

    # Persist all operations
    created = builder.persist()

    # --- Display results ---
    if dry_run:
        tree = Tree(f"[bold]{snake}[/bold] (dry run)")
        for p in sorted(created):
            tree.add(str(p.relative_to(project_root)))
        console.print(tree)
        return

    console.print(f"[green]✓[/green] Use case [bold]{module_ctx.class_name}UseCase[/bold] created. Created {len(created)} file(s).")


def register(app: typer.Typer) -> None:
    """Register guc / generate-use-case commands onto *app*."""

    @app.command(
        "generate-use-case",
        help=_GUC_HELP,
        epilog=_GUC_EPILOG,
    )
    @app.command("guc", hidden=True, help=_GUC_HELP, epilog=_GUC_EPILOG)
    def generate_use_case(
        ctx: typer.Context,
        name: Annotated[
            str | None, typer.Option("--name", help="Use case name (PascalCase).", rich_help_panel="Required")
        ] = None,
        dry_run: Annotated[
            bool,
            typer.Option(
                "--dry-run/--no-dry-run",
                help="Preview without writing.",
                rich_help_panel="Options",
                show_default=True,
            ),
        ] = False,
    ) -> None:
        """Scaffold a use case in domain/usecase/."""
        if name is None:
            typer.echo(ctx.get_help())
            raise typer.Exit(0)
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
    )
