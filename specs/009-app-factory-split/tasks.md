# Tasks: App Factory Split — server.py / app.py Separation

**Feature**: 009-app-factory-split  
**Input**: [plan.md](plan.md) · [spec.md](spec.md) · [data-model.md](data-model.md) · [contracts/gep-restapi.md](contracts/gep-restapi.md) · [quickstart.md](quickstart.md)  
**Branch**: `009-app-factory-split`  
**Total tasks**: 38 (T016b, T016c added post-analysis; T025/T029 corrected)

## Format: `[ID] [P?] [Story?] Description · file path`

- **[P]**: Can run in parallel with other [P] tasks in the same phase
- **[US1–US4]**: Which user story this task belongs to
- Red-test tasks MUST fail before corresponding implementation tasks begin (Constitution Principle V)

---

## Phase 1: Setup

**Purpose**: Confirm the starting baseline is clean before adding any red tests.

- [X] T001 Verify baseline — run `uv run pytest tests/` on branch `009-app-factory-split` and confirm ~450 tests pass with no unexpected failures

---

## Phase 2: Foundational

**Purpose**: All infrastructure (TemplateRenderer, FileWriter, `_build_operations`, pytest fixtures, `project_root` fixture in `test_generate_entry_point.py`) already exists from Feature 008. No new infrastructure is required.

**Checkpoint**: Phase 1 green → proceed directly to user stories.

---

## Phase 3: User Story 1 — App Factory Code Lives in `app.py` (Priority: P1) 🎯 MVP

**Goal**: `scaffold gep --type restapi` emits `application/app.py` containing `lifespan`, `create_app()`, and `start_server()`. Importing the module must not start a server.

**Independent Test**: Run `gep --type restapi` on a temporary project; assert `src/my_app/application/app.py` exists and its text contains `create_app` and `lifespan`.

### Tests for User Story 1 *(write first — must fail before T007–T009)*

- [X] T002 [US1] Add `test_restapi_creates_app_py` — assert `src/my_app/application/app.py` is created by `gep --type restapi` · `tests/commands/test_generate_entry_point.py`
- [X] T003 [P] [US1] Add `test_entry_point_restapi_app_has_create_app_factory` — render `app.py.jinja2`, assert `"create_app"` in output · `tests/templates/test_entry_point_templates.py`
- [X] T004 [P] [US1] Add `test_entry_point_restapi_app_has_lifespan` — render `app.py.jinja2`, assert `"lifespan"` and `"asynccontextmanager"` in output · `tests/templates/test_entry_point_templates.py`
- [X] T005 [P] [US1] Add `test_entry_point_restapi_app_has_container_wiring` — render `app.py.jinja2`, assert `"Container"` and `"wire("` in output · `tests/templates/test_entry_point_templates.py`
- [X] T006 [P] [US1] Add `test_entry_point_restapi_app_factory_path_uses_application_app` — render `app.py.jinja2`, assert `"application.app:create_app"` appears in the uvicorn.run call · `tests/templates/test_entry_point_templates.py`

### Implementation for User Story 1

- [X] T007 [US1] Create `app.py.jinja2` — move `lifespan`, `create_app`, `start_server` from `server.py.jinja2` into this new file; update `uvicorn.run` first arg to `"{{ project.python_package }}.application.app:create_app"` · `src/scaffold_ca_python/templates/entry_point/restapi/app.py.jinja2`
- [X] T008 [US1] Add `application/app.py` emission — in `_build_operations` restapi branch, add a `CreateFile` operation for `project_root / "src" / pkg / "application" / "app.py"` using `app.py.jinja2` · `src/scaffold_ca_python/commands/generate_entry_point.py`
- [X] T009 [P] [US1] Create ms_test reference implementation — copy `lifespan`, `create_app`, `start_server` from `ms_test/server.py` into new file; update uvicorn path to `"ms_test.application.app:create_app"` · `ms_test/src/ms_test/application/app.py`

**Checkpoint**: T002–T006 GREEN · `gep --type restapi` creates `application/app.py` with factory code

---

## Phase 4: User Story 2 — `server.py` Is a Thin Process Entry Point (Priority: P1)

**Goal**: The generated `server.py` contains only an import of `start_server` from `application.app` and a `__main__` guard — no factory logic, no `FastAPI`, no `Container`.

**Independent Test**: Inspect text of generated `server.py`; confirm `"FastAPI"` and `"Container"` are absent; confirm `"application.app import start_server"` is present.

### Tests for User Story 2 *(write first — must fail before T013–T014)*

- [X] T010 [US2] Add `test_restapi_server_py_is_thin_wrapper` — run `gep`, read `server.py`, assert `"FastAPI"` not in content and content line-count (non-blank, non-comment) ≤ 5 · `tests/commands/test_generate_entry_point.py`
- [X] T011 [P] [US2] Add `test_entry_point_restapi_server_is_thin_wrapper` — render `server.py.jinja2`, assert `"FastAPI"` not in output and `"Container"` not in output · `tests/templates/test_entry_point_templates.py`
- [X] T012 [P] [US2] Add `test_entry_point_restapi_server_imports_start_server` — render `server.py.jinja2`, assert `"application.app import start_server"` in output · `tests/templates/test_entry_point_templates.py`

### Implementation for User Story 2

- [X] T013 [US2] Replace full content of `server.py.jinja2` with thin wrapper: module docstring + `from {{ project.python_package }}.application.app import start_server` + blank line + `if __name__ == "__main__": start_server()` · `src/scaffold_ca_python/templates/entry_point/restapi/server.py.jinja2`
- [X] T014 [P] [US2] Update ms_test reference `server.py` to thin wrapper — replace body with `from ms_test.application.app import start_server` + `if __name__ == "__main__": start_server()` · `ms_test/src/ms_test/server.py`

**Checkpoint**: T010–T012 GREEN · generated `server.py` is thin; imports `start_server` from `application.app`

---

## Phase 5: User Story 3 — `main.py` Is Not Present in Generated Output (Priority: P1)

**Goal**: No `main.py` is written anywhere when `gep --type restapi` runs. Dry-run output lists `app.py` and new test files but never `main.py`.

**Independent Test**: Run `gep --type restapi` on a clean project; assert `Path("src/my_app/main.py").exists()` is `False`.

### Tests for User Story 3 *(write first — must fail before T016b–T017)*

- [X] T015 [US3] Add `test_restapi_no_main_py` — run `gep --type restapi`, assert `src/my_app/main.py` does **not** exist · `tests/commands/test_generate_entry_point.py`
- [X] T016 [P] [US3] Add `test_restapi_dry_run_includes_app_py_not_main` — run `gep --type restapi --dry-run`, assert `"app.py"` in output and `"main.py"` not in output (as a created file) · `tests/commands/test_generate_entry_point.py`
- [X] T016c [US3] Add `test_restapi_gep_twice_does_not_overwrite_app_py` — run `gep --type restapi`, record content of `application/app.py`, run `gep --type restapi` again (expect duplicate-dir error or no-op), assert content unchanged — **covers FR-007 for app.py** · `tests/commands/test_generate_entry_point.py`

### Implementation for User Story 3

- [X] T016b [US3] Update existing main.py-related tests in `test_generate_entry_point.py` — **before** removing the overwrite block: delete `test_restapi_overwrites_main_py` and `test_gep_prints_main_py_warning` (both assert old behaviour that is being removed); update `test_dry_run_does_not_overwrite_main_py` to assert `main.py` is untouched because gep *never creates it* (not merely because dry-run skipped it) · `tests/commands/test_generate_entry_point.py`
- [X] T017 [US3] Delete the `"Overwrite main.py"` block from `_generate_entry_point_impl` (~8 lines: the console warning, `main_tpl`, `main_content`, `overwrite_op`, and `writer.execute` call) · `src/scaffold_ca_python/commands/generate_entry_point.py`

**Checkpoint**: T015–T016b GREEN, T016b passes after edit · T017 removes the block · no `main.py` emitted for restapi type; dry-run output correct

---

## Phase 6: User Story 4 — Every Generated File Has a Corresponding Test Template (Priority: P2)

**Goal**: `gep --type restapi` emits five test files (one per source file). Every generated test file is immediately runnable by `pytest` without modification.

**Independent Test**: Run `gep --type restapi` on a clean project; confirm all five test files exist; count them.

### Tests for User Story 4 *(write first — must fail before T026–T031)*

- [X] T018 [US4] Add `test_restapi_creates_test_app` — run `gep`, assert `tests/application/test_app.py` exists · `tests/commands/test_generate_entry_point.py`
- [X] T019 [P] [US4] Add `test_restapi_creates_test_server` — run `gep`, assert `tests/infrastructure/entry_points/api/v1/test_server.py` exists · `tests/commands/test_generate_entry_point.py`
- [X] T020 [P] [US4] Add `test_restapi_creates_test_exception_handler` — run `gep`, assert `tests/infrastructure/entry_points/api/v1/test_exception_handler.py` exists · `tests/commands/test_generate_entry_point.py`
- [X] T021 [P] [US4] Add `test_restapi_creates_test_schemas` — run `gep`, assert `tests/infrastructure/entry_points/api/v1/test_schemas.py` exists · `tests/commands/test_generate_entry_point.py`
- [X] T022 [P] [US4] Add `test_entry_point_restapi_test_app_template_has_create_app_assertion` — render `test_app.py.jinja2`, assert `"create_app"` and `"FastAPI"` in output · `tests/templates/test_entry_point_templates.py`
- [X] T023 [P] [US4] Add `test_entry_point_restapi_test_server_template_references_start_server` — render `test_server.py.jinja2`, assert `"start_server"` in output · `tests/templates/test_entry_point_templates.py`
- [X] T024 [P] [US4] Add `test_entry_point_restapi_test_exception_handler_template_has_status_codes` — render `test_exception_handler.py.jinja2`, assert `"422"` or `"HTTPException"` in output · `tests/templates/test_entry_point_templates.py`
- [X] T025 [P] [US4] Add `test_entry_point_restapi_test_schemas_template_has_example_response` — render `test_schemas.py.jinja2`, assert `"ExampleResponse"` in output (matching actual `schemas.py.jinja2` which defines `ExampleResponse`, not `ErrorResponse`) · `tests/templates/test_entry_point_templates.py`

### Implementation for User Story 4

- [X] T026 [P] [US4] Create `test_app.py.jinja2` — generates a pytest file that: imports `create_app` from `application.app`, asserts return type is `FastAPI`, asserts router included, asserts exception handlers registered · `src/scaffold_ca_python/templates/entry_point/restapi/test_app.py.jinja2`
- [X] T027 [P] [US4] Create `test_server.py.jinja2` — generates a pytest file that: imports `start_server` from `application.app`, asserts it is callable, asserts importing `server` module does not raise · `src/scaffold_ca_python/templates/entry_point/restapi/test_server.py.jinja2`
- [X] T028 [P] [US4] Create `test_exception_handler.py.jinja2` — generates pytest + TestClient tests asserting `HTTPException` → JSON with `status_code`, `RequestValidationError` → 422, unhandled `Exception` → 500 · `src/scaffold_ca_python/templates/entry_point/restapi/test_exception_handler.py.jinja2`
- [X] T029 [P] [US4] Create `test_schemas.py.jinja2` — generates a pytest file that: imports `ExampleResponse` from `schemas` (matching actual `schemas.py.jinja2`), asserts it is a Pydantic model, asserts it has a `message` field · `src/scaffold_ca_python/templates/entry_point/restapi/test_schemas.py.jinja2`
- [X] T030 [US4] Update `_build_operations` restapi branch — add `CreateFile` for `project_root / "tests" / "application" / "test_app.py"` using `test_app.py.jinja2` (note: custom path, not `test_dir`) · `src/scaffold_ca_python/commands/generate_entry_point.py`
- [X] T031 [US4] Update `_build_operations` restapi branch — add three `_test(...)` calls for `test_server.py.jinja2 → test_server.py`, `test_exception_handler.py.jinja2 → test_exception_handler.py`, `test_schemas.py.jinja2 → test_schemas.py` in `test_dir` · `src/scaffold_ca_python/commands/generate_entry_point.py`

**Checkpoint**: T018–T025 GREEN · all 5 test files emitted by `gep --type restapi`

---

## Phase 7: Polish & Quality Gates

**Purpose**: Confirm all linting, type-checking, and coverage gates pass across every new and modified file.

- [X] T032 [P] Run `uv run ruff check src/ tests/` — zero lint errors
- [X] T033 [P] Run `uv run ruff format --check src/ tests/` — zero format violations
- [X] T034 [P] Run `uv run mypy src/` — zero type errors (strict mode)
- [X] T035 Run `uv run pytest tests/ --cov=src --cov-fail-under=80` — ≥ 80% line coverage; ≥ 466 tests passing (450 baseline + 16+ new)
- [X] T036 End-to-end smoke test per [quickstart.md](quickstart.md) — scaffold a fresh `demo_api` project, run `gep --type restapi`, confirm `application/app.py` exists, `main.py` absent, `server.py` thin; run generated tests

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: N/A — infrastructure already exists
- **Phase 3 (US1)**: Depends on Phase 1 ✅
- **Phase 4 (US2)**: Depends on Phase 3 complete (server.py.jinja2 imports from app.py; app.py must exist)
- **Phase 5 (US3)**: Depends on Phase 1 only; can run in parallel with Phase 3/4 if desired
- **Phase 6 (US4)**: Depends on Phase 3 (app.py template exists) and Phase 4 (server.py template updated)
- **Phase 7 (Polish)**: Depends on all story phases complete

### User Story Dependencies

- **US1 (P1)**: Depends on Phase 1 only
- **US2 (P1)**: Depends on US1 (server.py must import from application.app, which requires app.py.jinja2 to exist)
- **US3 (P1)**: Independent of US1 and US2 — the main.py removal is a separate code block
- **US4 (P2)**: Depends on US1 and US2 (all source templates must be in final form before test templates reference them)

### Within Each User Story

- RED tests MUST be written and confirmed FAILING before implementation tasks begin
- Multiple template-creation tasks within the same story marked `[P]` can be written simultaneously (different files)
- `_build_operations` changes (T008, T030, T031) each go to the same file but are sequential edits within that function

### Parallel Opportunities (per story)

**US1 (Phase 3)**:
```
T002 (command test) ──────────────────────────────► T008 (register in command)
T003, T004, T005, T006 [P] (template tests) ──────► T007 (create template) ──► T009 [P] (ms_test)
```

**US2 (Phase 4)**:
```
T010 (command test) ──────────────────────────────► T013 (update template)
T011, T012 [P] (template tests) ──────────────────► T014 [P] (ms_test update)
```

**US4 (Phase 6)**:
```
T018–T021 [P] (command tests) ──────────────────────┐
T022–T025 [P] (template rendering tests) ────────────┼──► T026–T029 [P] (create 4 templates) ──► T030, T031
```

---

## Implementation Strategy

**MVP scope**: Complete through Phase 5 (US1 + US2 + US3). At that point:
- `gep --type restapi` produces the correct architectural split
- No `main.py` is emitted
- The generated project is fully functional

**Increment 2**: Phase 6 (US4) adds per-file test templates — high quality-of-life improvement but not blocking a working split.

**Suggested commit checkpoints**:
1. After Phase 3: `feat: add application/app.py.jinja2 — factory and lifespan`
2. After Phase 4: `feat: server.py.jinja2 becomes thin wrapper`
3. After Phase 5: `feat: remove main.py emission from restapi generator`
4. After Phase 6: `feat: add test templates for all restapi generated files`
5. After Phase 7: `chore: quality gates — ruff, mypy, coverage`
