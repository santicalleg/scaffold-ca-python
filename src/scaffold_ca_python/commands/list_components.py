"""scaffold list — catalogue supported driven-adapter and entry-point types."""
from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from scaffold_ca_python.cli import app
from scaffold_ca_python.commands._output import error

console = Console()

ADAPTER_CATALOG: dict[str, str] = {
    "generic":         "Empty adapter stub — start from scratch",
    "repository":      "SQLAlchemy / asyncpg repository stub",
    "rest-client":     "HTTP REST client adapter (requires --url)",
    "mongodb":         "MongoDB adapter stub",
    "redis":           "Redis adapter stub (optional --mode template|repository)",
    "dynamo":          "DynamoDB adapter stub",
    "s3":              "AWS S3 adapter stub",
    "sqs-sender":      "Amazon SQS message sender stub",
    "kafka-sender":    "Kafka producer stub",
    "rabbitmq-sender": "RabbitMQ publisher stub",
    "secrets":         "Secrets provider adapter stub",
}

ENTRY_POINT_CATALOG: dict[str, str] = {
    "generic":             "Empty entry point stub — start from scratch",
    "rest-api":            "REST API router (Flask/FastAPI, sync or async)",
    "graphql":             "GraphQL schema and resolver (strawberry)",
    "kafka-consumer":      "Kafka consumer stub",
    "sqs-listener":        "Amazon SQS listener stub",
    "async-event-handler": "Async event handler (--tech rabbitmq|kafka)",
    "cli":                 "CLI command stub (Typer)",
}


def _print_catalog(title: str, catalog: dict[str, str]) -> None:
    table = Table(title=title, show_header=True, header_style="bold cyan")
    table.add_column("Type", style="green")
    table.add_column("Description")
    for type_name, description in catalog.items():
        table.add_row(type_name, description)
    console.print(table)


@app.command("list")
def list_components(
    list_type: Optional[str] = typer.Option(
        None, "--type", "-t",
        help="Filter by 'driven-adapter' or 'entry-point'."
    ),
) -> None:
    """Display supported driven-adapter and entry-point types."""
    if list_type and list_type not in ("driven-adapter", "entry-point"):
        error(f"Unknown type '{list_type}'. Use 'driven-adapter' or 'entry-point'.")
        raise typer.Exit(1)

    if list_type is None or list_type == "driven-adapter":
        _print_catalog("Driven Adapter Types  (scaffold generate driven-adapter --type <TYPE>)", ADAPTER_CATALOG)

    if list_type is None or list_type == "entry-point":
        _print_catalog("Entry Point Types  (scaffold generate entry-point --type <TYPE>)", ENTRY_POINT_CATALOG)
