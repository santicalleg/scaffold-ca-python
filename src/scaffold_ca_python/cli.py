import sys
import importlib.metadata
import typer

app = typer.Typer(
    name="Scaffold Clean Architecture Python CLI",
    help="Scaffold Clean Architecture Python development tools",
    add_completion=False,
    no_args_is_help=True,  # Show help if no args provided
)

@app.command()
def version() -> None:
    """Show the Scaffold version."""
    try:
        version = importlib.metadata.version("scaffold-ca-python")
        print(f"Scaffold version: {version}")
    except importlib.metadata.PackageNotFoundError:
        print("Scaffold version unknown (package not installed)")
        sys.exit(1)

@app.command()
def hello(name: str = typer.Argument("World")) -> None:
    """Say hello to NAME."""
    typer.echo(f"Hello, {name}!")
