# Feature Specification: Fix RestAPI Entry Point Test Templates

**Feature Branch**: `012-fix-restapi-test-templates`  
**Created**: 2026-04-10  
**Status**: Draft  
**Input**: User description: "When I create a new scaffold project and generates a restapi entry point, and I execute the test with pytest over the new project created with scaffold, the tests fail. The task is update the restapi entry point test_* templates, so, when a user generates the scaffold with restapi entrypoint, the tests pass correctly."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generated RestAPI Project Tests Pass Out of the Box (Priority: P1)

A developer runs `scaffold ca --name MyApp`, then `scaffold gep --type restapi`, then `cd my_app && uv run pytest`. Every generated test must pass without any manual edits to the generated code.

Currently the generated `test_rest_controller.py` imports `create_app` from `server` — which does not export that symbol — causing an `ImportError` at collection time that fails every test in the file. The template also emits a duplicate content block, producing a syntactically broken Python file with two module-level docstrings.

**Why this priority**: This is a developer-facing correctness bug that silently undermines the value proposition of the scaffold. A user who generates a project and immediately sees test failures loses trust in the tool.

**Independent Test**: Run `scaffold ca --name TestProj`, then `scaffold gep --type restapi`. In the generated project directory run `uv run pytest`. All tests must exit 0.

**Acceptance Scenarios**:

1. **Given** a freshly scaffolded CA project, **When** `gep --type restapi` runs and the user executes `pytest` in the generated project, **Then** all generated tests pass (exit code 0).
2. **Given** the generated `test_rest_controller.py`, **When** Python collects it, **Then** no `ImportError` is raised — the import path resolves correctly.
3. **Given** the generated `test_rest_controller.py`, **When** the user inspects it, **Then** each module-level docstring appears exactly once (no duplicate blocks).
4. **Given** `gep --type restapi` is run, **When** the user opens `tests/infrastructure/entry_points/api/v1/`, **Then** files `test_rest_controller.py`, `test_exception_handler.py`, `test_server.py`, and `test_schemas.py` are all present.

---

### User Story 2 - CLI Verification Tests for RestAPI Templates Pass (Priority: P1)

The scaffold-ca-python CLI's own test suite has pre-existing failures caused by missing Jinja2 templates (`schemas.py.jinja2`, `test_schemas.py.jinja2`, `router.py.jinja2`) and incorrect template-test references. These must be resolved so the CLI test suite returns to a clean baseline (excluding the two pre-existing `generate_project` tombstone failures).

**Why this priority**: A CLI that ships with a broken internal test suite cannot be confidently maintained. Equal priority to US1 because both block the feature's quality gates.

**Independent Test**: Run `uv run pytest tests/commands/test_generate_entry_point.py tests/templates/test_entry_point_templates.py --no-cov`. All tests that are not pre-existing tombstones must pass.

**Acceptance Scenarios**:

1. **Given** `gep --type restapi` runs, **When** the dry-run output is inspected, **Then** `schemas.py` appears in the listed files.
2. **Given** `gep --type restapi` runs, **When** the file system is inspected, **Then** both `schemas.py` and `test_schemas.py` exist at their expected paths under `infrastructure/entry_points/api/v1/`.
3. **Given** the `schemas.py.jinja2` template is rendered, **When** a swagger spec with routes is provided, **Then** the output references those routes.
4. **Given** the `test_schemas.py.jinja2` template is rendered, **When** Python collects it, **Then** it contains an `ExampleResponse` class or reference.
5. **Given** the `router.py.jinja2` template is rendered, **When** the output is inspected, **Then** it contains `async def`.
6. **Given** the two CLI template tests `test_restapi_main_has_fastapi_import` and `test_restapi_main_has_create_app`, **When** they run, **Then** they either pass (via a new `main.py.jinja2`) or are removed — because `main.py` is no longer generated for restapi projects (feature 011).

---

### Edge Cases

- What if `schemas.py.jinja2` is rendered without a swagger spec (no routes)? → The template must still emit a valid Python file with at least a placeholder `ExampleResponse` model.
- What if `test_schemas.py.jinja2` is rendered in a project with a non-standard package name? → The import paths must use `{{ project.python_package }}` throughout.
- What happens to `test_rest_controller.py.jinja2` in a project generated before this fix? → Existing projects are unaffected; the fix applies only to newly scaffolded projects.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The `test_rest_controller.py.jinja2` template MUST import `create_app` from `{{ project.python_package }}.application.app`, NOT from `{{ project.python_package }}.server`.
- **FR-002**: The `test_rest_controller.py.jinja2` template MUST emit its content exactly once — the duplicate block MUST be removed.
- **FR-003**: A `schemas.py.jinja2` template MUST exist and be rendered by `gep --type restapi` into `src/<pkg>/infrastructure/entry_points/api/v1/schemas.py`. When swagger routes are provided, the rendered file MUST reference those routes; without routes it MUST emit a placeholder `ExampleResponse` Pydantic model.
- **FR-004**: A `test_schemas.py.jinja2` template MUST exist and be rendered into `tests/infrastructure/entry_points/api/v1/test_schemas.py`. The rendered file MUST contain at least one test and reference `ExampleResponse`.
- **FR-005**: A `router.py.jinja2` template MUST exist in the restapi template directory. It MUST render to a valid Python file containing `async def`. This template does not need to be included in the set of files generated by `gep --type restapi`.
- **FR-006**: The two CLI template tests `test_restapi_main_has_fastapi_import` and `test_restapi_main_has_create_app` MUST be removed from `tests/templates/test_entry_point_templates.py`, because `main.py` is deleted for restapi projects by feature 011 and the referenced `main.py.jinja2` template serves no purpose.
- **FR-007**: `_build_operations` for the restapi type MUST include render operations for both `schemas.py.jinja2` → `schemas.py` and `test_schemas.py.jinja2` → `test_schemas.py`.
- **FR-008**: All existing passing tests MUST continue to pass after this feature is implemented (no regressions).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running `uv run pytest` in a freshly scaffolded restapi project exits with code 0 and all generated tests pass.
- **SC-002**: Running `uv run pytest tests/commands/test_generate_entry_point.py tests/templates/test_entry_point_templates.py --no-cov` in the CLI repository reports 0 failures (excluding the 2 pre-existing `generate_project` tombstones; those are out of scope).
- **SC-003**: The CLI test suite overall passing count increases by the number of new and fixed tests; no previously passing test is broken.
- **SC-004**: `gep --type restapi --dry-run` output lists `schemas.py` among the planned files.
- **SC-005**: `gep --type restapi` output includes `schemas.py` and `test_schemas.py` in the generated file set — verifiable by post-run filesystem check.

## Assumptions

- The `create_app` function lives in `<pkg>.application.app` — not in `<pkg>.server`. This was established by features 009 and 011 and is the correct import path for all generated tests.
- The `start_server` function also lives in `<pkg>.application.app`; `server.py` is a thin `__main__` wrapper that calls it without re-exporting it.
- The `ExampleResponse` Pydantic model in `schemas.py` serves as a placeholder; users are expected to replace it with their domain response models.
- Feature 011 (delete `main.py` for restapi) is already merged on branch `011-fix-restapi-cleanup`. This feature builds on that baseline.
- Fixing the test templates does NOT require changes to any source templates (`app.py.jinja2`, `server.py.jinja2`, `rest_controller.py.jinja2`, `exception_handler.py.jinja2`) — those are correct.
- The `test_exception_handler.py.jinja2` and `test_app.py.jinja2` templates are correct and generate passing tests; no changes needed there.

