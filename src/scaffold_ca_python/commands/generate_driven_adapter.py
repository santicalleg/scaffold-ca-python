"""generate_driven_adapter: scaffold a driven adapter and test stub (T030)."""

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
from scaffold_ca_python.factory.driven_adapters.da_generic import DrivenAdapterGeneric
from scaffold_ca_python.factory.driven_adapters.da_rest_consumer import DrivenAdapterRestConsumer
from scaffold_ca_python.factory.driven_adapters.da_secrets import DrivenAdapterSecrets
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer

console = Console()

_REGISTRY: dict[str, type[ModuleFactory]] = {
    "rest-consumer": DrivenAdapterRestConsumer,
    "secrets": DrivenAdapterSecrets,
    "generic": DrivenAdapterGeneric,
}

_GDA_HELP = "Scaffold a driven adapter and test stub. Alias 'gda'."
_GDA_EPILOG = (
    "Types:\n\n"
    "  * rest-consumer    HTTP outbound client (httpx)\n\n"
    "  * secrets          AWS Secrets Manager (boto3)\n\n"
    "  * generic          Custom adapter (--name required)\n\n"
    " ==================================================\n\n"
    "Examples:\n\n"
    "  * scaffold gda --type rest-consumer\n\n"
    "  * scaffold generate-driven-adapter --type generic --name MyAdapter\n\n"
)


def _generate_driven_adapter_impl(type_: str, name: str | None, dry_run: bool) -> None:  # noqa: ANN001
    # --- Validate type ---
    if type_ not in _REGISTRY:
        console.print(f"[red]Error:[/red] Unknown type '{type_}'. Allowed: {', '.join(_REGISTRY.keys())}.")
        raise typer.Exit(code=1) from None

    # --- Validate name requirement for generic ---
    if type_ == "generic" and not name:
        console.print("[red]Error:[/red] --name is required when --type is generic.")
        raise typer.Exit(code=1) from None

    # --- Validate name if provided ---
    if name:
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

    # --- Determine module context and subdir from type/name ---
    if type_ == "rest-consumer":
        subdir = "rest_consumer"
        module_ctx = ModuleContext(name="rest_consumer", layer=Layer.DRIVEN_ADAPTERS, project=project_ctx)
    elif type_ == "secrets":
        subdir = "secrets"
        module_ctx = ModuleContext(name="secrets", layer=Layer.DRIVEN_ADAPTERS, project=project_ctx)
    else:  # generic
        assert name is not None  # validated above
        subdir = to_snake_case(name)
        module_ctx = ModuleContext(name=name, layer=Layer.DRIVEN_ADAPTERS, project=project_ctx)

    pkg = project_ctx.python_package
    src_dir = project_root / "src" / pkg / "infrastructure" / "driven_adapters" / subdir

    # --- Duplicate guard ---
    if src_dir.exists():
        console.print(
            f"[red]Error:[/red] Directory '{src_dir.relative_to(project_root)}/' already exists.\n"
            "[dim]Hint:[/dim] Choose a different name or remove the existing directory first."
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
    factory_class = _REGISTRY[type_]
    factory = factory_class()

    # Invoke factory to build via ModuleBuilder
    factory.build(builder)

    # Persist all operations
    created = builder.persist()

    # --- Display results ---
    if dry_run:
        tree = Tree(f"[bold]{subdir}[/bold] (dry run)")
        for p in sorted(created):
            tree.add(str(p.relative_to(project_root)))
        console.print(tree)
        if builder._dependencies:
            console.print(f"[dim]Would add to [project.dependencies]: {', '.join(builder._dependencies)}[/dim]")
        return

    console.print(f"[green]✓[/green] Driven adapter [bold]{subdir}[/bold] created. Created {len(created)} file(s).")


def register(app: typer.Typer) -> None:
    """Register gda / generate-driven-adapter commands onto *app*."""

    @app.command(
        "generate-driven-adapter",
        help=_GDA_HELP,
        epilog=_GDA_EPILOG,
    )
    @app.command("gda", hidden=True, help=_GDA_HELP, epilog=_GDA_EPILOG)
    def generate_driven_adapter(
        ctx: typer.Context,
        type_: Annotated[
            str | None,
            typer.Option(
                "--type",
                help="Adapter type: rest-consumer, secrets, generic.",
                rich_help_panel="Required",
            ),
        ] = None,
        name: Annotated[
            str | None,
            typer.Option(
                "--name",
                help="Adapter name (required for --type generic).",
                rich_help_panel="Options",
            ),
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
        """Scaffold a driven adapter inside infrastructure/driven_adapters/."""
        if type_ is None:
            typer.echo(ctx.get_help())
            raise typer.Exit(0)
        _generate_driven_adapter_impl(type_, name, dry_run)


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
