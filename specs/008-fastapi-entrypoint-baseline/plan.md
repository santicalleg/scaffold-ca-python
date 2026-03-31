# Implementation Plan: FastAPI Entry Point Baseline Alignment

**Branch**: `008-fastapi-entrypoint-baseline` | **Date**: 2026-03-31 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/008-fastapi-entrypoint-baseline/spec.md`

## Summary

`scaffold gep --type restapi` currently generates a flat `infrastructure/entry_points/restapi/` layout that does not match the runnable ms_test baseline. This plan upgrades the restapi entry-point generator to produce a versioned `api/v1/` structure, a `server.py` package entry point driven by pydantic-settings, an exception handler, and test templates discoverable by pytest. It also adds a compatibility guard that blocks FastAPI generation when an MCP or Agent entry point already exists.

The implementation touches three areas: new Jinja2 templates (replacing/adding to `src/scaffold_ca_python/templates/entry_point/restapi/`), updated file-emission logic in `generate_entry_point.py`, and new template-rendering tests in `tests/templates/test_entry_point_templates.py`.

**Research findings** (from codebase inspection):

- `scaffold clean-architecture` already generates `Dockerfile`, `mypy.ini`, and `application/config/` — these do not need to be re-emitted by `gep`. FR-001/FR-005 scope only: new files under `infrastructure/entry_points/api/v1/` and `server.py`.
- `resource_container.py.jinja2` is absent from `src/scaffold_ca_python/templates/project/application/config/`; it must be added as a new template (used by `server.py` lifespan wiring).
- Current `_DEP_MAP["restapi"]` = `["fastapi>=0.100", "uvicorn[standard]>=0.20"]`; must add `"dependency-injector>=4.49.0"` and `"pydantic-settings>=2.13.1"`.
- The existing duplicate-directory guard (`src_dir.exists()`) fires after the type switch; the new compatibility guard must fire before any file check, as a separate early-exit.

## Technical Context

**Language/Version**: Python 3.13  
**Primary Dependencies**: Typer 0.16, Jinja2 3.1, Pydantic v2, Rich 14, uv (dep management)  
**Storage**: N/A — file I/O only via `FileWriter` / `TemplateRenderer`  
**Testing**: pytest, pytest-cov (≥80% gate), typer `CliRunner`  
**Target Platform**: CLI tool — macOS/Linux  
**Project Type**: CLI code-generator (library + scripts)  
**Performance Goals**: N/A — single-user CLI tool  
**Constraints**: ruff (line-length 120, `E/F/I/UP/ANN`), mypy strict, no ad-hoc string assembly for generated code (Principle II)  
**Scale/Scope**: ~8 new/modified templates, ~1 command file, ~2 test files

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I — Clean Architecture in generated projects | ✅ PASS | Generated `api/v1/` layout respects the three-layer rule (`domain`, `infrastructure`, `application`). `rest_controller.py` lives in `infrastructure/entry_points/`; `server.py` lives at `application/` root. |
| II — Template-driven generation | ✅ PASS | All new files are Jinja2 templates. New template tests added to `tests/templates/test_entry_point_templates.py`. |
| III — Command parity | ✅ PASS | `gep`/`generate-entry-point` already exists; this feature improves its `restapi` subtype only. |
| IV — Python-first idioms | ✅ PASS | Type hints, async/await, ruff + mypy strict enforced. |
| V — Test-first development | ✅ PASS | TDD (red → green) enforced per task ordering. Template tests cover all new templates. |
| VI — Developer experience | ✅ PASS | `--dry-run` preserved, Rich output maintained, error messages include resolution hints. |

**Post-design re-check**: No new violations introduced.

## Project Structure

### Documentation (this feature)

```text
specs/008-fastapi-entrypoint-baseline/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── quickstart.md        ← Phase 1 output
├── contracts/           ← Phase 1 output
└── tasks.md             ← /speckit.tasks output (not created here)
```

### Source Code Changes

```text
src/scaffold_ca_python/
├── commands/
│   └── generate_entry_point.py          # MODIFY: new path logic, compat guard, updated deps
├── templates/
│   ├── entry_point/
│   │   └── restapi/                     # REPLACE/ADD templates
│   │       ├── __init__.py.jinja2       # keep (unchanged)
│   │       ├── rest_controller.py.jinja2  # NEW (replaces router.py.jinja2 conceptually)
│   │       ├── exception_handler.py.jinja2  # NEW
│   │       ├── server.py.jinja2         # NEW (package-root uvicorn launcher)
│   │       ├── test_rest_controller.py.jinja2  # NEW (replaces test_router.py.jinja2)
│   │       ├── health.py.jinja2         # keep (may adjust route registration)
│   │       ├── schemas.py.jinja2        # keep (unchanged)
│   │       ├── main.py.jinja2           # MODIFY: use lifespan + DI container wiring
│   │       ├── router.py.jinja2         # REMOVE from emission (kept for backward compat, not emitted)
│   │       ├── test_router.py.jinja2    # REMOVE from emission (replaced by test_rest_controller)
│   │       └── entrypoint_main.py.jinja2  # keep (overrides main.py on the project)
│   └── project/
│       └── application/
│           └── config/
│               └── resource_container.py.jinja2  # NEW (missing from current template set)

tests/
├── commands/
│   └── test_generate_entry_point.py     # MODIFY: add US3 guard tests + new file assertion tests
└── templates/
    └── test_entry_point_templates.py    # MODIFY: add rendering tests for new templates
```

## Complexity Tracking

No constitution violations. All changes are within the existing command and template pattern.

