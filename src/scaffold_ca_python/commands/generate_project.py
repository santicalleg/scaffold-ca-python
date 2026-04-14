"""generate_project: scaffold a full Clean Architecture project skeleton (T032)."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.tree import Tree

from scaffold_ca_python.core.file_writer import FileWriter
from scaffold_ca_python.core.name_utils import ScaffoldError, to_snake_case, validate_name
from scaffold_ca_python.core.template_renderer import TemplateRenderer
from scaffold_ca_python.models.context import ProjectContext
from scaffold_ca_python.models.file_operation import CreateFile, FileOperation, GeneratedFile

console = Console()
renderer = TemplateRenderer()
writer = FileWriter()

# Layers: (subpath-under-src/<pkg>, label for layer_init.jinja2)
_LAYER_DIRS: list[tuple[str, str]] = [
    ("application", "application"),
    ("domain/model", "domain/model"),
    ("domain/usecase", "domain/usecase"),
    ("infrastructure/driven_adapters", "infrastructure/driven-adapters"),
    ("infrastructure/entry_points", "infrastructure/entry-points"),
    ("infrastructure/helpers", "infrastructure/helpers"),
]


def _generate_project_impl(
    name: str,
    dry_run: bool,
) -> None:
    try:
        validate_name(name)
    except ScaffoldError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from None

    python_pkg = to_snake_case(name)
    target_dir = Path.cwd() / python_pkg

    if target_dir.exists():
        console.print(
            f"[red]Error:[/red] Directory '{python_pkg}/' already exists. "
            "Aborting to prevent data loss.\n"
            "[dim]Hint:[/dim] Choose a different project name or remove the existing directory first."
        )
        raise typer.Exit(code=1)

    ctx = ProjectContext(name=name)
    ctx_dict = ctx.model_dump()
    ctx_dict["created_at"] = datetime.now(tz=UTC).isoformat()

    operations: list[FileOperation] = []

    # --- Config files at project root ----------------------------------------
    _add(
        operations,
        target_dir / "pyproject.toml",
        renderer.render_string(_tmpl("project/pyproject_toml.jinja2"), ctx_dict),
    )
    _add(operations, target_dir / "README.md", renderer.render_string(_tmpl("project/README.jinja2"), ctx_dict))
    _add(operations, target_dir / ".gitignore", renderer.render_string(_tmpl("project/gitignore.jinja2"), ctx_dict))
    _add(operations, target_dir / "mypy.ini", renderer.render_string(_tmpl("project/mypy_ini.jinja2"), ctx_dict))
    _add(operations, target_dir / "Dockerfile", renderer.render_string(_tmpl("project/dockerfile.jinja2"), ctx_dict))
    _add(
        operations, target_dir / ".dockerignore", renderer.render_string(_tmpl("project/dockerignore.jinja2"), ctx_dict)
    )
    _add(
        operations,
        target_dir / ".python-version",
        renderer.render_string(_tmpl("project/python_version.jinja2"), ctx_dict),
    )

    # --- DI config files -----------------------------------------------------
    _di_cfg = target_dir / "src" / python_pkg / "application" / "config"
    for _fname in (
        "__init__.py",
        "config.py",
        "resource_container.py",
        "driven_adapters_container.py",
        "usecases_container.py",
        "container.py",
    ):
        _add(
            operations,
            _di_cfg / _fname,
            renderer.render_string(_tmpl(f"project/application/config/{_fname}.jinja2"), ctx_dict),
        )

    # --- src/<pkg>/main.py ---------------------------------------------------
    _add(
        operations,
        target_dir / "src" / python_pkg / "main.py",
        renderer.render_string(_tmpl("project/main.py.jinja2"), ctx_dict),
    )

    # --- src/<pkg>/__init__.py ------------------------------------------------
    _add(operations, target_dir / "src" / python_pkg / "__init__.py", f'"""{name} package."""\n')

    # --- Layer __init__.py stubs ---------------------------------------------
    for layer_path, layer_label in _LAYER_DIRS:
        layer_ctx = {**ctx_dict, "layer": layer_label}
        _add(
            operations,
            target_dir / "src" / python_pkg / layer_path / "__init__.py",
            renderer.render_string(_tmpl("project/layer_init.jinja2"), layer_ctx),
        )

    # --- tests/__init__.py ---------------------------------------------------
    _add(operations, target_dir / "src" / "tests" / "__init__.py", "")

    if dry_run:
        preview = writer.execute(operations, dry_run=True)
        tree = Tree(f"[bold]{python_pkg}/[/bold] (dry run)")
        for p in sorted(preview):
            tree.add(str(p.relative_to(target_dir)))
        console.print(tree)
        return

    created = writer.execute(operations, dry_run=False)
    console.print(
        f"[green]✓[/green] Project [bold]{python_pkg}/[/bold] created successfully. Created {len(created)} file(s)."
    )


def register(app: typer.Typer) -> None:
    """Register clean-architecture / ca commands onto *app*."""

    @app.command(
        "clean-architecture",
        help="Scaffold a new CA project. Alias: ca",
        epilog="Example: scaffold clean-architecture --name OrderService",
    )
    def clean_architecture(
        ctx: typer.Context,
        name: Annotated[
            str,
            typer.Option(
                "--name",
                help="Project name (PascalCase or snake_case).",
                rich_help_panel="Required",
            ),
        ] = None,
        dry_run: Annotated[
            bool,
            typer.Option(
                "--dry-run/--no-dry-run",
                help="Preview files without writing.",
                rich_help_panel="Options",
                show_default=True,
            ),
        ] = False,
    ) -> None:
        """Scaffold a complete Clean Architecture Python project."""
        if name is None:
            typer.echo(ctx.get_help())
            raise typer.Exit(0)
        _generate_project_impl(name, dry_run)

    @app.command(
        "ca",
        hidden=True,
        help="Scaffold a new CA project. Alias: ca",
        epilog="Example: scaffold clean-architecture --name OrderService",
    )
    def ca(
        ctx: typer.Context,
        name: Annotated[
            str, typer.Option("--name", help="Project name (PascalCase or snake_case).", rich_help_panel="Required")
        ] = None,
        dry_run: Annotated[
            bool,
            typer.Option(
                "--dry-run/--no-dry-run",
                help="Preview files without writing.",
                rich_help_panel="Options",
                show_default=True,
            ),
        ] = False,
    ) -> None:
        """Scaffold a complete Clean Architecture Python project."""
        if name is None:
            typer.echo(ctx.get_help())
            raise typer.Exit(0)
        _generate_project_impl(name, dry_run)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _add(operations: list[FileOperation], path: Path, content: str) -> None:
    operations.append(CreateFile(file=GeneratedFile(path=path, content=content, template_name="")))


def _tmpl(name: str) -> str:
    """Read a bundled template source string via the renderer's resource loader."""
    import importlib.resources

    ref = importlib.resources.files("scaffold_ca_python.templates").joinpath(name)
    return ref.read_text(encoding="utf-8")
