# Tasks: FastAPI Entry Point Baseline Alignment

**Input**: Design documents from `/specs/008-fastapi-entrypoint-baseline/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/gep.md ✅, quickstart.md ✅

**TDD strictly enforced (Principle V)**: Within every user story phase, all test tasks MUST be written and confirmed failing before the corresponding implementation tasks begin.

**Organization**: Tasks grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no pending dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Exact file paths included in all descriptions

---

## Phase 1: Setup

**Purpose**: No new project initialization required — this is a modification of an existing CLI tool. Phase 1 is intentionally minimal.

- [X] T001 Verify branch `008-fastapi-entrypoint-baseline` is checked out and `uv sync` is clean

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add the missing `resource_container.py.jinja2` template to the project template set. This is required by `server.py` DI wiring and by `container.py` (already emitted by `scaffold ca`). It must be present before US1 template work begins.

**⚠️ CRITICAL**: US1 work (Phase 4) depends on this phase being complete.

### Tests for Foundational Phase *(write FIRST, confirm failing)*

- [X] T002 [P] Write failing test `test_project_resource_container_has_declarative_container` in `tests/templates/test_project_templates.py` that renders `project/application/config/resource_container.py.jinja2` and asserts it contains `DeclarativeContainer` and `pydantic_settings`

### Implementation for Foundational Phase

- [X] T003 Add `resource_container.py.jinja2` to `src/scaffold_ca_python/templates/project/application/config/resource_container.py.jinja2` — stub `ResourceContainer(containers.DeclarativeContainer)` that wires `Settings` from `{{ python_package }}.application.config.config`
- [X] T004 Register `resource_container.py.jinja2` in the `application/config/` emission block of `src/scaffold_ca_python/commands/generate_project.py` (alongside the existing five config templates)

**Checkpoint**: `uv run pytest tests/templates/test_project_templates.py -k resource_container` must be green before proceeding to Phase 3.

---

## Phase 3: User Story 3 — Entry Point Compatibility Guard (Priority: P1)

**Goal**: `scaffold gep --type restapi` exits 1 with an actionable error message when `mcp_server/` or `agent/` entry point directories already exist, without writing any files.

**Independent Test**: In a project containing `src/<pkg>/infrastructure/entry_points/mcp_server/`, run `scaffold gep --type restapi`. Command must exit code 1, print the conflict path and a resolution hint, and leave the filesystem unchanged.

### Tests for User Story 3 *(write FIRST, confirm failing)*

- [X] T005 [P] [US3] Write failing test `test_gep_restapi_blocked_when_mcp_server_exists` in `tests/commands/test_generate_entry_point.py` — creates `mcp_server/` dir in tmp project, invokes `gep --type restapi`, asserts exit code 1, no `api/v1/` directory created
- [X] T006 [P] [US3] Write failing test `test_gep_restapi_blocked_when_agent_exists` in `tests/commands/test_generate_entry_point.py` — creates `agent/` dir in tmp project, invokes `gep --type restapi`, asserts exit code 1, no `api/v1/` directory created
- [X] T007 [P] [US3] Write failing test `test_gep_restapi_proceeds_when_no_incompatible_entry_point` in `tests/commands/test_generate_entry_point.py` — clean project, asserts generation proceeds normally (exit 0)
- [X] T008 [P] [US3] Write failing test `test_gep_restapi_dry_run_still_reports_mcp_conflict` in `tests/commands/test_generate_entry_point.py` — `mcp_server/` + `--dry-run` → exit 1, no files written

### Implementation for User Story 3

- [X] T009 [US3] Add compatibility guard loop in `src/scaffold_ca_python/commands/generate_entry_point.py` — immediately after project root discovery, before the duplicate-directory guard: iterate `("mcp_server", "agent")`, check for dir existence, print Rich error with conflicting path + resolution hint, raise `typer.Exit(code=1)`

**Checkpoint**: `uv run pytest tests/commands/test_generate_entry_point.py -k "blocked_when or proceeds_when or dry_run_still_reports"` must be green before proceeding to Phase 4.

---

## Phase 4: User Story 1 — Baseline Structure Alignment (Priority: P1)

**Goal**: `scaffold gep --type restapi` produces a versioned `api/v1/` layout with `rest_controller.py`, `exception_handler.py`, `server.py`, updated dependencies, and all pyproject.toml injections matching the ms_test baseline.

**Independent Test**: Run `scaffold gep --type restapi` on a fresh CA project; verify `infrastructure/entry_points/api/v1/rest_controller.py`, `exception_handler.py`, `schemas.py`, `__init__.py`, and `src/<pkg>/server.py` are created; verify pyproject.toml contains `fastapi[standard]>=0.135.2`, `dependency-injector>=4.49.0`, `pydantic-settings>=2.13.1`.

### Tests for User Story 1 *(write FIRST, confirm failing)*

- [X] T010 [P] [US1] Write failing test `test_entry_point_restapi_rest_controller_has_apirouter` in `tests/templates/test_entry_point_templates.py` — renders `entry_point/restapi/rest_controller.py.jinja2`, asserts contains `APIRouter`, `async def`, `/health`
- [X] T011 [P] [US1] Write failing test `test_entry_point_restapi_exception_handler_has_http_exception` in `tests/templates/test_entry_point_templates.py` — renders `entry_point/restapi/exception_handler.py.jinja2`, asserts contains `HTTPException`, `RequestValidationError`
- [X] T012 [P] [US1] Write failing test `test_entry_point_restapi_server_has_fastapi_factory` in `tests/templates/test_entry_point_templates.py` — renders `entry_point/restapi/server.py.jinja2`, asserts contains `FastAPI`, `lifespan`, `Container`, `start_server`
- [X] T013 [US1] Update path assertions in `tests/commands/test_generate_entry_point.py` — change all `entry_points/restapi/` path references to `entry_points/api/v1/` and add assertions for `server.py` at package root

### Implementation for User Story 1

- [X] T014 [P] [US1] Add `rest_controller.py.jinja2` to `src/scaffold_ca_python/templates/entry_point/restapi/rest_controller.py.jinja2` — `APIRouter(prefix="/v1")` with `GET /health` endpoint returning `{"status": "app is online"}` using `async def`; wire into `server.py` app (see ms_test baseline)
- [X] T015 [P] [US1] Add `exception_handler.py.jinja2` to `src/scaffold_ca_python/templates/entry_point/restapi/exception_handler.py.jinja2` — handlers for `Exception`, `HTTPException`, `RequestValidationError`; no Jinja2 variables needed (pure Python)
- [X] T016 [P] [US1] Add `server.py.jinja2` to `src/scaffold_ca_python/templates/entry_point/restapi/server.py.jinja2` — `create_app()` factory with `lifespan` that wires `Container`, reads `HOST`/`PORT` from `Settings`, registers exception handlers and routers; also exposes `start_server()` entry point; uses `{{ python_package }}` variable
- [X] T017 [US1] Update `_build_operations("restapi", ...)` in `src/scaffold_ca_python/commands/generate_entry_point.py`:
  - Change subdir from `"restapi"` to `"api/v1"` (emit into `infrastructure/entry_points/api/v1/`)
  - Replace emitted file list: `__init__.py`, `rest_controller.py`, `exception_handler.py`, `schemas.py` (remove `health.py`, `router.py`, `main.py` from emission)
  - Add `server.py` operation emitting to `src/<pkg>/server.py` (package root)
  - Keep `entrypoint_main.py.jinja2` → `main.py` overwrite (unchanged)
- [X] T018 [US1] Update `_DEP_MAP["restapi"]` in `src/scaffold_ca_python/commands/generate_entry_point.py` to `["fastapi[standard]>=0.135.2", "uvicorn[standard]>=0.20", "dependency-injector>=4.49.0", "pydantic-settings>=2.13.1"]`
- [X] T018b [US1] Write failing test `test_gep_restapi_dry_run_lists_all_planned_files_and_writes_nothing` in `tests/commands/test_generate_entry_point.py` — invokes `gep --type restapi --dry-run` on a clean project, asserts exit 0, asserts output contains all six planned file paths (`__init__.py`, `rest_controller.py`, `exception_handler.py`, `schemas.py`, `server.py`, `test_rest_controller.py`), and asserts none of those files were created on disk (FR-013, SC-005)

**Checkpoint**: `uv run pytest tests/commands/test_generate_entry_point.py tests/templates/test_entry_point_templates.py` must be green before proceeding to Phase 5.

---

## Phase 5: User Story 2 — Test Template Scaffolding (Priority: P2)

**Goal**: `scaffold gep --type restapi` generates `tests/infrastructure/entry_points/api/v1/test_rest_controller.py` with a `TestClient` fixture and a health endpoint test that is immediately pytest-discoverable.

**Independent Test**: After generation, `uv run pytest tests/infrastructure/entry_points/api/v1/test_rest_controller.py` in the generated project must pass with zero configuration.

### Tests for User Story 2 *(write FIRST, confirm failing)*

- [ ] T019 [P] [US2] Write failing test `test_entry_point_restapi_test_rest_controller_has_testclient` in `tests/templates/test_entry_point_templates.py` — renders `entry_point/restapi/test_rest_controller.py.jinja2`, asserts contains `TestClient`, `GET /v1/health`, `assert response.status_code == 200`

### Implementation for User Story 2

- [ ] T020 [P] [US2] Add `test_rest_controller.py.jinja2` to `src/scaffold_ca_python/templates/entry_point/restapi/test_rest_controller.py.jinja2` — imports `TestClient` from `starlette.testclient`, imports `create_app` from `{{ python_package }}.server`, tests `GET /v1/health` → HTTP 200, includes a comment block for custom DI overrides
- [ ] T021 [US2] Add test template emission to `_build_operations("restapi", ...)` in `src/scaffold_ca_python/commands/generate_entry_point.py` — emit `test_rest_controller.py.jinja2` into `tests/infrastructure/entry_points/api/v1/test_rest_controller.py` with `overwrite=False`
- [ ] T022 [US2] Update `tests/commands/test_generate_entry_point.py` to assert that `tests/infrastructure/entry_points/api/v1/test_rest_controller.py` is in the generated file list for `--type restapi`

**Checkpoint**: All three story phases (US3, US1, US2) fully green. `uv run pytest` must pass 100%.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T023 [P] Run `uv run ruff check src/ tests/` — fix any ruff violations introduced by new templates or command changes
- [ ] T024 [P] Run `uv run mypy src/` — fix any mypy strict violations in `generate_entry_point.py` or `generate_project.py`
- [ ] T025 Run `uv run pytest --cov=scaffold_ca_python --cov-report=term-missing` — confirm overall coverage ≥ 80% gate passes
- [ ] T026 Validate quickstart.md scenario: scaffold a CA project, run `scaffold gep --type restapi`, confirm generated file tree matches quickstart.md section "After generation"

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS US1 (Phase 4)
- **US3 (Phase 3)**: Depends on Phase 1 only — can proceed in parallel with Phase 2
- **US1 (Phase 4)**: Depends on Phase 2 (foundational) complete
- **US2 (Phase 5)**: Depends on Phase 4 (US1 restructured `_build_operations`)
- **Polish (Phase 6)**: Depends on all story phases complete

### User Story Dependencies

- **US3 (P1)**: Independent — can run concurrently with Phase 2
- **US1 (P1)**: Requires Phase 2 complete; independent of US3 (different code paths)
- **US2 (P2)**: Requires US1 complete (depends on `_build_operations` restructure from T017)

### Files Modified Per Story

| File | Phase 2 | US3 | US1 | US2 | Polish |
|------|---------|-----|-----|-----|--------|
| `generate_project.py` | T004 | — | — | — | — |
| `generate_entry_point.py` | — | T009 | T017, T018 | T021 | — |
| `tests/commands/test_generate_entry_point.py` | — | T005–T008 | T013 | T022 | — |
| `tests/templates/test_entry_point_templates.py` | — | — | T010–T012 | T019 | — |
| `tests/templates/test_project_templates.py` | T002 | — | — | — | — |
| NEW `resource_container.py.jinja2` | T003 | — | — | — | — |
| NEW `rest_controller.py.jinja2` | — | — | T014 | — | — |
| NEW `exception_handler.py.jinja2` | — | — | T015 | — | — |
| NEW `server.py.jinja2` | — | — | T016 | — | — |
| NEW `test_rest_controller.py.jinja2` | — | — | — | T020 | — |

### Parallel Opportunities Within Each Story

- **Phase 2**: T002 (test) can be written while confirming foundational scope; T003 and T002 can be done in parallel (different files)
- **Phase 3 (US3)**: T005, T006, T007, T008 are all `[P]` — write all four failing tests simultaneously before T009
- **Phase 4 (US1)**: T010, T011, T012 are `[P]` — write all three template tests simultaneously; T014, T015, T016 are `[P]` — add all three templates simultaneously; T017, T018 are sequential changes to the same file
- **Phase 5 (US2)**: T019 (test) and T020 (template) are `[P]` — write simultaneously; T021 depends on T017 (same function in generate_entry_point.py)

---

## MVP Scope

**Suggested MVP**: Phase 2 + Phase 3 (Foundational + US3 guard) — delivers the safety guard without touching template complexity. Low risk, high protective value.

**Full P1 MVP**: Phase 2 + Phase 3 + Phase 4 (US1) — delivers a runnable FastAPI baseline. Recommended for immediate stakeholder demo.

---

## Implementation Strategy

1. **Red phase** (per story): Write all test tasks for the story, run the suite, confirm new tests fail.
2. **Green phase**: Implement until all tests pass.
3. **Refactor**: Run ruff + mypy; fix violations before moving to next story.
4. **Repeat** for each story in priority order: US3 → US1 → US2.
5. **Polish phase last**: Full coverage check and quickstart validation.

Total tasks: **27** (T001–T026, T018b)  
Parallelizable tasks: T002, T003, T005–T008, T010–T012, T014–T016, T019–T020, T023–T024
