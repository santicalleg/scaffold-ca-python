# Implementation Plan: Fix RestAPI Entry Point Cleanup

**Branch**: `011-fix-restapi-cleanup` | **Date**: 2026-04-10 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/011-fix-restapi-cleanup/spec.md`

## Summary

When `gep --type restapi` runs it must (1) delete `src/<pkg>/main.py` if present, and (2) rewrite `[project.scripts]` in `pyproject.toml` so the CLI entry points to `<pkg>.server:start_server`. Both steps are silent no-ops when already in the desired state, and both are suppressed (dry-run preview only) under `--dry-run`. No template changes are needed — the `pyproject_toml.jinja2` template continues generating `main:main` at project creation time; the runtime patch is applied exclusively by `gep --type restapi`.

## Technical Context

**Language/Version**: Python 3.13  
**Primary Dependencies**: typer, Rich (CLI); tomllib + tomli_w (TOML read/write); pytest + pytest-cov (testing); ruff (lint/format); mypy strict (types)  
**Storage**: Local filesystem — `pyproject.toml` (TOML), `main.py` (plain file delete)  
**Testing**: pytest + `typer.testing.CliRunner`; 80% coverage gate  
**Target Platform**: macOS / Linux developer workstation  
**Project Type**: CLI code-generation tool (Python library + executable)  
**Performance Goals**: No new performance requirements — file I/O only  
**Constraints**: TOML read-modify-write must be idempotent; must not reformat unrelated sections (same constraint as `inject_dependencies`)  
**Scale/Scope**: Affects one command handler (`generate_entry_point.py`) and one core module (`pyproject_writer.py`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I — Clean Architecture in generated projects | ✅ PASS | No generated project structure changes |
| II — Template-Driven Code Generation | ✅ PASS | No new templates needed (FR-003); `pyproject_toml.jinja2` unchanged; `pyproject_writer.py` is CLI infrastructure, not a template |
| III — Full Command Parity | ✅ PASS | `--dry-run` flag supported (FR-004); no new commands |
| IV — Python-First Idioms | ✅ PASS | Type hints, ruff, mypy strict, Python 3.13+ |
| V — Test-First Development | ✅ PASS | RED tests written before implementation in all phases |
| VI — Developer Experience | ✅ PASS | Rich output for delete confirmation + scripts update; dry-run preview |

No gate violations. Proceed to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/011-fix-restapi-cleanup/
├── plan.md          ← this file
├── research.md      ← Phase 0 output
├── data-model.md    ← Phase 1 output
├── quickstart.md    ← Phase 1 output
└── tasks.md         ← /speckit.tasks output (NOT created by /speckit.plan)
```

### Source Code (modified files only)

```text
src/scaffold_ca_python/
├── commands/
│   └── generate_entry_point.py      ← add: main.py delete + scripts update + dry-run preview
└── core/
    └── pyproject_writer.py          ← add: update_project_scripts(), dry_run_scripts_update()

tests/
├── commands/
│   └── test_generate_entry_point.py ← add: RED tests for US1 + US2
└── core/
    └── test_pyproject_writer.py     ← add: unit tests for new pyproject_writer functions
```

## Complexity Tracking

No constitution violations require justification — this feature is additive with minimal scope.