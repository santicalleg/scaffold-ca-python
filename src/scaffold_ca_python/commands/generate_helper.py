"""generate_helper: scaffold a helper utility class and test stub (T064)."""

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


def _generate_helper_impl(name: str, dry_run: bool) -> None:
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
    module_ctx = ModuleContext(name=name, layer=Layer.HELPERS, project=project_ctx)

    snake = to_snake_case(name)
    pkg = project_ctx.python_package
    src_dir = project_root / "src" / pkg / "infrastructure" / "helpers" / snake
    test_dir = project_root / "tests" / "infrastructure" / "helpers" / snake

    if src_dir.exists():
        console.print(
            f"[red]Error:[/red] Directory '{src_dir.relative_to(project_root)}/' already exists.\n"
            "[dim]Hint:[/dim] Choose a different name or remove the existing directory first."
        )
        raise typer.Exit(code=1) from None

    ctx_dict = module_ctx.model_dump()
    operations: list[FileOperation] = [
        CreateFile(file=GeneratedFile(
            path=src_dir / "__init__.py",
            content=renderer.render_string(_tmpl("helper/__init__.py.jinja2"), ctx_dict),
            template_name="helper/__init__.py.jinja2",
        )),
        CreateFile(file=GeneratedFile(
            path=src_dir / f"{snake}.py",
            content=renderer.render_string(_tmpl("helper/helper.py.jinja2"), ctx_dict),
            template_name="helper/helper.py.jinja2",
        )),
        CreateFile(file=GeneratedFile(
            path=test_dir / f"test_{snake}.py",
            content=renderer.render_string(_tmpl("helper/test_helper.py.jinja2"), ctx_dict),
            template_name="helper/test_helper.py.jinja2",
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
        f"[green]✓[/green] Helper [bold]{module_ctx.class_name}[/bold] created. "
        f"Created {len(created)} file(s)."
    )


def register(app: typer.Typer) -> None:
    """Register gh / generate-helper commands onto *app*."""

    @app.command(
        "generate-helper",
        help="Scaffold a helper utility class and test stub.",
        epilog="Example: scaffold gh --name DateUtils",
    )
    def generate_helper(
        name: Annotated[
            str, typer.Option("--name", help="Helper name (PascalCase).", rich_help_panel="Required")
        ],
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
        """Scaffold a helper inside infrastructure/helpers/."""
        _generate_helper_impl(name, dry_run)

    @app.command("gh", hidden=True, help="Alias for generate-helper.")
    def gh(
        name: Annotated[str, typer.Option("--name", help="Helper name.")],
        dry_run: Annotated[bool, typer.Option("--dry-run/--no-dry-run")] = False,
    ) -> None:
        """Alias for generate-helper."""
        _generate_helper_impl(name, dry_run)


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
