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
from scaffold_ca_python.core.template_renderer import TemplateRenderer
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.file_operation import CreateFile, FileOperation, GeneratedFile
from scaffold_ca_python.models.layer import Layer

console = Console()
renderer = TemplateRenderer()
writer = FileWriter()

_ALLOWED_TYPES = ("restapi", "agent", "mcp", "generic")
_TYPE_HELP = "Entry-point type: restapi, agent, mcp, generic."
_SWAGGER_HELP = "Path to OpenAPI YAML/JSON (restapi only)."
_KAFKA_HELP = "Add async Kafka consumer stub."
_MCP_CLIENT_HELP = "Add MCP tool-call client stub."


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

    # --- Determine subdir and module context ---
    subdir = "mcp_server" if type_ == "mcp" else type_
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

    operations = _build_operations(type_, src_dir, test_dir, ctx_dict)

    if dry_run:
        preview = writer.execute(operations, dry_run=True)
        tree = Tree(f"[bold]{subdir}[/bold] (dry run)")
        for p in sorted(preview):
            tree.add(str(p.relative_to(project_root)))
        console.print(tree)
        return

    created = writer.execute(operations, dry_run=False)
    console.print(
        f"[green]✓[/green] Entry point [bold]{subdir}[/bold] created. "
        f"Created {len(created)} file(s)."
    )


def _build_operations(
    type_: str,
    src_dir: Path,
    test_dir: Path,
    ctx_dict: dict[str, object],
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
        return [
            _src("__init__.py.jinja2", "__init__.py"),
            _src("main.py.jinja2", "main.py"),
            _src("router.py.jinja2", "router.py"),
            _src("health.py.jinja2", "health.py"),
            _src("schemas.py.jinja2", "schemas.py"),
            _test("test_router.py.jinja2", "test_router.py"),
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
        epilog="Example: scaffold gep --type restapi",
    )
    def generate_entry_point(
        type_: Annotated[str, typer.Option("--type", help=_TYPE_HELP, rich_help_panel="Required")],
        swagger: Annotated[str | None, typer.Option("--swagger", help=_SWAGGER_HELP, rich_help_panel="Options")] = None,
        enable_kafka: Annotated[
            bool, typer.Option("--enable-kafka/--no-enable-kafka", help=_KAFKA_HELP, rich_help_panel="Options", show_default=True)
        ] = False,
        enable_mcp_client: Annotated[
            bool, typer.Option("--enable-mcp-client/--no-enable-mcp-client", help=_MCP_CLIENT_HELP, rich_help_panel="Options", show_default=True)
        ] = False,
        dry_run: Annotated[bool, typer.Option("--dry-run/--no-dry-run", help="Preview without writing.", rich_help_panel="Options", show_default=True)] = False,
    ) -> None:
        """Scaffold an entry point inside infrastructure/entry_points/."""
        _generate_entry_point_impl(type_, swagger, enable_kafka, enable_mcp_client, dry_run)

    @app.command("gep", hidden=True, help="Alias for generate-entry-point.")
    def gep(
        type_: Annotated[str, typer.Option("--type", help=_TYPE_HELP)],
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
        package=section.get("package", "com.example"),
    )


def _tmpl(name: str) -> str:
    ref = importlib.resources.files("scaffold_ca_python.templates").joinpath(name)
    return ref.read_text(encoding="utf-8")
