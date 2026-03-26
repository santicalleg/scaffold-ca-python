"""scaffold generate model — generate domain entity + gateway interface."""
from __future__ import annotations

import sys
from pathlib import Path

import typer

from scaffold_ca_python.cli import generate_app
from scaffold_ca_python.commands._output import info, verbose, error
from scaffold_ca_python.core.naming import validate_name, to_pascal_case
from scaffold_ca_python.core.project import find_project_root, ProjectMarker, ComponentRecord, NoProjectError
from scaffold_ca_python.core.renderer import TemplateRenderer


@generate_app.command("model")
def generate_model(
    name: str = typer.Option(..., "--name", "-n", help="Model name (PascalCase or snake_case)."),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files."),
) -> None:
    """Generate a domain entity and its gateway interface stub."""
    # --- Project root guard ---
    try:
        root = find_project_root()
    except NoProjectError as exc:
        error(str(exc))
        sys.exit(1)

    marker = ProjectMarker.load(root)

    # --- Normalise name ---
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

    # entity
    entity_dest = root / pkg / "domain" / "model" / f"{snake_name}.py"
    try:
        renderer.render_to_file("model/entity.py.j2", entity_dest, context, force=force)
        verbose(f"  created {entity_dest.relative_to(root)}")
        generated.append(str(entity_dest.relative_to(root)))
    except FileExistsError as exc:
        error(str(exc))
        sys.exit(1)

    # gateway
    gateway_dest = root / pkg / "domain" / "model" / "gateways" / f"{snake_name}_gateway.py"
    try:
        renderer.render_to_file("model/gateway.py.j2", gateway_dest, context, force=force)
        verbose(f"  created {gateway_dest.relative_to(root)}")
        generated.append(str(gateway_dest.relative_to(root)))
    except FileExistsError as exc:
        error(str(exc))
        sys.exit(1)

    # Register
    marker.register_component(ComponentRecord(
        type="model",
        name=snake_name,
        layer=f"{pkg}/domain/model",
        generated_files=generated,
    ))
    marker.save(root)

    info(f"✓ Model '{pascal_name}' generated:")
    for f in generated:
        info(f"    {f}")
