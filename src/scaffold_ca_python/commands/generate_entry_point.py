"""generate_entry_point: scaffold an entry-point adapter and test stub (T055)."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path
from typing import Annotated

import typer
import yaml
from rich.console import Console
from rich.tree import Tree

from scaffold_ca_python.core.module_builder import ModuleBuilder
from scaffold_ca_python.core.name_utils import ScaffoldError
from scaffold_ca_python.core.project_detector import find_project_root
from scaffold_ca_python.factory import ModuleFactory
from scaffold_ca_python.factory.entry_points.ep_agent import EntryPointAgent
from scaffold_ca_python.factory.entry_points.ep_generic import EntryPointGeneric
from scaffold_ca_python.factory.entry_points.ep_mcp import EntryPointMcp
from scaffold_ca_python.factory.entry_points.ep_restapi import EntryPointRestApi
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer

console = Console()

_REGISTRY: dict[str, type[ModuleFactory]] = {
    "restapi": EntryPointRestApi,
    "agent": EntryPointAgent,
    "mcp": EntryPointMcp,
    "generic": EntryPointGeneric,
}

_TYPE_HELP = "Entry-point type: restapi, agent, mcp, generic."
_SWAGGER_HELP = "Path to OpenAPI YAML/JSON (restapi only)."
_KAFKA_HELP = "Add async Kafka consumer stub (agent type only)."
_MCP_CLIENT_HELP = "Add MCP tool-call client stub (agent type only)."
_GEP_HELP = "Scaffold an entry-point adapter and test stub. Alias 'gep'."
_GEP_EPILOG = (
    "Types:\n\n"
    "  * restapi    FastAPI REST API entry point\n\n"
    "  * agent      A2A agent entry point\n\n"
    "  * mcp        MCP server entry point\n\n"
    "  * generic    Plain entry point\n\n"
    " ==================================================\n\n"
    "Notes: --enable-kafka and --enable-mcp-client are agent type only.\n\n"
    " ==================================================\n\n"
    "Examples:\n\n"
    "  * scaffold gep --type restapi\n\n"
    "  * scaffold gep --type agent --enable-kafka\n\n"
    "  * scaffold gep --type mcp\n\n"
    "  * scaffold generate-entry-point --type generic\n"
)


def _load_project_context(project_root: Path) -> ProjectContext:
    """Load project context from pyproject.toml."""
    pyproject_path = project_root / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    project_name = data.get("project", {}).get("name", "project").replace("-", "_")
    return ProjectContext(name=project_name)


def _generate_entry_point_impl(
    type_: str,
    swagger: str | None,
    enable_kafka: bool,
    enable_mcp_client: bool,
    with_resources: bool,
    with_prompts: bool,
    dry_run: bool,
) -> None:
    # --- Validate type ---
    if type_ not in _REGISTRY:
        console.print(f"[red]Error:[/red] Unknown type '{type_}'. Allowed: {', '.join(_REGISTRY.keys())}.")
        raise typer.Exit(code=1) from None

    # --- Flag compatibility checks ---
    if swagger and type_ != "restapi":
        console.print("[red]Error:[/red] --swagger is only valid with --type restapi.")
        raise typer.Exit(code=1) from None

    if enable_mcp_client and type_ == "mcp":
        console.print("[red]Error:[/red] --enable-mcp-client is not valid with --type mcp.")
        raise typer.Exit(code=1) from None

    if (with_resources or with_prompts) and type_ != "mcp":
        console.print("[red]Error:[/red] --with-resources and --with-prompts are only valid with --type mcp.")
        raise typer.Exit(code=1) from None

    # --- Validate swagger path ---
    routes: list[tuple[str, str]] = []
    if swagger:
        swagger_path = Path(swagger)
        if not swagger_path.exists():
            console.print(f"[red]Error:[/red] Swagger file '{swagger}' not found.")
            raise typer.Exit(code=1) from None
        routes = _parse_swagger(swagger_path)

    # --- Locate project root ---
    try:
        project_root = find_project_root()
    except ScaffoldError:
        console.print("[red]Error:[/red] No scaffold-ca-python project found. Run 'scaffold ca' first.")
        raise typer.Exit(code=1) from None

    project_ctx = _load_project_context(project_root)

    # --- Compatibility guard (restapi vs mcp/agent) --------------------------
    if type_ == "restapi":
        pkg_ep = project_root / "src" / project_ctx.python_package / "infrastructure" / "entry_points"
        for incompatible in ("mcp_server", "agent"):
            conflict_dir = pkg_ep / incompatible
            if conflict_dir.exists():
                console.print(
                    f"[red]Error:[/red] Incompatible entry point '[bold]{incompatible}[/bold]' "
                    f"already exists at: {conflict_dir.relative_to(project_root)}\n"
                    "[dim]Hint:[/dim] A project may have only one entry-point type. "
                    f"Remove '{conflict_dir.relative_to(project_root)}' before adding restapi."
                )
                raise typer.Exit(code=1) from None

    if type_ in ("mcp", "agent"):
        restapi_dir = project_root / "src" / project_ctx.python_package / "infrastructure" / "entry_points" / "api"
        if restapi_dir.exists():
            console.print(
                f"[red]Error:[/red] Incompatible entry point '[bold]restapi[/bold]' "
                f"already exists at: {restapi_dir.relative_to(project_root)}\n"
                "[dim]Hint:[/dim] A project may have only one entry-point type. "
                f"Remove '{restapi_dir.relative_to(project_root)}' before adding {type_}."
            )
            raise typer.Exit(code=1) from None

    # --- Determine subdir and module context ---
    if type_ == "restapi":
        subdir = "api/v1"
    elif type_ == "mcp":
        subdir = "mcp_server"
    else:
        subdir = type_
    module_ctx = ModuleContext(
        name=type_.replace("-", "_"),
        layer=Layer.ENTRY_POINTS,
        project=project_ctx,
        subtype=type_,
    )

    pkg = project_ctx.python_package
    src_dir = project_root / "src" / pkg / "infrastructure" / "entry_points" / subdir

    # --- Duplicate guard ---
    if src_dir.exists():
        console.print(
            f"[red]Error:[/red] Directory '{src_dir.relative_to(project_root)}/' already exists.\n"
            "[dim]Hint:[/dim] Choose a different type or remove the existing directory first."
        )
        raise typer.Exit(code=1) from None

    # --- Create builder and get factory from registry ---
    builder = ModuleBuilder(
        project_root=project_root,
        project_ctx=project_ctx,
        module_ctx=module_ctx,
        dry_run=dry_run,
    )

    # Add flags to builder params for factory use
    builder.add_param("routes", routes)
    builder.add_param("enable_kafka", enable_kafka)
    builder.add_param("enable_mcp_client", enable_mcp_client)
    builder.add_param("with_resources", with_resources)
    builder.add_param("with_prompts", with_prompts)

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

        # Check if dependencies were collected by looking at builder internals
        if builder._dependencies:
            console.print(f"[dim]Would add to [project.dependencies]: {', '.join(builder._dependencies)}[/dim]")

        if type_ == "restapi":
            main_py = project_root / "src" / pkg / "main.py"
            if main_py.exists():
                console.print(f"[dim]Would delete: src/{pkg}/main.py[/dim]")
            console.print(f'[dim]Would update [project.scripts]: {pkg} = "{pkg}.server:start_server"[/dim]')
        else:
            console.print(f"[yellow]⚠[/yellow] main.py will be replaced with {type_} entrypoint.")
        return

    console.print(f"[green]✓[/green] Entry point [bold]{subdir}[/bold] created. Created {len(created)} file(s).")

    # --- Show results for special handling ---
    if type_ == "restapi":
        main_py = project_root / "src" / pkg / "main.py"
        if main_py.exists():
            console.print(f"[green]\u2713[/green] Deleted src/{pkg}/main.py")
        console.print(f'[green]\u2713[/green] Updated [project.scripts]: {pkg} = "{pkg}.server:start_server"')
    else:
        console.print(f"[yellow]⚠[/yellow] main.py replaced with {type_} entrypoint.")


def _parse_swagger(path: Path) -> list[tuple[str, str]]:
    """Parse an OpenAPI YAML/JSON file and return (path, method) pairs."""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in (".yaml", ".yml"):
        raw: object = yaml.safe_load(text)
    else:
        raw = json.loads(text)
    if not isinstance(raw, dict):
        return []
    paths_value = raw.get("paths", {})
    if not isinstance(paths_value, dict):
        return []
    result: list[tuple[str, str]] = []
    for route_path, methods in paths_value.items():
        if isinstance(methods, dict):
            for method in methods:
                if method.lower() in ("get", "post", "put", "patch", "delete", "head", "options"):
                    result.append((str(route_path), method.lower()))
    return result


def register(app: typer.Typer) -> None:
    """Register gep / generate-entry-point commands onto *app*."""

    @app.command(
        "generate-entry-point",
        help=_GEP_HELP,
        epilog=_GEP_EPILOG,
    )
    @app.command("gep", hidden=True, help=_GEP_HELP, epilog=_GEP_EPILOG)
    def generate_entry_point(
        ctx: typer.Context,
        type_: Annotated[str | None, typer.Option("--type", help=_TYPE_HELP, rich_help_panel="Required")] = None,
        swagger: Annotated[str | None, typer.Option("--swagger", help=_SWAGGER_HELP, rich_help_panel="Options")] = None,
        enable_kafka: Annotated[
            bool,
            typer.Option(
                "--enable-kafka/--no-enable-kafka",
                help=_KAFKA_HELP,
                rich_help_panel="Options",
                show_default=True,
            ),
        ] = False,
        enable_mcp_client: Annotated[
            bool,
            typer.Option(
                "--enable-mcp-client/--no-enable-mcp-client",
                help=_MCP_CLIENT_HELP,
                rich_help_panel="Options",
                show_default=True,
            ),
        ] = False,
        with_resources: Annotated[
            bool,
            typer.Option(
                "--with-resources/--no-with-resources",
                help="Generate resources.py primitive (mcp only).",
                rich_help_panel="Options",
                show_default=True,
            ),
        ] = False,
        with_prompts: Annotated[
            bool,
            typer.Option(
                "--with-prompts/--no-with-prompts",
                help="Generate prompts.py primitive (mcp only).",
                rich_help_panel="Options",
                show_default=True,
            ),
        ] = False,
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
        """Scaffold an entry point inside infrastructure/entry_points/."""
        if type_ is None:
            typer.echo(ctx.get_help())
            raise typer.Exit(0)
        _generate_entry_point_impl(
            type_, swagger, enable_kafka, enable_mcp_client, with_resources, with_prompts, dry_run
        )
