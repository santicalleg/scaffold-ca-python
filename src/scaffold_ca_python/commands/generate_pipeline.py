"""generate_pipeline: scaffold a CI/CD pipeline configuration file (T069)."""

from __future__ import annotations

import importlib.resources
import tomllib
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.tree import Tree

from scaffold_ca_python.core.file_writer import FileWriter
from scaffold_ca_python.core.name_utils import ScaffoldError
from scaffold_ca_python.core.project_detector import find_project_root
from scaffold_ca_python.core.template_renderer import TemplateRenderer
from scaffold_ca_python.models.context import ProjectContext
from scaffold_ca_python.models.file_operation import CreateFile, FileOperation, GeneratedFile

console = Console()
renderer = TemplateRenderer()
writer = FileWriter()

_ALLOWED_PROVIDERS = ("github", "azure")

_PROVIDER_HELP = "Pipeline provider (github, azure)."

_GPIPE_EPILOG = (
    "Providers:\n\n"
    "  github    GitHub Actions (.github/workflows/ci.yml)\n"
    "  azure     Azure Pipelines (azure-pipelines.yml)\n\n"
    "Note: --provider is required.\n\n"
    "Examples:\n\n"
    "  scaffold gpipe --provider github\n"
    "  scaffold gpipe --provider azure\n"
)

# Module-level option default needed with from __future__ import annotations
_PROVIDER_DEFAULT: str | None = None


def _generate_pipeline_impl(provider: str | None, dry_run: bool) -> None:
    # --- Validate provider presence ---
    if not provider:
        console.print(
            "[red]Error:[/red] --provider is required. "
            f"Choose from: {', '.join(_ALLOWED_PROVIDERS)}."
        )
        raise typer.Exit(code=1) from None

    # --- Validate provider value ---
    if provider not in _ALLOWED_PROVIDERS:
        console.print(
            f"[red]Error:[/red] Unknown provider '{provider}'. "
            f"Allowed: {', '.join(_ALLOWED_PROVIDERS)}."
        )
        raise typer.Exit(code=1) from None

    # --- Locate project root ---
    try:
        project_root = find_project_root()
    except ScaffoldError:
        console.print(
            "[red]Error:[/red] No scaffold-ca-python project found. Run 'scaffold ca' first."
        )
        raise typer.Exit(code=1) from None

    project_ctx = _load_project_context(project_root)
    ctx_dict = project_ctx.model_dump()

    # --- Resolve output path ---
    if provider == "github":
        out_path = project_root / ".github" / "workflows" / "ci.yml"
        template = "pipeline/github/ci.yml.jinja2"
        display_name = "ci.yml"
    else:  # azure
        out_path = project_root / "azure-pipelines.yml"
        template = "pipeline/azure/azure_pipelines.yml.jinja2"
        display_name = "azure-pipelines.yml"

    # --- Duplicate guard ---
    if out_path.exists():
        console.print(
            f"[red]Error:[/red] '{display_name}' already exists at "
            f"'{out_path.relative_to(project_root)}'. Use --force to overwrite.\n"
            "[dim]Hint:[/dim] Remove the existing file first or choose a different provider."
        )
        raise typer.Exit(code=1) from None

    operations: list[FileOperation] = [
        CreateFile(file=GeneratedFile(
            path=out_path,
            content=renderer.render_string(_tmpl(template), ctx_dict),
            template_name=template,
        )),
    ]

    if dry_run:
        preview = writer.execute(operations, dry_run=True)
        tree = Tree(f"[bold]{display_name}[/bold] (dry run)")
        for p in sorted(preview):
            tree.add(str(p.relative_to(project_root)))
        console.print(tree)
        return

    created = writer.execute(operations, dry_run=False)
    console.print(
        f"[green]✓[/green] Pipeline [bold]{display_name}[/bold] created. "
        f"Created {len(created)} file(s)."
    )


def register(app: typer.Typer) -> None:
    """Register gpipe / generate-pipeline commands onto *app*."""

    @app.command(
        "generate-pipeline",
        help="Scaffold a CI/CD pipeline configuration file.",
        epilog=_GPIPE_EPILOG,
    )
    def generate_pipeline(
        ctx: typer.Context,
        provider: Annotated[
            str | None,
            typer.Option(
                "--provider",
                help="Pipeline provider (github, azure).",
                rich_help_panel="Required",
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
        """Scaffold a CI/CD pipeline file for the specified provider."""
        if provider is None:
            typer.echo(ctx.get_help())
            raise typer.Exit(0)
        _generate_pipeline_impl(provider, dry_run)

    @app.command("gpipe", hidden=True, help="Alias for generate-pipeline.", epilog=_GPIPE_EPILOG)
    def gpipe(
        ctx: typer.Context,
        provider: Annotated[str | None, typer.Option("--provider", help="Pipeline provider (github, azure).")] = None,
        dry_run: Annotated[bool, typer.Option("--dry-run/--no-dry-run")] = False,
    ) -> None:
        """Alias for generate-pipeline."""
        if provider is None:
            typer.echo(ctx.get_help())
            raise typer.Exit(0)
        _generate_pipeline_impl(provider, dry_run)


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
