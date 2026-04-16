"""delete_module: safely remove a previously generated module and its test mirror (T039)."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from scaffold_ca_python.core.module_builder import ModuleBuilder
from scaffold_ca_python.core.name_utils import ScaffoldError, to_snake_case, validate_name
from scaffold_ca_python.core.project_detector import find_project_root, resolve_tests_root
from scaffold_ca_python.factory import ModuleFactory
from scaffold_ca_python.factory.simple.delete_module_factory import DeleteModuleFactory
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer

console = Console()

_REGISTRY: dict[str, type[ModuleFactory]] = {
    "delete": DeleteModuleFactory,
}

_DM_HELP = "Delete a previously generated module and its test mirror. Alias 'dm'."
_DM_EPILOG = (
    "Examples:\n\n"
    "  * scaffold dm --name Order\n\n"
    "  * scaffold delete-module --name MyAdapter\n\n"
)


# ---------------------------------------------------------------------------
# Module discovery helpers
# ---------------------------------------------------------------------------


def _find_module_targets(project_root: Path, snake: str) -> list[tuple[Path, Path | None]]:
    """Return a list of (target_path, test_path_or_None) for all matches of *snake*.

    Searches across:
      1. domain/model/<snake>.py
      2. domain/usecase/<snake>.py
      3. infrastructure/driven_adapters/<snake>/
      4. infrastructure/entry_points/<snake>/
      5. infrastructure/helpers/<snake>/
    """
    pkg = _get_python_package(project_root)
    src_root = project_root / "src" / pkg
    tests_root = resolve_tests_root(project_root)

    candidates: list[tuple[Path, Path | None]] = []

    # Single-file layers (domain/model, domain/usecase)
    for src_rel, test_rel in [
        (src_root / "domain" / "model" / f"{snake}.py", tests_root / "domain" / "model" / f"test_{snake}.py"),
        (src_root / "domain" / "usecase" / f"{snake}.py", tests_root / "domain" / "usecase" / f"test_{snake}.py"),
    ]:
        if src_rel.exists():
            candidates.append((src_rel, test_rel if test_rel.exists() else None))

    # Directory-based layers (infrastructure sub-dirs)
    for src_rel, test_rel in [
        (
            src_root / "infrastructure" / "driven_adapters" / snake,
            tests_root / "infrastructure" / "driven_adapters" / snake,
        ),
        (
            src_root / "infrastructure" / "entry_points" / snake,
            tests_root / "infrastructure" / "entry_points" / snake,
        ),
        (
            src_root / "infrastructure" / "helpers" / snake,
            tests_root / "infrastructure" / "helpers" / snake,
        ),
    ]:
        if src_rel.exists():
            candidates.append((src_rel, test_rel if test_rel.exists() else None))

    return candidates


def _get_python_package(root: Path) -> str:
    pyproject = root / "pyproject.toml"
    with pyproject.open("rb") as fh:
        data = tomllib.load(fh)
    section = data.get("tool", {}).get("scaffold-ca-python", {})
    name = section.get("name", root.name)
    import re

    s = name.replace("-", "_")
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return s.lower()


# ---------------------------------------------------------------------------
# Implementation
# ---------------------------------------------------------------------------


def _delete_module_impl(name: str, confirm: bool, dry_run: bool) -> None:
    # Validate name
    try:
        validate_name(name)
    except ScaffoldError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from None

    # Locate project root
    try:
        project_root = find_project_root()
    except ScaffoldError:
        console.print("[red]Error:[/red] No scaffold-ca-python project found. Run 'scaffold ca' first.")
        raise typer.Exit(code=1) from None

    project_ctx = _load_project_context(project_root)
    
    # Create a placeholder ModuleContext for the factory (layer doesn't matter for delete)
    module_ctx = ModuleContext(name=name, layer=Layer.HELPERS, project=project_ctx)

    # Find targets
    snake = to_snake_case(name)
    targets = _find_module_targets(project_root, snake)

    if not targets:
        console.print(
            f"[red]Error:[/red] No module named '{snake}' found in project.\n"
            "[dim]Hint:[/dim] Check spelling with 'scaffold vs' to list modules."
        )
        raise typer.Exit(code=1) from None

    # dry_run OR no --confirm → preview mode only
    if dry_run or not confirm:
        console.print("The following files would be deleted:\n")
        for src_path, test_path in targets:
            try:
                display = src_path.relative_to(project_root)
            except ValueError:
                display = src_path
            console.print(f"  {display}")
            if test_path:
                try:
                    display = test_path.relative_to(project_root)
                except ValueError:
                    display = test_path
                console.print(f"  {display}")
        console.print("\nRun with --confirm to proceed.")
        return

    # Use factory for deletion (only when confirm=True and not dry_run)
    builder = ModuleBuilder(
        project_root=project_root,
        project_ctx=project_ctx,
        module_ctx=module_ctx,
        dry_run=False,
    )

    factory_class = _REGISTRY["delete"]
    factory = factory_class()
    factory.build(builder)

    # Persist deletion
    builder.persist()
    console.print(f"[green]✓[/green] Deleted module(s) for [bold]{name}[/bold].")


def register(app: typer.Typer) -> None:
    """Register dm / delete-module command onto *app*."""

    @app.command(
        "delete-module",
        help=_DM_HELP,
        epilog=_DM_EPILOG,
    )
    @app.command("dm", hidden=True, help=_DM_HELP, epilog=_DM_EPILOG)
    def delete_module(
        ctx: typer.Context,
        name: Annotated[
            str | None, typer.Option("--name", help="Module name (PascalCase).", rich_help_panel="Required")
        ] = None,
        confirm: Annotated[
            bool,
            typer.Option(
                "--confirm/--no-confirm",
                help="Skip confirmation dialog and delete immediately.",
                rich_help_panel="Options",
            ),
        ] = False,
        dry_run: Annotated[
            bool,
            typer.Option(
                "--dry-run/--no-dry-run",
                help="Preview deletion without removing files.",
                rich_help_panel="Options",
                show_default=True,
            ),
        ] = False,
    ) -> None:
        """Delete a module and its test mirror."""
        if name is None:
            typer.echo(ctx.get_help())
            raise typer.Exit(0)
        _delete_module_impl(name, confirm, dry_run)


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
