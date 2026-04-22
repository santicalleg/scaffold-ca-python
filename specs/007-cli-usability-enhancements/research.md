# Research: CLI Usability Enhancements

**Feature**: 007-cli-usability-enhancements  
**Date**: 2026-03-30  
**Status**: Complete — all NEEDS CLARIFICATION resolved

---

## Decision 1: How to rename a Typer command while removing the old name

**Decision**: In `generate_project.py`, rename the primary `@app.command("generate-project", ...)` to `@app.command("clean-architecture", ...)`. Add a new `@app.command("generate-project", deprecated=True, hidden=True)` that prints a migration message and calls `raise typer.Exit(1)`. The `@app.command("ca", hidden=True)` alias remains unchanged, pointing to `_generate_project_impl`.

**Rationale**: Typer `@app.command(deprecated=True)` shows a deprecation notice automatically. Pairing it with a forced exit-1 and a custom error message ("Use `clean-architecture` instead") satisfies FR-002. The hidden=True keeps `generate-project` out of `--help` listings (FR-004). The `ca` alias stays hidden and points to the same impl (FR-003).

**Alternatives considered**:
- Fully removing `generate-project` via `@app.command` and relying on Click's "No such command" error — rejected because the error message would not contain a migration hint (FR-002).
- Using `@app.command("generate-project")` that errors without `deprecated=True` — simpler but loses the automatic deprecation warning; chosen option is more idiomatic.

---

## Decision 2: How to add a types table + Examples epilog to command help

**Decision**: Enable `rich_markup_mode="rich"` on the root `typer.Typer(...)` in `cli.py`. Use the `epilog=` parameter on each `@app.command(...)` decorator with Rich markup (e.g., `[bold cyan]Types:[/bold cyan]`). The types table is rendered as a Rich-marked-up list block in the epilog.

**Rationale**: Typer 0.16.0 supports `epilog=` on `@app.command()` and respects `rich_markup_mode` inherited from the parent `Typer()` instance. This approach is zero-dependency (Rich is already a required dependency) and keeps type documentation co-located with the command registration, not scattered in docstrings.

**Alternatives considered**:
- Embed the types table in the `help=` parameter of the `--type` option itself — rejected because the help string truncates in narrow terminals and doesn't allow multi-line formatting.
- Create a custom Click `HelpFormatter` subclass — rejected as over-engineering; Typer's built-in `epilog` is sufficient.

---

## Decision 3: How to expose `--enable-kafka` / `--enable-mcp-client` as agent-only in help

**Decision**: Update `_KAFKA_HELP` and `_MCP_CLIENT_HELP` module-level strings in `generate_entry_point.py` to include "(agent type only)" in the description. Additionally, mention this in the `gep` epilog under a "Notes" section.

**Rationale**: The option-level `help=` string is the most visible place in Typer output. Adding "(agent type only)" directly there and repeating it in the epilog Examples section covers all reading paths.

---

## Decision 4: How to achieve exit-0 on root no-args invocation

**Decision**: Replace the current `no_args_is_help=True` on the root `typer.Typer(...)` with a `@app.callback(invoke_without_command=True)` callback that checks `ctx.invoked_subcommand is None` and then calls `typer.echo(ctx.get_help()); raise typer.Exit(0)`.

**Rationale**: Tested and confirmed with Typer 0.16.0. `no_args_is_help=True` at root level triggers a Click "Missing command" error path that exits with code 2. The callback approach intercepts before any error and exits 0.

**Code pattern** (confirmed working):
```python
@app.callback(invoke_without_command=True)
def _root_callback(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)
```

**Alternatives considered**:
- Keep `no_args_is_help=True` — exits 2, violates SC-002.
- `context_settings={"help_option_names": [...]}` — does not change exit code.

---

## Decision 5: How to achieve exit-0 on subcommand no-args invocation

**Decision**: For each command that has required options (`--name`, `--type`):
1. Add `ctx: typer.Context` as the first parameter of the command function.
2. Change the option from `typer.Option(...)` (required) to `typer.Option(None, ...)` (optional default).
3. Add an early return guard: `if name is None: typer.echo(ctx.get_help()); raise typer.Exit(0)`.
4. Keep all existing validation logic below the guard unchanged.

**Rationale**: Tested and confirmed with Typer 0.16.0. This pattern gives exit 0 on no-args and preserves all existing behavior for supplied arguments. The `ctx` parameter is injected automatically by Typer when declared as the first param.

**Affected commands** (those with required options that trigger errors on no-args): `gm`, `guc`, `gep`, `gda`, `gpipe`, `ghelper`, `gdm`, `vs`, `up`. Commands `dm` and `up` should also be reviewed.

**Code pattern** (confirmed working):
```python
@app.command("gm")
def generate_model(
    ctx: typer.Context,
    name: str | None = typer.Option(None, "--name", help="..."),
    dry_run: bool = typer.Option(False, ...),
) -> None:
    if name is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(0)
    _generate_model_impl(name, dry_run)
```

**Important**: Existing tests that exercise the normal path (with `--name X`) are unaffected. No existing tests assert exit-2 for missing required options.

---

## Decision 6: How to add alias annotation in root help listing

**Decision**: In `cli.py`, rename the primary command function to include the alias in its `short_help=` parameter (e.g., `short_help="Scaffold a CA project. Alias: ca"`). The hidden `ca` alias command stays as-is. All existing hidden short-name aliases (`gep`, `gda`, etc.) similarly get `short_help="... Alias: gep"` added to the primary long-form command.

**Rationale**: Typer does not natively show aliases on the same line in the commands table. The simplest spec-compliant approach is to include the alias in `short_help=` of the primary long-name command. FR-013 only requires the alias to appear somewhere in the root help output.

**Alternatives considered**:
- Customizing Click's `format_commands` helper — requires subclassing Click's MultiCommand; too invasive.
- Showing alias as a second entry in the help table (two rows per command) — clutters the output.

---

## Decision 7: Constitution amendment required

**Decision**: `constitution.md` Principle III table must be updated after implementation to replace the `generate-project | ca` row with `clean-architecture | ca`. This is a PATCH amendment (command rename, no scope change). Defer until US1 implementation is complete and tests pass.

**Rationale**: The constitution governs what the CLI MUST implement. After renaming, the table must reflect reality. Updating it prematurely could cause the `speckit.implement` agent to act on stale facts.
