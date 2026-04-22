# Feature Specification: Deduplicate Command + Alias Function Bodies in commands Package

**Feature Branch**: `016-dedup-command-aliases`
**Created**: 2026-04-14
**Status**: Draft
**Input**: User description: "Into commands package, the modules with generate_ name are repeating the functions with same parameters for both the full command and the alias. The idea is that with @app.command annotation change how the command is called but the function should be the same and not duplicated."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Developer Reads a Command Module Without Duplicate Logic (Priority: P1)

A contributor opening a command module — such as `generate_model.py`, `generate_use_case.py`, `generate_helper.py`, `generate_entry_point.py`, `generate_driven_adapter.py`, or `delete_module.py` — sees only a single command handler function inside `register()`. The abbreviated alias (`gm`, `guc`, `gh`, `gep`, `gda`, `dm`) is wired to the same function, not a copy of it.

**Why this priority**: The duplication is visible in every module and directly affects readability and maintainability. Any future change to parameters or help text must be made in two places, risking drift.

**Independent Test**: Each affected command module has exactly one function definition inside `register()`. Running the full test suite before and after the change produces the same pass/fail results. Both the long name and short alias continue to work identically.

**Acceptance Scenarios**:

1. **Given** the `generate_model.py` module, **When** a developer reads the `register()` function, **Then** there is only one function body that handles both `generate-model` and `gm` invocations.
2. **Given** any of the 6 affected command modules, **When** both `scaffold generate-model --name Order` and `scaffold gm --name Order` are invoked, **Then** both commands produce identical output and side effects.
3. **Given** a command with no `--name` argument, **When** either the long or short form is invoked, **Then** both display the help text the same way.

---

### User Story 2 - Contributor Adds a New Alias Without Duplicating Code (Priority: P2)

A contributor who needs to add a new alias for an existing command references the established pattern and registers the alias by pointing `@app.command` at the shared handler function — without copying the function body.

**Why this priority**: Establishes a clear convention that prevents future duplication from being reintroduced.

**Independent Test**: The pattern is demonstrably consistent across all 6 command modules, so a new contributor can follow it by imitation.

**Acceptance Scenarios**:

1. **Given** the refactored modules, **When** a contributor adds a new alias for an existing command, **Then** they register `@app.command("new-alias", ...)` pointing at the same handler function without copying the function body.

---

### Edge Cases

- What happens when the long-form command is invoked with `--help`? The rich help panel annotations must remain on the long-form command.
- What happens when the short alias is invoked with `--help`? It may show a simpler help (acceptable — current behavior preserved).
- How does the system handle the `ctx` parameter when no arguments are provided? Both aliases must still call the same early-exit logic.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Each command module under `src/scaffold_ca_python/commands/` that registers both a long-form command and a short alias MUST define only one shared handler function inside `register()`.
- **FR-002**: The shared handler function MUST be registered under the long-form command name (e.g., `generate-model`) via `@app.command(...)`.
- **FR-003**: The short alias (e.g., `gm`) MUST be registered by decorating the same handler function with an additional `@app.command(alias, hidden=True, ...)` decorator rather than defining a separate function.
- **FR-004**: All existing command behaviour — invocation, parameter names, defaults, help text, exit codes — MUST remain identical after the refactor.
- **FR-005**: No existing test file MAY be modified as a result of this change; all currently passing tests MUST continue to pass.
- **FR-006**: The refactoring MUST be applied to all 6 affected modules: `generate_model.py`, `generate_use_case.py`, `generate_helper.py`, `generate_entry_point.py`, `generate_driven_adapter.py`, and `delete_module.py`.

### Key Entities

- **Command module**: A Python file under `commands/` that calls `register(app)` to add one or more Typer commands to the CLI app.
- **Long-form command**: The primary, human-readable command name (e.g., `generate-model`) registered via `@app.command("generate-model", ...)`.
- **Short alias**: A hidden abbreviated command (e.g., `gm`) registered via `@app.command("gm", hidden=True, ...)`.
- **Handler function**: The single Python function that implements the command logic and is decorated by both `@app.command` calls.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Each of the 6 affected `register()` functions contains exactly one inner function definition (confirmed by code inspection or automated grep).
- **SC-002**: All currently passing tests continue to pass after the change; zero test regressions.
- **SC-003**: Both the long-form name and the short alias produce identically structured CLI invocations (confirmed via existing CLI integration tests).
- **SC-004**: Total lines of code across the 6 affected command modules decreases (duplication removed; expected reduction: ~180 lines from the current 1132-line total).

## Assumptions

- Typer supports stacking multiple `@app.command(...)` decorators on the same function to register it under two names; this is the mechanism to be used.
- The `ctx` parameter and `None`-check early-exit pattern is the same in both the full and alias functions today, so a single function body handles both identically.
- `generate_project.py` and `generate_pipeline.py` are out of scope as they do not follow the duplicate alias pattern.
- Test files are not modified; the spec assumes all current tests cover both long-form and alias invocations.
