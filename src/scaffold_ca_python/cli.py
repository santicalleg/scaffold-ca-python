import typer

from scaffold_ca_python.commands import generate_project

app = typer.Typer(
    name="scaffold-ca-python",
    help="Scaffold production-ready Clean Architecture Python projects.",
    add_completion=False,
    no_args_is_help=True,
)

generate_project.register(app)

