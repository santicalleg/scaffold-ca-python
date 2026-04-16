# Tasks: PEP 8 / PEP 423 Naming Validation

**Feature**: `017-pep8-naming-validation`  
**Branch**: `017-pep8-naming-validation`  
**Input**: Design documents from `/specs/017-pep8-naming-validation/`  
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/ ✅

**Tests**: Per constitution Principle V, tests are MANDATORY and written BEFORE implementation (TDD).  
**Organization**: Grouped by user story — each story is independently testable.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no shared state)
- **[US1/US2/US3]**: Which user story the task belongs to
- Exact file paths included in every task

---

## Phase 1: Setup

**Purpose**: Confirm the baseline is clean before making any changes.

- [X] T001 Record baseline test count and verify all tests pass: `uv run pytest --ignore=tests/performance -q`

---

## Phase 2: Foundational

No blocking foundational work is needed. All stories build directly on the existing `name_utils.py` and `context.py` utilities. Proceed to user story phases.

---

## Phase 3: User Story 1 — Reject invalid project name at input (Priority: P1) 🎯 MVP

**Goal**: Any scaffold command rejects `--name` values that are not `kebab-case` or `snake_case`, exiting 1 with a message that mentions both accepted formats.

**Independent Test**: `scaffold ca --name MyProject` exits 1 and output contains `"kebab-case"`. `scaffold ca --name my-project --dry-run` exits 0.

### Tests for User Story 1 *(write FIRST — must FAIL before implementation)*

- [X] T002 [US1] Update `tests/core/test_name_utils.py`: invert `test_validate_name_accepts_pascal_case` to assert `ScaffoldError` is raised for `"MyProject"`, rename `test_validate_name_rejects_hyphens` to `test_validate_name_accepts_kebab_case` and assert it returns `"my-project"` (no exception)
- [X] T003 [P] [US1] Add unit tests to `tests/core/test_name_utils.py` for `validate_name`: `test_validate_name_accepts_multi_word_kebab` (`"my-order-service"` → accepted), `test_validate_name_rejects_camel_case` (`"myProject"` → `ScaffoldError` matching `"kebab-case"`), `test_validate_name_rejects_pascal_case` (`"MyProject"` → `ScaffoldError` matching `"kebab-case"`), `test_validate_name_rejects_mixed_case_with_hyphen` (`"My-Project"` → `ScaffoldError`), `test_validate_name_rejects_consecutive_hyphens` (`"my--project"` → `ScaffoldError`), `test_validate_name_rejects_leading_hyphen` (`"-myproject"` → `ScaffoldError`), `test_validate_name_rejects_trailing_underscore` (`"myproject_"` → `ScaffoldError`)
- [X] T004 [P] [US1] Add CLI integration test to `tests/commands/test_generate_project.py`: `runner.invoke(app, ["ca", "--name", "MyProject"])` → `exit_code == 1`, `"kebab-case" in output`
- [X] T005 [P] [US1] Add CLI integration tests for all remaining commands in `tests/commands/test_generate_model.py`, `tests/commands/test_generate_use_case.py`, `tests/commands/test_generate_helper.py`, `tests/commands/test_generate_driven_adapter.py`, `tests/commands/test_delete_module.py`: for each command (`gm`, `guc`, `gh`, `gda`, `dm`), assert `runner.invoke(app, ["<alias>", "--name", "InvalidName"])` → `exit_code == 1`, `"kebab-case" in result.output`

### Pre-implementation: Update existing tests to use snake_case / kebab-case names

> **⚠️ These MUST run before T006/T007 — they migrate the 110 existing PascalCase `--name` invocations that would otherwise break when the regex is tightened.**

- [X] T006a [P] [US1] Update `tests/commands/test_generate_project.py`: replace all PascalCase `--name` values — `"MyProject"` → `"my-project"`, `"SimpleApp"` → `"simple-app"`, `"Demo"` → `"demo"`, `"DryProject"` → `"dry-project"`. Update any assertions that reference derived identifiers (e.g. directory name `my_project/`, class text `"MyProject"` in output) to match the new names.
- [X] T006b [P] [US1] Update `tests/commands/test_generate_use_case.py`, `tests/commands/test_generate_model.py`, `tests/commands/test_generate_helper.py`: replace `"CreateOrder"` → `"create-order"`, `"PlaceOrder"` → `"place-order"`, `"CancelOrder"` → `"cancel-order"`, `"MyApp"` → `"my-app"`. Update output assertions accordingly.
- [X] T006c [P] [US1] Update `tests/commands/test_generate_driven_adapter.py`, `tests/commands/test_generate_entry_point.py`, `tests/commands/test_delete_module.py`: replace all PascalCase `--name` values with `kebab-case` equivalents. Update any output assertions (directory names, class names, file stems) accordingly.
- [X] T006d [P] [US1] Update `tests/commands/test_dry_run_checksum.py`, `tests/commands/test_workflow.py`, `tests/commands/test_validate_structure.py`, `tests/commands/test_generate_pipeline.py`, `tests/commands/test_update_project.py`: replace all PascalCase `--name` values with `kebab-case` equivalents. Update output assertions accordingly.

### Implementation for User Story 1

- [X] T007 [US1] Update `src/scaffold_ca_python/core/name_utils.py`: replace `_NAME_RE` with `re.compile(r"^[a-z][a-z0-9]*([_-][a-z0-9]+)*$")` and update `validate_name` error message to `f"Invalid name {name!r}. Use kebab-case (e.g., 'my-project') or snake_case (e.g., 'my_project')."`
- [X] T008 [P] [US1] Update `src/scaffold_ca_python/models/context.py`: replace module-level `_NAME_RE` with `re.compile(r"^[a-z][a-z0-9]*([_-][a-z0-9]+)*$")` and update the error message in both `ProjectContext._validate_name` and `ModuleContext._validate_name` to match the new wording from T007

**Checkpoint**: US1 fully functional — `scaffold ca --name MyProject` exits 1 with an actionable error. `scaffold ca --name my-project --dry-run` and `scaffold ca --name my_project --dry-run` both exit 0.

---

## Phase 4: User Story 2 — Generated module files always use snake_case (Priority: P2)

**Goal**: When a `kebab-case` name is accepted, all generated `.py` file names are normalised to `snake_case` (e.g., `my-project` → `my_project/__init__.py`).

**Independent Test**: `scaffold ca --name my-project --dry-run` output lists only file paths whose stem matches `[a-z][a-z0-9_]*`.

### Tests for User Story 2 *(write FIRST — must FAIL before implementation)*

- [X] T009 [US2] Add unit tests to `tests/core/test_name_utils.py`: `test_to_snake_case_from_kebab` (`to_snake_case("my-project") == "my_project"`), `test_to_snake_case_multi_word_kebab` (`to_snake_case("my-order-service") == "my_order_service"`)
- [X] T010 [P] [US2] Add integration test to `tests/commands/test_generate_project.py`: invoke `["ca", "--name", "my-project", "--dry-run"]` in a `tmp_path`, assert no generated file path contains a hyphen or uppercase letter in its stem

### Implementation for User Story 2

- [X] T011 [US2] Update `to_snake_case` in `src/scaffold_ca_python/core/name_utils.py`: prepend `name = name.replace("-", "_")` as the first line of the function body (before the `_CAMEL_BOUNDARY_RE.sub` call)
- [X] T012 [P] [US2] Update `_to_snake_case` in `src/scaffold_ca_python/models/context.py`: prepend `name = name.replace("-", "_")` as the first line of the function body

**Checkpoint**: US2 fully functional — `scaffold ca --name my-project --dry-run` generates a `my_project/` directory tree with only `snake_case` file names.

---

## Phase 5: User Story 3 — Generated class definitions always use PascalCase (Priority: P3)

**Goal**: All class names emitted in generated `.py` files are `PascalCase`, regardless of whether the input was `kebab-case` or `snake_case`.

**Independent Test**: `scaffold gm --name my-model --dry-run` produces a file containing `class MyModel(BaseModel):`.

### Tests for User Story 3 *(write FIRST — must FAIL before implementation)*

- [X] T013 [US3] Add unit tests to `tests/core/test_name_utils.py`: `test_to_pascal_case_from_snake_after_kebab_normalisation` — assert `to_pascal_case(to_snake_case("my-model")) == "MyModel"` and `to_pascal_case(to_snake_case("my-order-service")) == "MyOrderService"`
- [X] T014 [P] [US3] Add integration test to `tests/commands/test_generate_model.py`: invoke `["gm", "--name", "my-model"]` in a `tmp_path`, read the generated model `.py` file and assert it contains `"class MyModel"`

### Implementation for User Story 3

- [X] T015 [US3] Update `_to_pascal_case` in `src/scaffold_ca_python/models/context.py`: change `re.split(r"[_\s]+", name)` to `re.split(r"[_\s-]+", name)` so hyphens are also treated as word separators (defence-in-depth for direct `ModuleContext` usage with kebab input)

**Checkpoint**: US3 fully functional — all generated class definitions are `PascalCase` for both `kebab-case` and `snake_case` input names.

---

## Phase 6: Polish & Quality Gates

**Purpose**: Ensure no new ruff violations, no new mypy errors, and coverage gate is met.

- [X] T016 [P] Run `uv run ruff check src/ tests/` and fix any new violations introduced by T007–T015
- [X] T017 [P] Run `uv run mypy src/` and fix any new strict-mode errors introduced by T007–T015
- [X] T018 Run `uv run pytest --ignore=tests/performance` and confirm: all previously passing tests still pass, all new tests pass, coverage ≥ 80%

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 3 (US1)**: Depends on Phase 1. Tests T002–T005 must be written and failing; T006a–T006d must migrate existing tests; then T007–T008 implement the regex change
- **Phase 4 (US2)**: Depends on Phase 3 completion (name validation must be in place before normalisation is tested end-to-end)
- **Phase 5 (US3)**: Depends on Phase 4 completion (hyphen→snake normalisation must work before pascal derivation is verified)
- **Phase 6 (Quality Gates)**: Depends on all implementation tasks (T007–T015) being complete

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories — implement first, delivers the MVP
- **US2 (P2)**: Depends on US1 being complete (kebab input must be accepted before normalisation can be tested via CLI)
- **US3 (P3)**: Depends on US2 being complete (snake_case normalisation must work before PascalCase derivation is verified)

### Parallel Opportunities Per Story

**US1**: T003, T004, T005 can run in parallel (different test files). T006a, T006b, T006c, T006d can run in parallel (different test files). T007 and T008 can run in parallel (different source files).  
**US2**: T010 can run in parallel with T009 (different files). T011 and T012 can run in parallel.  
**US3**: T014 can run in parallel with T013 (different files).  
**Quality gates**: T016 and T017 can run in parallel.

---

## Implementation Strategy

**MVP scope**: Phase 3 (US1) alone is a shippable increment — it enforces the naming rule at input and prevents any non-compliant artifact from being generated.

**Incremental delivery**:
1. Complete Phase 3 → merge as MVP
2. Complete Phase 4 → guarantees snake_case file names for kebab input
3. Complete Phase 5 → guarantees PascalCase class names for kebab input
4. Complete Phase 6 → all quality gates green

**Total tasks**: 21  
**Tasks per user story**: US1=10 (incl. 4 test-migration tasks), US2=4, US3=3, Setup+Quality=4  
**Parallel opportunities**: 12 tasks marked `[P]`
