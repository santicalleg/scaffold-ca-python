# Research: Deduplicate Command + Alias Function Bodies

**Feature**: 016-dedup-command-aliases  
**Date**: 2026-04-14

## Decision Log

### 1. Typer Stacked Decorator Support

**Decision**: Use stacked `@app.command(...)` decorators on a single function to register it under
both the long-form name and the short alias.

**Rationale**: Typer ≥0.16.0 natively supports multiple `@app.command` decorators on the same
function. Both decorators route to the identical function body. This eliminates all duplicate
function definitions with zero behavior change.

**Alternatives considered**:
- **Dictionary dispatch** (e.g., `_aliases = {"gm": generate_model_fn}`): rejected — adds
  indirection, not idiomatic Typer; hides the alias from code inspection.
- **Separate `register_alias()` helper**: rejected — adds abstraction for a one-time structural
  operation; stacked decorators are self-documenting and how Typer is designed to be used.
- **Typer `result_callback` or `app.registered_commands` manipulation**: rejected — internal API,
  fragile across Typer versions.

**Verification** (executed against typer==0.16.0 before planning):

```python
# Pattern used in verification
@app.command("generate-model", help="Generate a model.", rich_help_panel="Generate")
@app.command("gm", hidden=True)
def generate_model(
    ctx: typer.Context,
    name: Annotated[str | None, typer.Option("--name", "-n")] = None,
    dry_run: Annotated[bool, typer.Option("--dry-run")] = False,
) -> None:
    if ctx.invoked_subcommand is not None or name is None:
        print(ctx.get_help())
        raise typer.Exit()
    # ... business logic
```

Test results (all ✓):
- `scaffold generate-model --name Order` → exit 0, correct output
- `scaffold gm --name Order` → exit 0, identical output
- `scaffold gm` (no args) → exit 0, help text displayed

**Constraint discovered**: The long-form decorator must be outermost (declared first in source
order); the short-alias decorator must be innermost (declared second, immediately before `def`):

```python
@app.command("generate-model", ...)  # outermost — long-form with full help metadata
@app.command("gm", hidden=True)      # innermost — hidden alias
def generate_model(...): ...
```

Reversing the order is syntactically valid but places the alias metadata as the "primary" entry,
which breaks the `rich_help_panel` grouping expected in `--help` output.

---

### 2. Scope of Change

**Decision**: Apply stacked decorator pattern to exactly 6 modules. Do not touch any other command
module.

**Rationale**: Only the listed 6 modules have the exact long-form + hidden-alias duplicate inner
function pattern. Confirmed via `grep -n "def "` on all command modules.

**Affected modules** (verified):
| Module | Long-form | Alias | Alias line (before refactor) |
|--------|-----------|-------|------------------------------|
| `generate_model.py` | `generate-model` | `gm` | L116 |
| `generate_use_case.py` | `generate-use-case` | `guc` | L116 |
| `generate_helper.py` | `generate-helper` | `gh` | L116 |
| `generate_entry_point.py` | `generate-entry-point` | `gep` | L275 |
| `generate_driven_adapter.py` | `generate-driven-adapter` | `gda` | L169 |
| `delete_module.py` | `delete-module` | `dm` | L199 |

**Out of scope** (confirmed no duplicate pattern):
- `generate_pipeline.py` — `gpipe` alias exists but does not use duplicate inner functions
- `validate_structure.py`, `update_project.py`, `generate_project.py` — no aliases registered

---

### 3. Decorator Order and Help Text Preservation

**Decision**: Place the long-form decorator (`@app.command("generate-model", help="...",
rich_help_panel="...")`) first (outermost), the alias (`@app.command("gm", hidden=True)`) second
(innermost).

**Rationale**: The outermost decorator's `help`, `rich_help_panel`, and `epilog` metadata take
precedence in Typer's command registry. This preserves the current UX where
`scaffold generate-model --help` shows the full help text and `scaffold gm` is a hidden shortcut
with minimal help.

---

### 4. No Test Modifications Required

**Decision**: No test files are added or modified.

**Rationale**: The refactor is purely structural — function signatures, parameter names, defaults,
return types, exit codes, and output text are all unchanged. Existing tests that invoke both
long-form and alias commands continue to pass without modification. Constitution Principle V
(TDD) is satisfied because: the tests already exist, they are green, and the refactor's only
obligation is to keep them green throughout.

---

## NEEDS CLARIFICATION

None — all decisions resolved before implementation.
