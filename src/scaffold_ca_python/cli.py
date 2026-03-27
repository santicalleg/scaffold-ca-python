import typer

from scaffold_ca_python.commands import generate_model, generate_project, generate_use_case

app = typer.Typer(
    name="scaffold-ca-python",
    help="Scaffold production-ready Clean Architecture Python projects.",
    add_completion=False,
    no_args_is_help=True,
)

generate_project.register(app)
generate_model.register(app)
generate_use_case.register(app)

