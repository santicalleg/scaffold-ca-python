"""scaffold generate use-case — generate a use case stub."""
from __future__ import annotations

import sys
from pathlib import Path

import typer

from scaffold_ca_python.cli import generate_app
from scaffold_ca_python.commands._output import info, verbose, error
from scaffold_ca_python.core.naming import validate_name, to_pascal_case
from scaffold_ca_python.core.project import find_project_root, ProjectMarker, ComponentRecord, NoProjectError
from scaffold_ca_python.core.renderer import TemplateRenderer


@generate_app.command("use-case")
def generate_use_case(
    name: str = typer.Option(..., "--name", "-n", help="Use case name."),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files."),
) -> None:
    """Generate a use case class stub and a test stub."""
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
    generated: list[str] = []

    # Use case class
    uc_dest = root / pkg / "domain" / "usecase" / f"{snake_name}_use_case.py"
    try:
        renderer.render_to_file("use_case/use_case.py.j2", uc_dest, context, force=force)
        verbose(f"  created {uc_dest.relative_to(root)}")
        generated.append(str(uc_dest.relative_to(root)))
    except FileExistsError as exc:
        error(str(exc))
        sys.exit(1)

    # Test stub (inside tests/usecase/)
    test_dest = root / "tests" / "usecase" / f"test_{snake_name}_use_case.py"
    try:
        renderer.render_to_file("use_case/test_use_case.py.j2", test_dest, context, force=force)
        verbose(f"  created {test_dest.relative_to(root)}")
        generated.append(str(test_dest.relative_to(root)))
    except FileExistsError as exc:
        error(str(exc))
        sys.exit(1)

    marker.register_component(ComponentRecord(
        type="use-case",
        name=snake_name,
        layer=f"{pkg}/domain/usecase",
        generated_files=generated,
    ))
    marker.save(root)

    info(f"✓ Use case '{pascal_name}UseCase' generated:")
    for f in generated:
        info(f"    {f}")
