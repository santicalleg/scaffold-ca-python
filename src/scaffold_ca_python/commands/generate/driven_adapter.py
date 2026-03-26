"""scaffold generate driven-adapter — generate infrastructure adapter stubs."""
from __future__ import annotations

import sys

from typing import Optional

import typer

from scaffold_ca_python.cli import generate_app
from scaffold_ca_python.commands._output import info, verbose, error
from scaffold_ca_python.core.naming import validate_name, to_pascal_case
from scaffold_ca_python.core.project import find_project_root, ProjectMarker, ComponentRecord, NoProjectError
from scaffold_ca_python.core.renderer import TemplateRenderer

ADAPTER_TYPES: dict[str, str] = {
    "generic":        "Empty adapter stub",
    "repository":     "SQLAlchemy / asyncpg repository stub",
    "rest-client":    "HTTP REST client adapter (requires --url)",
    "mongodb":        "MongoDB adapter stub",
    "redis":          "Redis adapter stub (optional --mode template|repository)",
    "dynamo":         "DynamoDB adapter stub",
    "s3":             "AWS S3 adapter stub",
    "sqs-sender":     "Amazon SQS message sender stub",
    "kafka-sender":   "Kafka producer stub",
    "rabbitmq-sender":"RabbitMQ publisher stub",
    "secrets":        "Secrets provider adapter stub",
}

# Map CLI type name → template subdirectory name
_TYPE_TO_DIR: dict[str, str] = {
    "generic":         "generic",
    "repository":      "repository",
    "rest-client":     "rest_client",
    "mongodb":         "mongodb",
    "redis":           "redis",
    "dynamo":          "dynamo",
    "s3":              "s3",
    "sqs-sender":      "sqs_sender",
    "kafka-sender":    "kafka_sender",
    "rabbitmq-sender": "rabbitmq_sender",
    "secrets":         "secrets",
}


@generate_app.command("driven-adapter")
def generate_driven_adapter(
    adapter_type: str = typer.Option(..., "--type", "-t", help="Adapter type."),
    name: str = typer.Option(..., "--name", "-n", help="Adapter name."),
    url: Optional[str] = typer.Option(None, "--url", help="Base URL (required for --type rest-client)."),
    redis_mode: Optional[str] = typer.Option(None, "--mode", help="Redis mode: template or repository (only for --type redis)."),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files."),
) -> None:
    """Generate a driven adapter stub and its gateway interface."""
    # --- Validate type ---
    if adapter_type not in ADAPTER_TYPES:
        error(f"Unknown adapter type '{adapter_type}'. Supported types:")
        for t, desc in ADAPTER_TYPES.items():
            error(f"  {t:<20} {desc}")
        sys.exit(1)

    if adapter_type == "rest-client" and not url:
        error("--url is required for --type rest-client.")
        sys.exit(1)

    if redis_mode and redis_mode not in ("template", "repository"):
        error("--mode must be 'template' or 'repository' for --type redis.")
        sys.exit(1)

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
    type_dir = _TYPE_TO_DIR[adapter_type]

    context = {
        "snake_name": snake_name,
        "pascal_name": pascal_name,
        "package": pkg,
        "mode": redis_mode or "template" if adapter_type == "redis" else marker.mode,
        "adapter_type": adapter_type,
        "url": url or "",
    }

    renderer = TemplateRenderer()
    generated: list[str] = []

    # --- Gateway interface (skip if already exists and no --force) ---
    gw_dest = root / pkg / "domain" / "model" / "gateways" / f"{snake_name}_gateway.py"
    if not gw_dest.exists() or force:
        try:
            # All adapter types share the same gateway template structure
            renderer.render_to_file(
                f"driven_adapter/{type_dir}/gateway.py.j2",
                gw_dest,
                {**context, "mode": marker.mode},
                force=force,
            )
            verbose(f"  created {gw_dest.relative_to(root)}")
            generated.append(str(gw_dest.relative_to(root)))
        except FileExistsError as exc:
            error(str(exc))
            sys.exit(1)
    else:
        verbose(f"  gateway already exists, skipping: {gw_dest.relative_to(root)}")

    # --- Adapter stub ---
    adapter_dir = root / pkg / "infrastructure" / "driven_adapters" / type_dir
    adapter_dest = adapter_dir / f"{snake_name}.py"
    try:
        renderer.render_to_file(
            f"driven_adapter/{type_dir}/adapter.py.j2",
            adapter_dest,
            context,
            force=force,
        )
        verbose(f"  created {adapter_dest.relative_to(root)}")
        generated.append(str(adapter_dest.relative_to(root)))
    except FileExistsError as exc:
        error(str(exc))
        sys.exit(1)

    marker.register_component(ComponentRecord(
        type="driven-adapter",
        name=snake_name,
        layer=f"{pkg}/infrastructure/driven_adapters/{type_dir}",
        generated_files=generated,
    ))
    marker.save(root)

    info(f"✓ Driven adapter '{pascal_name}' ({adapter_type}) generated:")
    for f in generated:
        info(f"    {f}")
