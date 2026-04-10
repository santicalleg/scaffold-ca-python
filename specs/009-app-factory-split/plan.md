# Implementation Plan: App Factory Split — server.py / app.py Separation

**Branch**: `009-app-factory-split` | **Date**: 2026-04-10 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/009-app-factory-split/spec.md`  
> **Note**: Task IDs in this file (Phase tables) are superseded by [tasks.md](tasks.md). tasks.md is the single authoritative ID space.

## Summary

Move the FastAPI application factory (`create_app`, `lifespan`) and server launcher (`start_server`) from the generated `server.py` into a new generated file `application/app.py`. Replace `server.py` with a two-line thin wrapper that delegates to `application.app.start_server()`. Remove `main.py` from the restapi generator output. Add a test template for every generated source file (4 new templates). The scaffold tool itself gets corresponding template-rendering unit tests and command integration tests for all new behaviour.

## Technical Context

**Language/Version**: Python 3.13  
**Primary Dependencies**: FastAPI ≥ 0.135.2, uvicorn[standard] ≥ 0.20, dependency-injector ≥ 4.49.0, pydantic-settings ≥ 2.13.1, Jinja2 ≥ 3.1, pydantic ≥ 2.0, typer ≥ 0.16, rich ≥ 14.1  
**Storage**: N/A (code-generation tool; no database)  
**Testing**: pytest + pytest-cov (80% line-coverage gate enforced in CI); typer.testing.CliRunner for command tests  
**Target Platform**: macOS / Linux developer workstation; uv-managed virtual environment  
**Project Type**: CLI library (scaffold tool that generates Python Clean Architecture projects)  
**Performance Goals**: N/A — generator runs in <1 s; no throughput SLA  
**Constraints**: ruff line-length 120, target-version py313; mypy strict; no sync I/O patterns in generated code  
**Scale/Scope**: ~450 existing tests; 9 new files touched or created; ~15 new test assertions

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status | Notes |
|---|---|---|---|
| I — Clean Architecture | `application/app.py` placed in `application/` layer; `server.py` is process entry only | ✅ PASS | Factory/lifespan are composition-root concerns; they belong in `application/`. Dependency rule: `server.py` imports from `application/`, not the other way around. |
| II — Template-Driven | All new generated files come from Jinja2 templates; new templates have `tests/templates/` rendering tests | ✅ PASS | 5 new templates created; `test_entry_point_templates.py` extended with one test per new template |
| III — Command Parity | `gep --type restapi` remains the canonical FastAPI entry-point; contract updated in `contracts/gep-restapi.md` | ✅ PASS | No new command needed; existing `gep` is extended |
| IV — Python-First Idioms | Type hints, ruff, mypy strict, async/await, Python 3.13, uv | ✅ PASS | All generated templates use `from __future__ import annotations`; `async def lifespan`; full type annotations |
| V — Test-First (TDD) | Tests written before implementation; generated project ships test files; 80% coverage gate | ✅ PASS | RED tests written first; 5 test templates emitted by generator; coverage checked in quality gates |
| VI — Developer Experience | Rich output; `--dry-run` lists new files; error messages with hints | ✅ PASS | No changes to Rich output needed; `--dry-run` automatically picks up new operations list |
| VII — Git Workflow | Branch `009-app-factory-split` follows convention | ✅ PASS | Branch created and active |

**Re-check post-design**: All gates still pass. `app.py` in `application/` is architecturally correct per Principle I. No violations require justification.

## Project Structure

### Documentation (this feature)

```text
specs/009-app-factory-split/
├── plan.md              # This file
├── research.md          # Phase 0 output ✅
├── data-model.md        # Phase 1 output ✅
├── quickstart.md        # Phase 1 output ✅
├── contracts/
│   └── gep-restapi.md   # Phase 1 output ✅
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
src/scaffold_ca_python/
├── commands/
│   └── generate_entry_point.py          # UPDATE: add app.py emission, add 4 test emissions, remove main.py overwrite
└── templates/
    └── entry_point/
        └── restapi/
            ├── app.py.jinja2            # CREATE: factory + lifespan + start_server
            ├── server.py.jinja2         # UPDATE: thin wrapper only
            ├── test_app.py.jinja2       # CREATE: tests for app.py
            ├── test_server.py.jinja2    # CREATE: tests for server.py
            ├── test_exception_handler.py.jinja2  # CREATE
            └── test_schemas.py.jinja2   # CREATE

tests/
├── commands/
│   └── test_generate_entry_point.py     # UPDATE: add ~8 new assertions
└── templates/
    └── test_entry_point_templates.py    # UPDATE: add ~8 new rendering tests

ms_test/src/ms_test/
├── application/
│   └── app.py                          # CREATE: reference implementation
└── server.py                           # UPDATE: thin wrapper reference implementation
```

---

## Implementation Phases

### Phase 1 — RED Tests (TDD gate)

**Goal**: Write all failing tests before touching any implementation code. Constitution Principle V strictly enforced.

**Tasks**:

| ID | File | Test description |
|---|---|---|
| T001 | `tests/commands/test_generate_entry_point.py` | `test_restapi_creates_app_py` — running `gep --type restapi` creates `src/my_app/application/app.py` |
| T002 | `tests/commands/test_generate_entry_point.py` | `test_restapi_no_main_py` — `main.py` is NOT created after `gep --type restapi` |
| T003 | `tests/commands/test_generate_entry_point.py` | `test_restapi_server_py_is_thin_wrapper` — `server.py` contains ≤ 5 non-blank non-comment lines and no `FastAPI` import |
| T004 | `tests/commands/test_generate_entry_point.py` | `test_restapi_creates_test_app` — `tests/application/test_app.py` is created |
| T005 | `tests/commands/test_generate_entry_point.py` | `test_restapi_creates_test_server` — `tests/infrastructure/entry_points/api/v1/test_server.py` created |
| T006 | `tests/commands/test_generate_entry_point.py` | `test_restapi_creates_test_exception_handler` — counterpart test file created |
| T007 | `tests/commands/test_generate_entry_point.py` | `test_restapi_creates_test_schemas` — counterpart test file created |
| T008 | `tests/commands/test_generate_entry_point.py` | `test_restapi_dry_run_includes_app_py` — dry-run output mentions `app.py` and all new test files |
| T009 | `tests/templates/test_entry_point_templates.py` | `test_restapi_app_has_create_app_factory` — `app.py.jinja2` renders with `create_app` present |
| T010 | `tests/templates/test_entry_point_templates.py` | `test_restapi_app_has_lifespan` — `app.py.jinja2` renders with `lifespan` async context manager |
| T011 | `tests/templates/test_entry_point_templates.py` | `test_restapi_app_has_container_wiring` — `app.py.jinja2` renders with `Container` and `wire(` present |
| T012 | `tests/templates/test_entry_point_templates.py` | `test_restapi_app_factory_path_uses_application_app` — `app.py.jinja2` `uvicorn.run` path = `<pkg>.application.app:create_app` |
| T013 | `tests/templates/test_entry_point_templates.py` | `test_restapi_server_is_thin_wrapper` — `server.py.jinja2` does NOT contain `FastAPI` or `Container` |
| T014 | `tests/templates/test_entry_point_templates.py` | `test_restapi_server_imports_start_server` — `server.py.jinja2` renders with `from ... application.app import start_server` |
| T015 | `tests/templates/test_entry_point_templates.py` | `test_restapi_test_app_template_has_create_app_assertion` — `test_app.py.jinja2` renders with `create_app` and `FastAPI` |
| T016 | `tests/templates/test_entry_point_templates.py` | `test_restapi_test_server_template_importable` — `test_server.py.jinja2` renders with `start_server` referenced |

**Verification**: `uv run pytest tests/ -k "test_restapi"` — all 16 new tests RED (fail), existing restapi tests still GREEN.

---

### Phase 2 — Templates (GREEN for template tests)

**Goal**: Create/update Jinja2 templates to make T009–T016 pass.

**Tasks**:

| ID | Action | File |
|---|---|---|
| T017 | CREATE | `src/scaffold_ca_python/templates/entry_point/restapi/app.py.jinja2` — full factory template (lifespan + create_app + start_server) |
| T018 | UPDATE | `src/scaffold_ca_python/templates/entry_point/restapi/server.py.jinja2` — replace with thin wrapper (import + guard) |
| T019 | CREATE | `src/scaffold_ca_python/templates/entry_point/restapi/test_app.py.jinja2` |
| T020 | CREATE | `src/scaffold_ca_python/templates/entry_point/restapi/test_server.py.jinja2` |
| T021 | CREATE | `src/scaffold_ca_python/templates/entry_point/restapi/test_exception_handler.py.jinja2` |
| T022 | CREATE | `src/scaffold_ca_python/templates/entry_point/restapi/test_schemas.py.jinja2` |

**Verification**: `uv run pytest tests/templates/` — T009–T016 GREEN; all prior template tests still GREEN.

---

### Phase 3 — Generator Command (GREEN for command tests)

**Goal**: Update `generate_entry_point.py` to emit `app.py` and all new test files, and stop emitting `main.py`, making T001–T008 pass.

**Tasks**:

| ID | Action | Location | Description |
|---|---|---|---|
| T023 | UPDATE | `_build_operations` restapi branch | Add `CreateFile` for `project_root / "src" / pkg / "application" / "app.py"` using `app.py.jinja2` |
| T024 | UPDATE | `_build_operations` restapi branch | Add `CreateFile` for `project_root / "tests" / "application" / "test_app.py"` using `test_app.py.jinja2` |
| T025 | UPDATE | `_build_operations` restapi branch | Add 3 test `CreateFile` ops for `test_server.py`, `test_exception_handler.py`, `test_schemas.py` in `test_dir` |
| T026 | DELETE | `_generate_entry_point_impl` | Remove the 7-line `"Overwrite main.py"` block |

**Verification**: `uv run pytest tests/commands/test_generate_entry_point.py` — T001–T008 GREEN; all prior command tests still GREEN.

---

### Phase 4 — ms_test Reference Implementation

**Goal**: Update `ms_test` (the reference project) to match the new generated structure, so it serves as a living example.

**Tasks**:

| ID | Action | File |
|---|---|---|
| T027 | CREATE | `ms_test/src/ms_test/application/app.py` — copy factory/lifespan/start_server from current `server.py`; update uvicorn path to `ms_test.application.app:create_app` |
| T028 | UPDATE | `ms_test/src/ms_test/server.py` — replace with thin wrapper: `from ms_test.application.app import start_server` + guard |

**Verification**: If `ms_test` has its own test suite, run it. Otherwise verify the module imports cleanly: `cd ms_test && uv run python -c "from ms_test.application.app import create_app; print(create_app())"`.

---

### Phase 5 — Quality Gates

**Goal**: Ensure all linting, type-checking, and coverage gates pass.

**Tasks**:

| ID | Command | Expected result |
|---|---|---|
| T029 | `uv run ruff check src/ tests/` | Zero errors |
| T030 | `uv run ruff format --check src/ tests/` | Zero format violations |
| T031 | `uv run mypy src/` | Zero errors (strict mode) |
| T032 | `uv run pytest tests/ --cov=src --cov-fail-under=80` | ≥ 80% line coverage; ≥ 466 tests passing (450 + 16 new) |

---

## Complexity Tracking

> No Constitution Check violations. No complexity justification required.

---

## Key Risks

| Risk | Likelihood | Mitigation |
|---|---|---|
| `uvicorn.run()` factory path breaks silently if wrong module path | Medium | T012 explicitly asserts the generated path; end-to-end smoke test in quickstart validates it |
| `application/` directory may not exist in generated project at `gep` time | Low | `FileWriter` creates parent directories; `application/__init__.py` is created by `ca` command (feature 008 confirmed) |
| Existing workflow tests assert `main.py` is emitted | Low | One existing test (`test_restapi_main_contains_fastapi`) checks `rest_controller.py`, not `main.py` itself; check all existing restapi assertions before removing the overwrite block |
```