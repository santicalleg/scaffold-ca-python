"""scaffold generate helper — generate a helper utility stub."""
from __future__ import annotations

import sys

import typer

from scaffold_ca_python.cli import generate_app
from scaffold_ca_python.commands._output import info, verbose, error
from scaffold_ca_python.core.naming import validate_name, to_pascal_case
from scaffold_ca_python.core.project import find_project_root, ProjectMarker, ComponentRecord, NoProjectError
from scaffold_ca_python.core.renderer import TemplateRenderer


@generate_app.command("helper")
def generate_helper(
    name: str = typer.Option(..., "--name", "-n", help="Helper name."),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files."),
) -> None:
    """Generate a helper utility stub in infrastructure/helpers/."""
    try:
        root = find_project_root()
    except NoProjectError as exc:
        error(str(exc))
        sys.exit(1)

    marker = ProjectMarker.load(root)

    try:
        snake_name, was_normalised = validate_name(name)
    except ValueError as exc:
        error(str(exc))
        sys.exit(1)
    if was_normalised:
        info(f"Name normalised: '{name}' → '{snake_name}'")

    pascal_name = to_pascal_case(snake_name)
    pkg = marker.base_package
    context = {
        "snake_name": snake_name,
        "pascal_name": pascal_name,
        "package": pkg,
        "mode": marker.mode,
    }

    renderer = TemplateRenderer()

    dest = root / pkg / "infrastructure" / "helpers" / f"{snake_name}.py"
    try:
        renderer.render_to_file("helper/helper.py.j2", dest, context, force=force)
        verbose(f"  created {dest.relative_to(root)}")
    except FileExistsError as exc:
        error(str(exc))
        sys.exit(1)

    generated = [str(dest.relative_to(root))]
    marker.register_component(ComponentRecord(
        type="helper",
        name=snake_name,
        layer=f"{pkg}/infrastructure/helpers",
        generated_files=generated,
    ))
    marker.save(root)

    info(f"✓ Helper '{pascal_name}' generated:")
    for f in generated:
        info(f"    {f}")
