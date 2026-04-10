"""generate_entry_point: scaffold an entry-point adapter and test stub (T055)."""

from __future__ import annotations

import importlib.resources
import json
import tomllib
from pathlib import Path
from typing import Annotated

import typer
import yaml
from rich.console import Console
from rich.tree import Tree

from scaffold_ca_python.core.file_writer import FileWriter
from scaffold_ca_python.core.name_utils import ScaffoldError
from scaffold_ca_python.core.project_detector import find_project_root
from scaffold_ca_python.core.pyproject_writer import dry_run_inject, inject_dependencies
from scaffold_ca_python.core.template_renderer import TemplateRenderer
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.file_operation import CreateFile, FileOperation, GeneratedFile
from scaffold_ca_python.models.layer import Layer

console = Console()
renderer = TemplateRenderer()
writer = FileWriter()

_ALLOWED_TYPES = ("restapi", "agent", "mcp", "generic")
_TYPE_HELP = "Entry-point type: restapi, agent, mcp, generic."
_DEP_MAP: dict[str, list[str]] = {
    "restapi": [
        "fastapi[standard]>=0.135.2",
        "uvicorn[standard]>=0.20",
        "dependency-injector>=4.49.0",
        "pydantic-settings>=2.13.1",
    ],
    "agent": ["a2a-sdk>=0.1"],
    "mcp": ["mcp>=1.0"],
    "generic": [],
}
_SWAGGER_HELP = "Path to OpenAPI YAML/JSON (restapi only)."
_KAFKA_HELP = "Add async Kafka consumer stub (agent type only)."
_MCP_CLIENT_HELP = "Add MCP tool-call client stub (agent type only)."
_GEP_EPILOG = (
    "Types:\n\n"
    "  restapi    FastAPI REST API entry point\n"
    "  agent      A2A agent entry point\n"
    "  mcp        MCP server entry point\n"
    "  generic    Plain entry point\n\n"
    "Notes: --enable-kafka and --enable-mcp-client are agent type only.\n\n"
    "Examples:\n\n"
    "  scaffold gep --type restapi\n"
    "  scaffold gep --type agent --enable-kafka\n"
    "  scaffold gep --type mcp\n"
    "  scaffold gep --type generic\n"
)


def _generate_entry_point_impl(
    type_: str,
    swagger: str | None,
    enable_kafka: bool,
    enable_mcp_client: bool,
    dry_run: bool,
) -> None:
    # --- Validate type ---
    if type_ not in _ALLOWED_TYPES:
        console.print(
            f"[red]Error:[/red] Unknown type '{type_}'. "
            f"Allowed: {', '.join(_ALLOWED_TYPES)}."
        )
        raise typer.Exit(code=1) from None

    # --- Flag compatibility checks ---
    if swagger and type_ != "restapi":
        console.print("[red]Error:[/red] --swagger is only valid with --type restapi.")
        raise typer.Exit(code=1) from None

    if enable_mcp_client and type_ == "mcp":
        console.print("[red]Error:[/red] --enable-mcp-client is not valid with --type mcp.")
        raise typer.Exit(code=1) from None

    # --- Validate swagger path ---
    routes: list[tuple[str, str]] = []
    if swagger:
        swagger_path = Path(swagger)
        if not swagger_path.exists():
            console.print(
                f"[red]Error:[/red] Swagger file '{swagger}' not found."
            )
            raise typer.Exit(code=1) from None
        routes = _parse_swagger(swagger_path)

    # --- Locate project root ---
    try:
        project_root = find_project_root()
    except ScaffoldError:
        console.print(
            "[red]Error:[/red] No scaffold-ca-python project found. Run 'scaffold ca' first."
        )
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
    test_dir = project_root / "tests" / "infrastructure" / "entry_points" / subdir

    # --- Duplicate guard ---
    if src_dir.exists():
        console.print(
            f"[red]Error:[/red] Directory '{src_dir.relative_to(project_root)}/' already exists.\n"
            "[dim]Hint:[/dim] Choose a different type or remove the existing directory first."
        )
        raise typer.Exit(code=1) from None

    ctx_dict = {
        **module_ctx.model_dump(),
        "routes": routes,
        "enable_kafka": enable_kafka,
        "enable_mcp_client": enable_mcp_client,
    }

    operations = _build_operations(type_, src_dir, test_dir, ctx_dict, project_root, pkg)

    deps = _DEP_MAP.get(type_, [])

    if dry_run:
        preview = writer.execute(operations, dry_run=True)
        tree = Tree(f"[bold]{subdir}[/bold] (dry run)")
        for p in sorted(preview):
            tree.add(str(p.relative_to(project_root)))
        console.print(tree)
        if deps:
            would_add = dry_run_inject(project_root, deps)
            if would_add:
                console.print(
                    f"[dim]Would add to [project.dependencies]: {', '.join(would_add)}[/dim]"
                )
        return

    created = writer.execute(operations, dry_run=False)
    console.print(
        f"[green]✓[/green] Entry point [bold]{subdir}[/bold] created. "
        f"Created {len(created)} file(s)."
    )

    # --- Inject dependencies ------------------------------------------------
    if deps:
        added = inject_dependencies(project_root, deps)
        if added:
            console.print(
                f"[green]✓[/green] Added {', '.join(added)} to [project.dependencies]."
            )

    # --- Overwrite main.py with type-specific entrypoint --------------------
    main_py = project_root / "src" / pkg / "main.py"
    console.print(f"[yellow]⚠[/yellow] main.py will be replaced with {type_} entrypoint.")
    main_tpl = _tmpl(f"entry_point/{type_}/entrypoint_main.py.jinja2")
    main_content = renderer.render_string(main_tpl, {**module_ctx.model_dump(), "routes": routes})
    overwrite_op = CreateFile(file=GeneratedFile(
        path=main_py,
        content=main_content,
        template_name=f"entry_point/{type_}/entrypoint_main.py.jinja2",
        overwrite=True,
    ))
    writer.execute([overwrite_op], dry_run=False)


def _build_operations(
    type_: str,
    src_dir: Path,
    test_dir: Path,
    ctx_dict: dict[str, object],
    project_root: Path | None = None,
    pkg: str | None = None,
) -> list[FileOperation]:
    """Return the CreateFile operations for the given entry-point type."""
    base = f"entry_point/{type_}"

    def _src(tpl: str, out: str) -> CreateFile:
        return CreateFile(file=GeneratedFile(
            path=src_dir / out,
            content=renderer.render_string(_tmpl(f"{base}/{tpl}"), ctx_dict),
            template_name=f"{base}/{tpl}",
        ))

    def _test(tpl: str, out: str) -> CreateFile:
        return CreateFile(file=GeneratedFile(
            path=test_dir / out,
            content=renderer.render_string(_tmpl(f"{base}/{tpl}"), ctx_dict),
            template_name=f"{base}/{tpl}",
            is_test=True,
        ))

    if type_ == "restapi":
        assert project_root is not None and pkg is not None
        server_path = project_root / "src" / pkg / "server.py"
        return [
            _src("__init__.py.jinja2", "__init__.py"),
            _src("rest_controller.py.jinja2", "rest_controller.py"),
            _src("exception_handler.py.jinja2", "exception_handler.py"),
            _src("schemas.py.jinja2", "schemas.py"),
            CreateFile(file=GeneratedFile(
                path=server_path,
                content=renderer.render_string(_tmpl(f"{base}/server.py.jinja2"), ctx_dict),
                template_name=f"{base}/server.py.jinja2",
            )),
        ]
    if type_ == "agent":
        return [
            _src("__init__.py.jinja2", "__init__.py"),
            _src("agent.py.jinja2", "agent.py"),
            _src("card.py.jinja2", "card.py"),
            _test("test_agent.py.jinja2", "test_agent.py"),
        ]
    if type_ == "mcp":
        return [
            _src("__init__.py.jinja2", "__init__.py"),
            _src("server.py.jinja2", "server.py"),
            _test("test_server.py.jinja2", "test_server.py"),
        ]
    # generic
    return [
        _src("__init__.py.jinja2", "__init__.py"),
        _src("handler.py.jinja2", "entry_point.py"),
        _test("test_handler.py.jinja2", "test_entry_point.py"),
    ]


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
        help="Scaffold an entry-point adapter and test stub.",
        epilog=_GEP_EPILOG,
    )
    def generate_entry_point(
        ctx: typer.Context,
        type_: Annotated[str | None, typer.Option("--type", help=_TYPE_HELP, rich_help_panel="Required")] = None,
        swagger: Annotated[
            str | None, typer.Option("--swagger", help=_SWAGGER_HELP, rich_help_panel="Options")
        ] = None,
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
        _generate_entry_point_impl(type_, swagger, enable_kafka, enable_mcp_client, dry_run)

    @app.command("gep", hidden=True, help="Alias for generate-entry-point.", epilog=_GEP_EPILOG)
    def gep(
        ctx: typer.Context,
        type_: Annotated[str | None, typer.Option("--type", help=_TYPE_HELP)] = None,
        swagger: Annotated[str | None, typer.Option("--swagger", help=_SWAGGER_HELP)] = None,
        enable_kafka: Annotated[
            bool, typer.Option("--enable-kafka/--no-enable-kafka", help=_KAFKA_HELP)
        ] = False,
        enable_mcp_client: Annotated[
            bool, typer.Option("--enable-mcp-client/--no-enable-mcp-client", help=_MCP_CLIENT_HELP)
        ] = False,
        dry_run: Annotated[bool, typer.Option("--dry-run/--no-dry-run")] = False,
    ) -> None:
        """Alias for generate-entry-point."""
        if type_ is None:
            typer.echo(ctx.get_help())
            raise typer.Exit(0)
        _generate_entry_point_impl(type_, swagger, enable_kafka, enable_mcp_client, dry_run)


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
