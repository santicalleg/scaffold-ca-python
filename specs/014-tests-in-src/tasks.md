# Tasks: Move Tests to src/ Layout; Add Entrypoint Exclusivity Validation

**Feature**: `014-tests-in-src` | **Branch**: `014-tests-in-src`  
**Input**: [plan.md](plan.md), [spec.md](spec.md), [research.md](research.md), [data-model.md](data-model.md), [quickstart.md](quickstart.md)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no incomplete dependencies)
- **[Story]**: User story this task belongs to — [US1], [US2], [US3]
- All file paths are relative to the repository root

---

## Phase 1: Setup

**Purpose**: Baseline verification before any code changes.

- [X] T001 Run `uv run pytest tests/ --ignore=tests/performance --no-cov -q` and confirm baseline: 484 passing, 2 tombstone failures (`test_generate_project_tombstone_exits_1`, `test_generate_project_tombstone_exits_1_no_args`)

**Checkpoint**: Baseline confirmed. Zero regressions introduced before work begins.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Add `resolve_tests_root` utility and fix `pyproject_toml.jinja2`. These are *prerequisites* for every US1 command task and for US3 template correctness.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

### Tests for Foundational Phase *(write these first — they must be RED)*

- [X] T002 [P] Add `test_resolve_tests_root_returns_src_tests_when_src_tests_exists` to `tests/core/test_project_detector.py` — create tmp dir with `src/tests/` present; call `resolve_tests_root`; assert result == `tmp / "src" / "tests"`
- [X] T003 [P] Add `test_resolve_tests_root_falls_back_to_root_tests` to `tests/core/test_project_detector.py` — create tmp dir with `tests/` at root only (no `src/tests/`); assert result == `tmp / "tests"`
- [X] T004 [P] Add `test_resolve_tests_root_defaults_to_src_tests_when_neither_exists` to `tests/core/test_project_detector.py` — create empty tmp dir; assert result == `tmp / "src" / "tests"`
- [X] T005 Add `test_pyproject_template_testpaths_is_src_tests` to `tests/templates/test_project_templates.py` — render `project/pyproject_toml.jinja2` with `_ctx()`; assert `'testpaths = ["src/tests"]'` in output (currently fails — template has `"tests"`)
- [X] T006 [P] Add `test_pyproject_template_coverage_uses_package_variable` to `tests/templates/test_project_templates.py` — render template; assert `"mcp_server_code_review"` not in output AND `"ms_test"` not in output AND `'source = ["my_app"]'` in output (verifies `{{ python_package }}` is rendered)

### Implementation for Foundational Phase

- [X] T007 Add `resolve_tests_root(project_root: Path) -> Path` free function to `src/scaffold_ca_python/core/project_detector.py` — probe `src/tests/` first, then `tests/`, else default to `src/tests/`; confirm T002/T003/T004 turn GREEN
- [X] T008 Fix 4 fields in `src/scaffold_ca_python/templates/project/pyproject_toml.jinja2`: `testpaths = ["src/tests"]`; `"src/tests/**/*.py"` ruff per-file-ignores key; `source = ["{{ python_package }}"]`; `addopts = "--cov={{ python_package }} --cov-fail-under=80"`; confirm T005/T006 turn GREEN

**Checkpoint**: Foundation ready — `resolve_tests_root` importable; template renders correct paths. US1 and US3 command tasks can now begin.

---

## Phase 3: User Story 1 — src/tests/ Layout for All generate-* Commands (Priority: P1) 🎯 MVP

**Goal**: Every `scaffold ca` and `generate-*` command writes test files to `src/tests/` inside the generated project, not to `tests/` at the project root.

**Independent Test**: Run `scaffold ca --name LayoutTest && cd LayoutTest && ls src/tests/__init__.py` — no `tests/` at root. Run `gep --type restapi`, `gm`, `guc`, `gh`, `gda`; verify all create under `src/tests/`.

### Tests for User Story 1 *(update existing — they must go RED before implementation)*

- [X] T009 Update `tests/commands/test_generate_project.py` — change the 1 path assertion from `tests/__init__.py` to `src/tests/__init__.py`; add new test `test_ca_creates_src_tests_init` asserting `project_root / "src" / "tests" / "__init__.py"` is created by the runner; add `test_ca_dry_run_shows_src_tests_init` asserting `--dry-run` output contains `"src/tests/__init__.py"` and does NOT contain `"tests/__init__.py"`; confirm all RED
- [X] T010 [P] [US1] Update `tests/commands/test_generate_model.py` — change the 2 `tests/domain/model/...` path assertions to `src/tests/domain/model/...`; confirm RED
- [X] T011 [P] [US1] Update `tests/commands/test_generate_use_case.py` — change the 2 `tests/domain/usecase/...` path assertions to `src/tests/domain/usecase/...`; confirm RED
- [X] T012 [P] [US1] Update `tests/commands/test_generate_helper.py` — change the 2 `tests/infrastructure/helpers/...` path assertions to `src/tests/infrastructure/helpers/...`; confirm RED
- [X] T013 [P] [US1] Update `tests/commands/test_generate_driven_adapter.py` — change the 4 `tests/infrastructure/driven_adapters/...` path assertions to `src/tests/infrastructure/driven_adapters/...`; confirm RED
- [X] T014 [P] [US1] Update `tests/commands/test_delete_module.py` — change the 2 `tests_root = project_root / "tests"` path assertions to use `src/tests/`; confirm RED
- [X] T015 [US1] Update `tests/commands/test_generate_entry_point.py` — change all 13 `tests/infrastructure/entry_points/...` path assertions (including `shutil.rmtree` and `unlink` cleanup refs) to `src/tests/infrastructure/entry_points/...`; confirm RED
- [X] T016 [P] [US1] Update `tests/commands/test_performance.py` — change the 4 `tests/...` path assertions to `src/tests/...`; confirm RED

### Implementation for User Story 1

- [X] T017 [US1] Update `src/scaffold_ca_python/commands/generate_project.py` — change `target_dir / "tests" / "__init__.py"` to `target_dir / "src" / "tests" / "__init__.py"` (1 line); confirm T009 turns GREEN
- [X] T018 [P] [US1] Update `src/scaffold_ca_python/commands/generate_model.py` — add `from scaffold_ca_python.core.project_detector import resolve_tests_root` import; replace `project_root / "tests"` with `resolve_tests_root(project_root)` for `test_path`; confirm T010 GREEN
- [X] T019 [P] [US1] Update `src/scaffold_ca_python/commands/generate_use_case.py` — import `resolve_tests_root`; replace `project_root / "tests"` with `resolve_tests_root(project_root)` for `test_path`; confirm T011 GREEN
- [X] T020 [P] [US1] Update `src/scaffold_ca_python/commands/generate_helper.py` — import `resolve_tests_root`; replace `project_root / "tests"` with `resolve_tests_root(project_root)` for `test_dir`; confirm T012 GREEN
- [X] T021 [P] [US1] Update `src/scaffold_ca_python/commands/generate_driven_adapter.py` — import `resolve_tests_root`; replace `project_root / "tests"` with `resolve_tests_root(project_root)` for `test_dir`; confirm T013 GREEN
- [X] T022 [US1] Update `src/scaffold_ca_python/commands/generate_entry_point.py` (path only, NOT the guard) — import `resolve_tests_root`; replace `project_root / "tests"` with `resolve_tests_root(project_root)` for `test_dir` (line 134); confirm T015 path assertions GREEN (exclusivity tests still RED — expected)
- [X] T023 [US1] Update `src/scaffold_ca_python/commands/delete_module.py` — import `resolve_tests_root`; replace `project_root / "tests"` with `resolve_tests_root(project_root)` for `tests_root`; confirm T014 GREEN

**Checkpoint**: All US1 tests GREEN. `scaffold ca` + all `generate-*` commands write tests to `src/tests/`. T016 performance assertions also GREEN.

---

## Phase 4: User Story 2 — Bidirectional Entry Point Exclusivity (Priority: P1)

**Goal**: `gep --type mcp` and `gep --type agent` raise exit code 1 with a descriptive Rich error if a `restapi` entry point already exists. `gep --type generic` is always allowed regardless.

**Independent Test**: Scaffold a new project, add restapi entry point, then run `gep --type mcp` — must exit 1 with message containing `"restapi"`. Run `gep --type generic` in the same project — must exit 0.

### Tests for User Story 2 *(write these first — they must be RED)*

- [X] T024 [US2] Add `test_gep_mcp_blocked_when_restapi_exists` to `tests/commands/test_generate_entry_point.py` — scaffold project, create `restapi` entry point, run `gep --type mcp`; assert `result.exit_code == 1` and `"restapi"` in `result.output`; confirm RED
- [X] T025 [P] [US2] Add `test_gep_agent_blocked_when_restapi_exists` to `tests/commands/test_generate_entry_point.py` — same setup; run `gep --type agent`; assert `exit_code == 1` and `"restapi"` in output; confirm RED
- [X] T026 [P] [US2] Add `test_gep_generic_not_blocked_when_restapi_exists` to `tests/commands/test_generate_entry_point.py` — scaffold project with restapi entry point; run `gep --type generic`; assert `exit_code == 0`; confirm GREEN (no implementation needed — generic already allowed)

### Implementation for User Story 2

- [X] T027 [US2] Add reverse exclusivity guard in `src/scaffold_ca_python/commands/generate_entry_point.py` after the existing `if type_ == "restapi":` guard block — add `if type_ in ("mcp", "agent"):` block checking `restapi_dir = project_root / "src" / project_ctx.python_package / "infrastructure" / "entry_points" / "api"`; if exists: `console.print(...)` with Rich formatting and hint, then `raise typer.Exit(code=1) from None`; confirm T024/T025 turn GREEN; confirm T026 remains GREEN

**Checkpoint**: T024 + T025 GREEN. T026 confirms generic is unaffected. Existing `restapi→mcp/agent` guard tests still pass.

---

## Phase 5: User Story 3 — ms_test Reference Project (Priority: P2)

**Goal**: Create a fully functional reference project at `ms_test/` using the correct `src/tests/` layout, CA skeleton, and working health endpoint tests. This project serves as a living end-to-end validation of the generated layout.

**Independent Test**: `cd ms_test && uv run pytest -q` → exit 0 with all tests passing.

### Implementation for User Story 3

- [X] T028 [US3] Create `ms_test/pyproject.toml` — package name `ms_test`, `testpaths = ["src/tests"]`, `source = ["ms_test"]`, `addopts = "--cov=ms_test --cov-fail-under=80"`, per-file-ignores `"src/tests/**/*.py"`, dev deps: `httpx`, `pytest`, `pytest-cov`, `ruff`, `mypy`
- [X] T029 [P] [US3] Create ms_test source skeleton (19 files) in `ms_test/src/ms_test/`: `__init__.py`, `server.py`, `application/__init__.py`, `application/app.py` (returns FastAPI instance via `create_app()`), `application/config/__init__.py`, `application/config/config.py`, `application/config/container.py`, `application/config/driven_adapters_container.py`, `application/config/resource_container.py`, `application/config/usecases_container.py`, `domain/model/__init__.py`, `domain/usecase/__init__.py`, `infrastructure/driven_adapters/__init__.py`, `infrastructure/entry_points/__init__.py`, `infrastructure/entry_points/api/__init__.py`, `infrastructure/entry_points/api/v1/__init__.py`, `infrastructure/entry_points/api/v1/rest_controller.py` (FastAPI router with `GET /health` → `{"status": "ok"}`), `infrastructure/entry_points/api/v1/exception_handler.py`, `infrastructure/helpers/__init__.py`
- [X] T030 [US3] Create ms_test test structure (9 files) in `ms_test/src/tests/`: `__init__.py`, `application/__init__.py`, `application/test_app.py` (imports `create_app` from `ms_test.application.app`; asserts `isinstance(create_app(), FastAPI)`), `infrastructure/__init__.py`, `infrastructure/entry_points/__init__.py`, `infrastructure/entry_points/api/__init__.py`, `infrastructure/entry_points/api/v1/__init__.py`, `infrastructure/entry_points/api/v1/test_rest_controller.py` (uses `starlette.testclient.TestClient(create_app())`; calls `GET /health`; asserts `response.status_code == 200` and `response.json() == {"status": "ok"}`)
- [X] T031 [US3] Run `cd ms_test && uv sync` to generate `ms_test/uv.lock`; verify `uv run pytest -q` exits 0 from `ms_test/` directory

**Checkpoint**: ms_test fully functional. `cd ms_test && uv run pytest -q` exits 0 with health endpoint tests passing.

---

## Phase 6: Quality Gates

**Purpose**: Confirm the complete feature meets all constitutional gates before PR.

- [X] T032 [P] Run `uv run ruff check src/ tests/` from repo root — assert zero lint errors
- [X] T033 [P] Run `uv run ruff format --check src/ tests/` — assert zero format violations
- [X] T034 [P] Run `uv run mypy src/` — assert zero new type errors (pre-existing issues, if any, are not regressions from this feature)
- [X] T035 Run `uv run pytest tests/ --ignore=tests/performance --cov=src --cov-fail-under=80 -q` — assert ≥ 80% coverage; only 2 tombstone failures remain (`test_generate_project_tombstone_exits_1*`); total passing count ≥ 494 (484 baseline + 10 new: T002–T006 unit/template tests + T024/T025/T026 exclusivity tests + 2 from T009 `test_ca_creates_src_tests_init` and `test_ca_dry_run_shows_src_tests_init`)
- [X] T036 [P] Smoke test layout — run `scaffold ca --name SmokeTest` in a tmp dir; confirm `SmokeTest/src/tests/__init__.py` exists and `SmokeTest/tests/` does NOT exist
- [X] T037 [P] Smoke test exclusivity — scaffold project + add restapi entry point; run `gep --type mcp`; confirm exit code 1 and Rich error message contains hint about restapi
- [X] T038 Run ms_test smoke — `cd ms_test && uv run pytest -q` → exit 0, both test files pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 completion — **BLOCKS all user stories**
- **Phase 3 (US1)**: Depends on Phase 2 only — can start once `resolve_tests_root` is importable
- **Phase 4 (US2)**: Depends on Phase 2 + Phase 3 T022 (same file: `generate_entry_point.py`) — start T024–T025 tests immediately after Phase 2; write T027 after T022
- **Phase 5 (US3)**: Depends on Phase 2 (template fix in T008) — can overlap with Phase 3/4
- **Phase 6 (Quality Gates)**: Depends on Phases 3, 4, and 5 all complete

### User Story Dependencies

- **US1**: Depends only on Phase 2 (resolve_tests_root available)
- **US2**: Tests (T024–T026) can be written after Phase 2; implementation (T027) depends on T022 landing first (same file)
- **US3**: Depends only on Phase 2 (template fixed); fully independent of US1 and US2

### Within Each Phase

- Tests MUST be RED before implementation starts (Constitution Principle V)
- Tests marked [P] within the same phase can be written in parallel (they target different files or isolated functions)
- Implementation tasks marked [P] can run in parallel once their prerequisite test exists

---

## Parallel Opportunities

### Phase 2 — Foundational tests (run together)

```
Task: T002 — test_resolve_tests_root_returns_src_tests_when_src_tests_exists
Task: T003 — test_resolve_tests_root_falls_back_to_root_tests
Task: T004 — test_resolve_tests_root_defaults_to_src_tests_when_neither_exists
Task: T005 — test_pyproject_template_testpaths_is_src_tests
Task: T006 — test_pyproject_template_coverage_uses_package_variable
```

### Phase 3 — US1 test updates (run together after T009)

```
Task: T010 — test_generate_model.py (2 paths)
Task: T011 — test_generate_use_case.py (2 paths)
Task: T012 — test_generate_helper.py (2 paths)
Task: T013 — test_generate_driven_adapter.py (4 paths)
Task: T014 — test_delete_module.py (2 paths)
Task: T016 — test_performance.py (4 paths)
```

### Phase 3 — US1 implementation (run together after T017)

```
Task: T018 — generate_model.py
Task: T019 — generate_use_case.py
Task: T020 — generate_helper.py
Task: T021 — generate_driven_adapter.py
```

### Phase 4 — US2 exclusivity tests (run together)

```
Task: T025 — test_gep_agent_blocked_when_restapi_exists
Task: T026 — test_gep_generic_not_blocked_when_restapi_exists
```

### Phase 5 — US3 source + test creation (run together)

```
Task: T029 — ms_test source skeleton (19 files)
Task: T030 — ms_test test structure (depends on T029 for imports)
```

---

## Implementation Strategy

### MVP First (US1 + US2, P1 stories only)

1. Complete Phase 1: Baseline
2. Complete Phase 2: Foundational (`resolve_tests_root` + template fixes)
3. Complete Phase 3: US1 — all generate-* commands write to `src/tests/`
4. Complete Phase 4: US2 — bidirectional exclusivity for `gep`
5. **STOP and VALIDATE**: Run full test suite → ≥ 493 passing
6. US3 can land in a follow-up if time is constrained

### Incremental Delivery

1. Phase 1 + 2 → locked-in `resolve_tests_root` utility (unblocks US1 and US3)
2. Phase 3 → `src/tests/` layout across all commands (US1 complete, independently testable)
3. Phase 4 → bidirectional exclusivity guard (US2 complete, independently testable)
4. Phase 5 → ms_test reference project (US3 complete)
5. Phase 6 → quality gates on the full feature

### Task Count Summary

| Phase | Tasks | New Tests Added |
|-------|-------|-----------------|
| Phase 1 — Setup | 1 | 0 |
| Phase 2 — Foundational | 7 | 5 (T002–T006) |
| Phase 3 — US1 | 15 | 2 (`test_ca_creates_src_tests_init`, `test_ca_dry_run_shows_src_tests_init`) |
| Phase 4 — US2 | 4 | 3 (T024–T026) |
| Phase 5 — US3 | 4 | 2 (`test_app.py`, `test_rest_controller.py`) |
| Phase 6 — Quality Gates | 7 | 0 |
| **Total** | **38** | **12** |

**Baseline**: 484 passing / 2 tombstone failures  
**Target**: ≥ 494 passing / 2 tombstone failures (unchanged) / ≥ 80% coverage
