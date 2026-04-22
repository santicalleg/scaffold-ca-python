"""update_project: upgrade dependencies via uv (T075)."""

from __future__ import annotations

import subprocess
from typing import Annotated

import typer
from rich.console import Console

from scaffold_ca_python.core.name_utils import ScaffoldError
from scaffold_ca_python.core.project_detector import find_project_root

console = Console()

_GUP = "Update project dependencies via uv lock --upgrade + uv sync. Alias: 'up'"
_GUP_EPILOG = "Example:\n\n  * scaffold up --dry-run\n\n  * scaffold update-project --dry-run"


def _update_project_impl(dry_run: bool) -> None:
    # Locate project root
    try:
        project_root = find_project_root()
    except ScaffoldError:
        console.print("[red]Error:[/red] No scaffold-ca-python project found. Run 'scaffold ca' first.")
        raise typer.Exit(code=1) from None

    lock_cmd = ["uv", "lock", "--upgrade"]
    sync_cmd = ["uv", "sync"]

    if dry_run:
        console.print("Would run:")
        console.print(f"  {' '.join(lock_cmd)}   (cwd: {project_root})")
        console.print(f"  {' '.join(sync_cmd)}             (cwd: {project_root})")
        return

    try:
        subprocess.run(lock_cmd, check=True, cwd=project_root)
    except FileNotFoundError:
        console.print(
            "[red]Error:[/red] 'uv' is not installed or not on PATH. Install it from https://docs.astral.sh/uv/"
        )
        raise typer.Exit(code=1) from None
    except subprocess.CalledProcessError:
        console.print("[red]Error:[/red] Dependency lock failed. See output above.")
        raise typer.Exit(code=2) from None

    try:
        subprocess.run(sync_cmd, check=True, cwd=project_root)
    except FileNotFoundError:
        console.print(
            "[red]Error:[/red] 'uv' is not installed or not on PATH. Install it from https://docs.astral.sh/uv/"
        )
        raise typer.Exit(code=1) from None
    except subprocess.CalledProcessError:
        console.print("[red]Error:[/red] Sync failed. See output above.")
        raise typer.Exit(code=2) from None

    console.print("[green]✓[/green] Locked updated dependencies.")
    console.print("[green]✓[/green] Synced virtual environment.")


def register(app: typer.Typer) -> None:
    """Register up / update-project commands onto *app*."""

    @app.command(
        "update-project",
        help=_GUP,
        epilog=_GUP_EPILOG,
    )
    @app.command("up", hidden=True, help=_GUP, epilog=_GUP_EPILOG)
    def update_project(
        dry_run: Annotated[
            bool,
            typer.Option(
                "--dry-run/--no-dry-run",
                help="Preview commands without running.",
                rich_help_panel="Options",
                show_default=True,
            ),
        ] = False,
    ) -> None:
        """Update dependencies using uv."""
        _update_project_impl(dry_run)
