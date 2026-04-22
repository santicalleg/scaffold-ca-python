import typer

from scaffold_ca_python.commands import (
    delete_module,
    generate_driven_adapter,
    generate_entry_point,
    generate_helper,
    generate_model,
    generate_pipeline,
    generate_project,
    generate_use_case,
    update_project,
    validate_structure,
)

app = typer.Typer(
    name="scaffold-ca-python",
    help="Scaffold production-ready Clean Architecture Python projects.",
    add_completion=False,
    rich_markup_mode="rich",
)

generate_project.register(app)
generate_model.register(app)
generate_use_case.register(app)
generate_driven_adapter.register(app)
generate_entry_point.register(app)
generate_helper.register(app)
generate_pipeline.register(app)
delete_module.register(app)
update_project.register(app)
validate_structure.register(app)


@app.callback(invoke_without_command=True)
def _main(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)
