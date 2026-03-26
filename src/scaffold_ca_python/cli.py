import importlib.metadata

import typer

app = typer.Typer(
    name="scaffold-ca-python",
    help="Scaffold production-ready Clean Architecture Python projects.",
    add_completion=False,
    no_args_is_help=True,
)


@app.command()
def version() -> None:
    """Show the installed scaffold-ca-python version."""
    try:
        v = importlib.metadata.version("scaffold-ca-python")
        typer.echo(f"scaffold-ca-python {v}")
    except importlib.metadata.PackageNotFoundError:
        typer.echo("scaffold-ca-python (version unknown — package not installed)")
        raise typer.Exit(code=1)

