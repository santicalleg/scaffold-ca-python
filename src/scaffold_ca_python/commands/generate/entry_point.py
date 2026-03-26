"""scaffold generate entry-point — generate entry point stubs."""
from __future__ import annotations

import sys
from typing import Optional

import typer

from scaffold_ca_python.cli import generate_app
from scaffold_ca_python.commands._output import info, verbose, error
from scaffold_ca_python.core.naming import validate_name, to_pascal_case
from scaffold_ca_python.core.project import find_project_root, ProjectMarker, ComponentRecord, NoProjectError
from scaffold_ca_python.core.renderer import TemplateRenderer

ENTRY_POINT_TYPES: dict[str, str] = {
    "generic":             "Empty entry point stub",
    "rest-api":            "REST API router stub (Flask/FastAPI, sync or async)",
    "graphql":             "GraphQL schema and resolver stub (strawberry)",
    "kafka-consumer":      "Kafka consumer stub",
    "sqs-listener":        "Amazon SQS listener stub",
    "async-event-handler": "Async event handler stub (--tech rabbitmq|kafka)",
    "cli":                 "CLI command stub (Typer)",
}

_TYPE_TO_DIR: dict[str, str] = {
    "generic":             "generic",
    "rest-api":            "rest_api",
    "graphql":             "graphql",
    "kafka-consumer":      "kafka_consumer",
    "sqs-listener":        "sqs_listener",
    "async-event-handler": "async_event_handler",
    "cli":                 "cli",
}


@generate_app.command("entry-point")
def generate_entry_point(
    entry_type: str = typer.Option(..., "--type", "-t", help="Entry point type."),
    name: str = typer.Option(..., "--name", "-n", help="Entry point name."),
    tech: Optional[str] = typer.Option(None, "--tech", help="Event tech (rabbitmq or kafka), only for --type async-event-handler."),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files."),
) -> None:
    """Generate an entry point stub in infrastructure/entry_points/."""
    if entry_type not in ENTRY_POINT_TYPES:
        error(f"Unknown entry-point type '{entry_type}'. Supported types:")
        for t, desc in ENTRY_POINT_TYPES.items():
            error(f"  {t:<25} {desc}")
        sys.exit(1)

    if entry_type == "async-event-handler" and tech and tech not in ("rabbitmq", "kafka"):
        error("--tech must be 'rabbitmq' or 'kafka' for --type async-event-handler.")
        sys.exit(1)

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
    type_dir = _TYPE_TO_DIR[entry_type]

    context = {
        "snake_name": snake_name,
        "pascal_name": pascal_name,
        "package": pkg,
        "mode": marker.mode,
        "tech": tech or "kafka",
    }

    renderer = TemplateRenderer()

    dest = root / pkg / "infrastructure" / "entry_points" / type_dir / f"{snake_name}.py"
    try:
        renderer.render_to_file(
            f"entry_point/{type_dir}/entry_point.py.j2",
            dest,
            context,
            force=force,
        )
        verbose(f"  created {dest.relative_to(root)}")
    except FileExistsError as exc:
        error(str(exc))
        sys.exit(1)

    generated = [str(dest.relative_to(root))]
    marker.register_component(ComponentRecord(
        type="entry-point",
        name=snake_name,
        layer=f"{pkg}/infrastructure/entry_points/{type_dir}",
        generated_files=generated,
    ))
    marker.save(root)

    info(f"✓ Entry point '{pascal_name}' ({entry_type}) generated:")
    for f in generated:
        info(f"    {f}")
