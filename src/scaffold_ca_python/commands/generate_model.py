"""generate_model: scaffold a domain model class and test stub (T033)."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.tree import Tree

from scaffold_ca_python.core.module_builder import ModuleBuilder
from scaffold_ca_python.core.name_utils import ScaffoldError, validate_name
from scaffold_ca_python.core.project_detector import find_project_root
from scaffold_ca_python.factory import ModuleFactory
from scaffold_ca_python.factory.simple.model_factory import ModelFactory
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer

console = Console()

_REGISTRY: dict[str, type[ModuleFactory]] = {
    "model": ModelFactory,
}
_GM_HELP = "Scaffold a Pydantic v2 domain model and test stub. Alias 'gm'."
_GM_EPILOG = "Example:\n\n  * scaffold gm --name Order\n\n  * scaffold generate-model --name Order\n\n"


def _generate_model_impl(name: str, dry_run: bool) -> None:
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
    module_ctx = ModuleContext(name=name, layer=Layer.DOMAIN_MODEL, project=project_ctx)

    pkg = project_ctx.python_package
    src_dir = project_root / "src" / pkg / "domain" / "model"

    # --- Duplicate guard ---
    src_path = src_dir / f"{module_ctx.module_name}.py"
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
    factory_class = _REGISTRY["model"]
    factory = factory_class()

    # Invoke factory to build via ModuleBuilder
    factory.build(builder)

    # Persist all operations
    created = builder.persist()

    # --- Display results ---
    if dry_run:
        tree = Tree(f"[bold]{module_ctx.module_name}[/bold] (dry run)")
        for p in sorted(created):
            tree.add(str(p.relative_to(project_root)))
        console.print(tree)
        return

    msg = f"[green]✓[/green] Model [bold]{module_ctx.class_name}[/bold] created. Created {len(created)} file(s)."
    console.print(msg)


def register(app: typer.Typer) -> None:
    """Register gm / generate-model commands onto *app*."""

    # Both names route to the same handler; add further aliases by stacking @app.command before the def.
    @app.command(
        "generate-model",
        help=_GM_HELP,
        epilog=_GM_EPILOG,
    )
    @app.command("gm", hidden=True, help=_GM_HELP, epilog=_GM_EPILOG)
    def generate_model(
        ctx: typer.Context,
        name: Annotated[
            str | None, typer.Option("--name", help="Model name (PascalCase).", rich_help_panel="Required")
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
        """Scaffold a domain model in domain/model/."""
        if name is None:
            typer.echo(ctx.get_help())
            raise typer.Exit(0)
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
