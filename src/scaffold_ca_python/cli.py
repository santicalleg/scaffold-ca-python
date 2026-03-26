"""scaffold-ca-python CLI entry point."""
from __future__ import annotations

import sys
import importlib.metadata
from enum import Enum

import typer

# ---------------------------------------------------------------------------
# Output mode state (set by global callback; consumed by all commands)
# ---------------------------------------------------------------------------


class OutputMode(str, Enum):
    normal = "normal"
    quiet = "quiet"
    verbose = "verbose"


class _State:
    mode: OutputMode = OutputMode.normal


_state = _State()


def get_output_mode() -> OutputMode:
    return _state.mode


# ---------------------------------------------------------------------------
# Top-level app
# ---------------------------------------------------------------------------

app = typer.Typer(
    name="scaffold-ca-python",
    help="Scaffold Clean Architecture Python development tools",
    add_completion=False,
    no_args_is_help=True,
)

# Sub-app for `scaffold generate <subcommand>`
generate_app = typer.Typer(
    name="generate",
    help="Generate a new component inside the current project",
    no_args_is_help=True,
)
app.add_typer(generate_app)


@app.callback()
def _global_options(
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress informational output."),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show debug-level output."),
) -> None:
    """scaffold-ca — Python Clean Architecture project scaffolder."""
    if quiet:
        _state.mode = OutputMode.quiet
    elif verbose:
        _state.mode = OutputMode.verbose
    else:
        _state.mode = OutputMode.normal


# ---------------------------------------------------------------------------
# version command (kept from original)
# ---------------------------------------------------------------------------


@app.command()
def version() -> None:
    """Show the scaffold-ca-python version."""
    try:
        ver = importlib.metadata.version("scaffold-ca-python")
        typer.echo(f"scaffold-ca-python {ver}")
    except importlib.metadata.PackageNotFoundError:
        typer.echo("scaffold-ca-python version unknown (package not installed)")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Lazy command registration — imported at module load to register subcommands
# ---------------------------------------------------------------------------

from scaffold_ca_python.commands import new as _new_cmd  # noqa: E402, F401
from scaffold_ca_python.commands import validate as _validate_cmd  # noqa: E402, F401
from scaffold_ca_python.commands import delete as _delete_cmd  # noqa: E402, F401
from scaffold_ca_python.commands import update as _update_cmd  # noqa: E402, F401
from scaffold_ca_python.commands import list_components as _list_cmd  # noqa: E402, F401
from scaffold_ca_python.commands.generate import model as _model_cmd  # noqa: E402, F401
from scaffold_ca_python.commands.generate import use_case as _use_case_cmd  # noqa: E402, F401
from scaffold_ca_python.commands.generate import driven_adapter as _da_cmd  # noqa: E402, F401
from scaffold_ca_python.commands.generate import entry_point as _ep_cmd  # noqa: E402, F401
from scaffold_ca_python.commands.generate import helper as _helper_cmd  # noqa: E402, F401
