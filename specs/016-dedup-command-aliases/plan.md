# Implementation Plan: Deduplicate Command + Alias Function Bodies

**Branch**: `016-dedup-command-aliases` | **Date**: 2026-04-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/016-dedup-command-aliases/spec.md`

## Summary

Remove duplicate inner function bodies from the `register()` functions in 6 command modules
(`generate_model.py`, `generate_use_case.py`, `generate_helper.py`, `generate_entry_point.py`,
`generate_driven_adapter.py`, `delete_module.py`) by stacking two `@app.command(...)` decorators
on a single shared handler function. Typer ≥0.16.0 supports this pattern natively (verified —
see `research.md`). No behavior change; zero test regressions required.

## Technical Context

**Language/Version**: Python 3.13+  
**Primary Dependencies**: typer>=0.16.0, rich>=14.1.0; ruff (linter/formatter), mypy strict (type checker)  
**Storage**: N/A — CLI tool, no database  
**Testing**: pytest + pytest-cov; 80% line-coverage gate enforced; tests in `tests/`  
**Target Platform**: Linux/macOS CLI  
**Project Type**: CLI library / code-generation tool  
**Performance Goals**: N/A — pure structural refactor; no I/O-bound paths affected  
**Constraints**: Zero test regressions; no test file modifications; `ruff check` + `mypy` must pass after refactor  
**Scale/Scope**: 6 command modules, ~1132 lines total; ~180 lines of duplication removed

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Applies? | Status | Notes |
|-----------|----------|--------|-------|
| I — Clean Architecture (generated projects) | No | EXEMPT | Principle I governs *generated projects*, not the CLI tool's own source code |
| II — Template-Driven Code Generation | No | EXEMPT | No templates are added, removed, or modified by this refactor |
| III — Full Command Parity (aliases required) | **Yes** | **PASS** | All 6 short aliases (`gm`, `guc`, `gh`, `gep`, `gda`, `dm`) are preserved via stacked `@app.command` decorators |
| IV — Python-First Idioms (ruff, mypy strict) | **Yes** | **GATE** | `uv run ruff check src/` and `uv run mypy src/` must pass after each module is refactored; verified at end of each phase |
| V — Test-First Development | **Yes** | **JUSTIFIED** | Pure structural refactor with zero behavior change. Existing passing test suite serves as the regression guard. No new behavior is introduced, so no new failing tests are written. Red-Green state: tests are already green and must remain green throughout. |
| VI — Developer Experience | **Yes** | **PASS** | Aliases preserved; Rich output and `--dry-run` behavior unchanged |
| VII — Git Workflow | **Yes** | **PASS** | Branch `016-dedup-command-aliases` follows the flat numbered-branch convention (constitution v2.0.3 exception) |

## Project Structure

### Documentation (this feature)

```text
specs/016-dedup-command-aliases/
├── plan.md          # This file (/speckit.plan output)
├── research.md      # Phase 0 output (/speckit.plan)
├── data-model.md    # Phase 1 output — N/A for this refactor
├── quickstart.md    # Phase 1 output — N/A (no interface changes)
├── contracts/       # Phase 1 output — N/A (no new public contracts)
└── tasks.md         # Phase 2 output (/speckit.tasks — NOT created by /speckit.plan)
```

### Source Code (affected files only)

```text
src/scaffold_ca_python/commands/
├── generate_model.py           # 141 → ~120 lines: remove inner gm(), stack @app.command on generate_model()
├── generate_use_case.py        # 141 → ~120 lines: remove inner guc(), stack on generate_use_case()
├── generate_helper.py          # 141 → ~120 lines: remove inner gh(), stack on generate_helper()
├── generate_entry_point.py     # 289 → ~245 lines: remove inner gep(), stack on generate_entry_point()
├── generate_driven_adapter.py  # 196 → ~165 lines: remove inner gda(), stack on generate_driven_adapter()
└── delete_module.py            # 224 → ~195 lines: remove inner dm(), stack on delete_module()
```

No new files created. No test files modified. No template files affected.

**Structure Decision**: Single-project. All changes are isolated to 6 existing command modules
under `src/scaffold_ca_python/commands/`. Tests live in `tests/` and are read-only for this feature.

## Complexity Tracking

No constitution violations requiring justification. Principle V (TDD) is addressed inline in the
Constitution Check above — the refactor introduces no new behavior, so no new failing tests are
written before implementation.
