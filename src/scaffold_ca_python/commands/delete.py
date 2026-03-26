"""scaffold delete — remove a generated module from the project."""
from __future__ import annotations

import sys
from pathlib import Path

import typer

from scaffold_ca_python.cli import app
from scaffold_ca_python.commands._output import info, verbose, error
from scaffold_ca_python.core.naming import to_snake_case
from scaffold_ca_python.core.project import find_project_root, ProjectMarker, NoProjectError


@app.command("delete")
def delete(
    module: str = typer.Option(..., "--module", "-m", help="Module name to delete (snake_case)."),
) -> None:
    """Remove a previously generated component and its files."""
    try:
        root = find_project_root()
    except NoProjectError as exc:
        error(str(exc))
        sys.exit(1)

    marker = ProjectMarker.load(root)
    snake_name = to_snake_case(module)

    record = marker.find_component(snake_name)
    if record is None:
        error(
            f"No component named '{snake_name}' found in .scaffold-ca.json. "
            "Run 'scaffold list' to see registered components."
        )
        sys.exit(1)

    # Remove files
    removed: list[str] = []
    missing: list[str] = []
    for rel_path in record.generated_files:
        abs_path = root / rel_path
        if abs_path.exists():
            abs_path.unlink()
            verbose(f"  deleted {rel_path}")
            removed.append(rel_path)
            # Remove parent directory if empty
            parent = abs_path.parent
            if parent.exists() and not any(parent.iterdir()):
                parent.rmdir()
                verbose(f"  removed empty dir {parent.relative_to(root)}")
        else:
            missing.append(rel_path)
            verbose(f"  already absent: {rel_path}")

    marker.deregister_component(snake_name)
    marker.save(root)

    if removed:
        info(f"✓ Component '{snake_name}' deleted:")
        for f in removed:
            info(f"    {f}")
    if missing:
        info(f"  (already absent: {', '.join(missing)})")
