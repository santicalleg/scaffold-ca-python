"""validate_structure: AST-based CA layer import checker (T060)."""

from __future__ import annotations

from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from scaffold_ca_python.core.name_utils import ScaffoldError
from scaffold_ca_python.core.project_detector import find_project_root
from scaffold_ca_python.core.structure_validator import StructureValidator

console = Console()
_validator = StructureValidator()

_GVS_HELP = "Scan src/ for Clean Architecture import violations. Alias: 'vs'."
_GVS_EPILOG = (
    "Example:\n\n"
    "  * scaffold vs\n\n"
    "  * scaffold validate-structure\n"
)

def _validate_structure_impl(dry_run: bool) -> None:
    try:
        project_root = find_project_root()
    except ScaffoldError:
        console.print("[red]Error:[/red] No scaffold-ca-python project found. Run 'scaffold ca' first.")
        raise typer.Exit(code=1) from None

    try:
        report = _validator.validate(project_root)
    except ScaffoldError as exc:
        console.print(f"[red]Error:[/red] {exc}")
        raise typer.Exit(code=1) from None

    if report.passed:
        console.print(f"[green]✓[/green] Validated [bold]{report.files_scanned}[/bold] file(s) — no violations found.")
        return

    # --- Print violation table ---
    table = Table(
        title=f"[red]✗[/red] {len(report.violations)} violation(s) found",
        show_header=True,
        header_style="bold",
    )
    table.add_column("File", style="cyan", no_wrap=False)
    table.add_column("Line", style="yellow", justify="right")
    table.add_column("Import", style="white", no_wrap=False)
    table.add_column("Hint", style="dim", no_wrap=False)

    for v in report.violations:
        try:
            file_str = str(v.source_file.relative_to(project_root))
        except ValueError:
            file_str = str(v.source_file)

        table.add_row(
            file_str,
            str(v.line_number),
            v.import_statement,
            v.resolution_hint,
        )

    console.print(table)

    if not dry_run:
        raise typer.Exit(code=1)


def register(app: typer.Typer) -> None:
    """Register vs / validate-structure commands onto *app*."""

    @app.command(
        "validate-structure",
        help=_GVS_HELP,
        epilog=_GVS_EPILOG,
    )
    @app.command("vs", hidden=True, help=_GVS_HELP, epilog=_GVS_EPILOG)
    def validate_structure(
        dry_run: Annotated[
            bool,
            typer.Option(
                "--dry-run/--no-dry-run",
                help="Print results but always exit 0.",
                rich_help_panel="Options",
                show_default=True,
            ),
        ] = False,
    ) -> None:
        """Validate Clean Architecture layer boundaries in the current project."""
        _validate_structure_impl(dry_run)
