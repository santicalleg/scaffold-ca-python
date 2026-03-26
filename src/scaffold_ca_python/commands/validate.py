"""scaffold validate — check Clean Architecture layer dependency rules."""
from __future__ import annotations

import sys

import typer

from scaffold_ca_python.cli import app
from scaffold_ca_python.commands._output import info, error
from scaffold_ca_python.core.project import find_project_root, NoProjectError
from scaffold_ca_python.core.validator import validate_project


@app.command("validate")
def validate() -> None:
    """Validate project layer dependency rules using AST analysis."""
    try:
        root = find_project_root()
    except NoProjectError as exc:
        error(str(exc))
        sys.exit(1)

    violations = validate_project(root)

    if not violations:
        info("✓ No layer violations found — project structure is clean.")
        return

    typer.echo(f"✗ {len(violations)} layer violation(s) detected:", err=True)
    for v in violations:
        try:
            rel = v.file.relative_to(root)
        except ValueError:
            rel = v.file
        typer.echo(f"  {rel}: imports '{v.import_stmt}' — {v.rule}", err=True)

    sys.exit(1)
