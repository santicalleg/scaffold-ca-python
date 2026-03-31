"""delete_module: safely remove a previously generated module and its test mirror (T072)."""

from __future__ import annotations

import shutil
import tomllib
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from scaffold_ca_python.core.name_utils import ScaffoldError, to_snake_case, validate_name
from scaffold_ca_python.core.project_detector import find_project_root

console = Console()


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
    tests_root = project_root / "tests"

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
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
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
        console.print(
            "[red]Error:[/red] No scaffold-ca-python project found. Run 'scaffold ca' first."
        )
        raise typer.Exit(code=1) from None

    snake = to_snake_case(name)
    targets = _find_module_targets(project_root, snake)

    if not targets:
        console.print(
            f"[red]Error:[/red] No module named '{snake}' found in project.\n"
            "[dim]Hint:[/dim] Check spelling with 'scaffold vs' to list modules."
        )
        raise typer.Exit(code=1) from None

    # Collect all paths to delete
    paths_to_delete: list[Path] = []
    for src_path, test_path in targets:
        paths_to_delete.append(src_path)
        if test_path is not None:
            paths_to_delete.append(test_path)

    # dry_run OR no --confirm → preview mode only
    if dry_run or not confirm:
        console.print("The following files would be deleted:\n")
        for p in paths_to_delete:
            try:
                display = p.relative_to(project_root)
            except ValueError:
                display = p
            console.print(f"  {display}")
        console.print("\nRun with --confirm to proceed.")
        return

    # Actually delete
    deleted: list[Path] = []
    for p in paths_to_delete:
        if p.is_dir():
            shutil.rmtree(p)
        elif p.is_file():
            p.unlink()
        deleted.append(p)

    console.print("Deleted:")
    for p in deleted:
        try:
            display = p.relative_to(project_root)
        except ValueError:
            display = p
        console.print(f"  [green]✓[/green] {display}")


def register(app: typer.Typer) -> None:
    """Register dm / delete-module commands onto *app*."""

    @app.command(
        "delete-module",
        help="Safely remove a module and its test mirror.",
        epilog="Example: scaffold dm --name Order --confirm",
    )
    def delete_module(
        ctx: typer.Context,
        name: Annotated[str | None, typer.Option("--name", help="Module name to delete.", rich_help_panel="Required")] = None,
        confirm: Annotated[
            bool,
            typer.Option(
                "--confirm/--no-confirm",
                help="Actually perform deletion.",
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
        """Preview or delete a previously generated module."""
        if name is None:
            typer.echo(ctx.get_help())
            raise typer.Exit(0)
        _delete_module_impl(name, confirm, dry_run)

    @app.command("dm", hidden=True, help="Alias for delete-module.")
    def dm(
        ctx: typer.Context,
        name: Annotated[str | None, typer.Option("--name", help="Module name to delete.")] = None,
        confirm: Annotated[bool, typer.Option("--confirm/--no-confirm")] = False,
        dry_run: Annotated[bool, typer.Option("--dry-run/--no-dry-run")] = False,
    ) -> None:
        """Alias for delete-module."""
        if name is None:
            typer.echo(ctx.get_help())
            raise typer.Exit(0)
        _delete_module_impl(name, confirm, dry_run)
