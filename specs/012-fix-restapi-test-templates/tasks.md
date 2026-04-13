# Tasks: Fix RestAPI Entry Point Test Templates

**Input**: Design documents from `/specs/012-fix-restapi-test-templates/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Tests**: Constitution Principle V — TDD enforced. All RED tests are written before implementation tasks.

**Organization**: Tasks are grouped by user story. US1 (generated project tests pass) and US2 (CLI internal test suite passes) are both P1 and can be worked in parallel after foundational Phase 2.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on in-progress tasks)
- **[Story]**: Which user story this task maps to
- Exact file paths are included in all descriptions

---

## Phase 1: Setup

**Purpose**: Confirm baseline and orient against the current test state.

- [X] T001 Run `uv run pytest --ignore=tests/performance --no-cov -q` from repo root and record: 476 passing, 8 pre-existing failures (`test_restapi_main_has_fastapi_import`, `test_restapi_main_has_create_app`, `test_restapi_creates_schemas`, `test_restapi_creates_test_schemas`, `test_restapi_dry_run_lists_all_planned_files_and_writes_nothing`, `test_swagger_schemas_contains_routes`, `test_restapi_router_has_async_def`, `test_entry_point_restapi_test_schemas_template_has_example_response`)

**Checkpoint**: Baseline confirmed — all subsequent phases must not introduce new failures.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Remove the two stale CLI tests that reference the non-existent `main.py.jinja2`. These deletions are prerequisites for both US1 and US2 because the stale tests pollute the test count and make RED/GREEN tracking ambiguous.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [X] T002 Delete `test_restapi_main_has_fastapi_import` from `tests/templates/test_entry_point_templates.py` (FR-006 — `main.py.jinja2` no longer exists for restapi; research Q7)
- [X] T003 Delete `test_restapi_main_has_create_app` from `tests/templates/test_entry_point_templates.py` (FR-006 — same reason as T002; do in the same edit as T002, same file — not parallelizable)

**Checkpoint**: Foundation ready — 2 stale tests removed, 6 remaining pre-existing failures, 476 passing. User story work can now begin in parallel.

---

## Phase 3: User Story 1 — Generated RestAPI Project Tests Pass Out of the Box (Priority: P1) 🎯 MVP

**Goal**: Rewrite `test_rest_controller.py.jinja2` so that `scaffold gep --type restapi` generates a `test_rest_controller.py` whose import resolves correctly (`application.app`, not `server`) and whose content appears exactly once (no duplicate block).

**Independent Test**: `scaffold ca --name TestProj && cd test_proj && scaffold gep --type restapi && uv run pytest tests/ --no-cov -q` → exit 0, all generated tests pass.

### Tests for User Story 1 *(write first — confirm RED)*

- [X] T004 [US1] Add `test_generated_test_rest_controller_imports_application_app` to `tests/templates/test_entry_point_templates.py`: render `entry_point/restapi/test_rest_controller.py.jinja2` with a minimal context, assert `"application.app" in rendered_output` and `"server import" not in rendered_output` — confirm test is RED before T006
- [X] T005 [P] [US1] Add `test_generated_test_rest_controller_has_no_duplicate_docstring` to `tests/templates/test_entry_point_templates.py`: render `test_rest_controller.py.jinja2`, assert `rendered_output.count('"""Tests') == 1` (module-level docstring sentinel appears exactly once) — confirm test is RED before T006

### Implementation for User Story 1

- [X] T006 [US1] Rewrite `src/scaffold_ca_python/templates/entry_point/restapi/test_rest_controller.py.jinja2`: single unified block importing `create_app` from `{{ project.python_package }}.application.app`, one `@pytest.fixture` returning `TestClient(create_app())`, two tests (`test_health_returns_200`, `test_health_returns_online_status` with `response.json().get("status") is not None` assertion) — confirms T004 and T005 turn GREEN

**Checkpoint**: T004 and T005 are GREEN. `test_rest_controller.py.jinja2` is correct. End-to-end generated project `uv run pytest` passes for the controller.

---

## Phase 4: User Story 2 — CLI Verification Tests for RestAPI Templates Pass (Priority: P1)

**Goal**: Create the three missing Jinja2 templates (`schemas.py.jinja2`, `test_schemas.py.jinja2`, `router.py.jinja2`), wire the first two into `_build_operations`, and add CLI rendering tests for all three. This resolves the 6 remaining pre-existing failures.

**Independent Test**: `uv run pytest tests/commands/test_generate_entry_point.py tests/templates/test_entry_point_templates.py --no-cov -q` → 0 failures (excluding the 2 pre-existing `generate_project` tombstones).

### Tests for User Story 2 *(write first — confirm RED)*

- [X] T007 [US2] Add `test_entry_point_restapi_schemas_template_has_example_response` to `tests/templates/test_entry_point_templates.py`: render `entry_point/restapi/schemas.py.jinja2` with a minimal context (no routes), assert `"ExampleResponse" in rendered_output` — confirm RED (template does not exist yet)
- [X] T008 [P] [US2] Add `test_entry_point_restapi_schemas_template_has_base_model` to `tests/templates/test_entry_point_templates.py`: render `schemas.py.jinja2`, assert `"BaseModel" in rendered_output` — confirm RED
- [X] T009 [P] [US2] Confirm `test_entry_point_restapi_test_schemas_template_has_example_response` is already present in `tests/templates/test_entry_point_templates.py` and is RED (template absent). If the test is absent, add it following the pattern of T007 before proceeding to T012.
- [X] T010 [P] [US2] Confirm `test_restapi_router_has_async_def` is present in `tests/templates/test_entry_point_templates.py` and is RED. If the test is absent, add it following the pattern of T008 (render `entry_point/restapi/router.py.jinja2`, assert `"async def" in rendered_output`) before proceeding to T013.

### Implementation for User Story 2

- [X] T011 [US2] Create `src/scaffold_ca_python/templates/entry_point/restapi/schemas.py.jinja2`: Pydantic v2 `class ExampleResponse(BaseModel): status: str = "ok"` as body; `{% if routes %}` block for optional route-based response stubs using `routes` context variable — resolves T007 and T008
- [X] T012 [P] [US2] Create `src/scaffold_ca_python/templates/entry_point/restapi/test_schemas.py.jinja2`: import `ExampleResponse` from `{{ project.python_package }}.infrastructure.entry_points.api.v1.schemas`; one test `test_example_response_is_valid_schema` asserting `ExampleResponse().status == "ok"` — resolves T009 and `test_entry_point_restapi_test_schemas_template_has_example_response`
- [X] T013 [P] [US2] Create `src/scaffold_ca_python/templates/entry_point/restapi/router.py.jinja2`: standalone `APIRouter` with `async def health()` endpoint returning `{"status": "ok"}`; this template is NOT added to `_build_operations` (supplemental, FR-005) — resolves T010 and `test_restapi_router_has_async_def`. Do NOT add an entry for `router.py` in `generate_entry_point.py`.
- [X] T014 [US2] Wire schemas into `_build_operations` in `src/scaffold_ca_python/commands/generate_entry_point.py`: in the `restapi` branch, add after `exception_handler.py.jinja2` entry — `_src("schemas.py.jinja2", "schemas.py")` and `_test("test_schemas.py.jinja2", "test_schemas.py")` — (FR-007; research Q6). Resolves `test_restapi_creates_schemas`, `test_restapi_creates_test_schemas`, `test_restapi_dry_run_lists_all_planned_files_and_writes_nothing`, `test_swagger_schemas_contains_routes`.

**Checkpoint**: All 6 pre-existing failures are now GREEN. T007–T010 are GREEN. Total: ≥ 486 passing (476 baseline + 2 new T004/T005 + 2 new T007/T008 + 6 fixed pre-existing = 486 passing). Note: deleting 2 failing tests in Phase 2 does not affect the passing count.

---

## Phase 5: Quality Gates

**Purpose**: Confirm no regressions, verify coverage, and run end-to-end smoke test.

- [X] T015 [P] Run `uv run ruff check src/ tests/` — zero lint errors
- [X] T016 [P] Run `uv run ruff format --check src/ tests/` — zero format violations (fix with `uv run ruff format src/ tests/` if needed)
- [X] T017 [P] Run `uv run mypy src/` — zero **new** type errors (the 2 pre-existing `generate_project` tombstone errors are out of scope)
- [X] T018 Run `uv run pytest tests/ --ignore=tests/performance --cov=src --cov-fail-under=80 -q` — ≥ 80% coverage; ≥ 486 passing tests (476 baseline + 2 T004/T005 + 2 T007/T008 + 6 fixed pre-existing = 486); only the 2 pre-existing `generate_project` tombstone failures remain
- [X] T019 [P] Verify dry-run output: `scaffold gep --type restapi --dry-run` in a scaffolded project lists `schemas.py` among planned files (SC-004); also confirm `router.py` does NOT appear in the dry-run output (FR-005)
- [X] T020 Smoke test end-to-end: `cd /tmp && scaffold ca --name SmokeTest && cd smoke_test && scaffold gep --type restapi && uv run pytest tests/ --no-cov -q` → exit 0 (SC-001). Also verify: (a) `src/smoke_test/infrastructure/entry_points/api/v1/schemas.py` exists on disk (SC-005); (b) `tests/infrastructure/entry_points/api/v1/test_schemas.py` exists on disk (SC-005); (c) all four test files `test_rest_controller.py`, `test_exception_handler.py`, `test_server.py`, `test_schemas.py` are present under `tests/infrastructure/entry_points/api/v1/` (US1/AC4)

**Checkpoint**: All quality gates pass. Feature 012 is complete.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — confirm baseline immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — T002/T003 can be a single file edit; BLOCKS Phase 3 and 4
- **Phase 3 (US1)**: Depends on Phase 2 — T004/T005 (RED tests) can be written in parallel with Phase 3 implementation
- **Phase 4 (US2)**: Depends on Phase 2 — can proceed in parallel with Phase 3
- **Phase 5 (Quality Gates)**: Depends on Phases 3 and 4 complete

### User Story Dependencies

- **US1 (Phase 3)**: Independent of US2 — single template rewrite
- **US2 (Phase 4)**: Independent of US1 — new templates + wire-up
- No cross-story integration required

### Within Each Phase

- RED tests must be confirmed failing before their implementation task runs
- T006 (implementation) depends on T004 + T005 (tests) being RED
- T011/T012/T013 (implementation) depend on T007/T008/T009/T010 (tests) being RED or confirmed
- T014 (wire-up) depends on T011 + T012 being complete

---

## Parallel Example: Phase 4 (US2)

```bash
# Step A — write RED tests first (T007, T008, T009, T010 can be batched)
# All go into tests/templates/test_entry_point_templates.py

# Step B — implement in parallel (different files):
# Worker 1: T011 (schemas.py.jinja2)
# Worker 2: T012 (test_schemas.py.jinja2)
# Worker 3: T013 (router.py.jinja2)

# Step C — wire-up (T014, depends on B):
# Single edit to generate_entry_point.py _build_operations
```

---

## Implementation Strategy

**MVP = Phase 3 (US1) alone**: Fixes the most visible user-facing bug (generated tests fail immediately with ImportError). Can be shipped independently.

**Full feature = Phase 3 + Phase 4**: Adds missing schemas templates and fixes all CLI internal test failures. Required for a clean CI baseline.

**Recommended order**: Phase 1 → Phase 2 → Phase 3 and Phase 4 in parallel → Phase 5.
