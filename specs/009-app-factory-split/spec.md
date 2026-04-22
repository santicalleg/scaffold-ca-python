# Feature Specification: App Factory Split — server.py / app.py Separation

**Feature Branch**: `009-app-factory-split`  
**Created**: 2026-04-10  
**Status**: Draft  
**Input**: User description: "Split server.py into app.py factory and thin server.py entry point; remove main.py; add per-file test coverage"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - App Factory Code Lives in `app.py` (Priority: P1)

As a developer running `scaffold gep --type restapi`, I want the generated project to include
`application/app.py` that owns the FastAPI application factory and lifecycle management, so that the
application creation logic is separated from the process entry point and is independently testable.

**Why this priority**: This is the core architectural change. Every other story depends on `app.py`
existing. Without it, `server.py` cannot become a thin wrapper and test coverage cannot be added per-file.

**Independent Test**: Can be fully tested by running `scaffold gep --type restapi` on a fresh project
and verifying that `application/app.py` is present and contains a callable that returns a configured
application instance, with no process-launch side-effects.

**Acceptance Scenarios**:

1. **Given** a developer runs the restapi entry-point generator, **When** generation completes, **Then** the file `application/app.py` exists in the output directory.
2. **Given** the generated `application/app.py`, **When** its factory callable is invoked, **Then** it returns a fully configured application instance with routers and exception handlers registered.
3. **Given** the generated `application/app.py`, **When** it is imported, **Then** no server process is started and no side-effects occur.
4. **Given** the generated `application/app.py`, **When** its lifecycle management is inspected, **Then** it wires and tears down the dependency-injection container around each application lifespan event.

---

### User Story 2 - `server.py` Is a Thin Process Entry Point (Priority: P1)

As a developer, I want the generated `server.py` to contain only the minimal code required to launch
the application (delegating all factory logic to `application/app.py`), so that process-start
concerns are cleanly separated from application-assembly concerns.

**Why this priority**: Equal priority with US1 — together they form the split. A fat `server.py` that
still duplicates factory code defeats the purpose of the feature.

**Independent Test**: Can be fully tested by inspecting the generated `server.py`; it must import from
the `application` layer and call a single start method with no additional logic.

**Acceptance Scenarios**:

1. **Given** a developer runs the restapi entry-point generator, **When** generation completes, **Then** `server.py` exists at the project root and contains ≤ 5 non-blank, non-comment lines.
2. **Given** the generated `server.py`, **When** its source is inspected, **Then** it imports the application object from `application.app` and calls its start method — no factory or lifecycle code is present in `server.py` itself.
3. **Given** the generated `server.py`, **When** it is executed as the entry point, **Then** the application starts, serving requests on the configured host and port.

---

### User Story 3 - `main.py` Is Not Present in Generated Output (Priority: P1)

As a developer, I want the restapi generator to produce `server.py` as the sole process entry point
without also emitting a `main.py`, so that there is no ambiguity about how to start the service.

**Why this priority**: The current scaffold emits `main.py` alongside `server.py`, creating confusion
about which file is the actual entry point. Removing it is a correctness fix with zero complexity.

**Independent Test**: Can be fully tested by running the restapi generator on a clean directory and
asserting that no file named `main.py` is created anywhere in the output tree.

**Acceptance Scenarios**:

1. **Given** a developer runs `scaffold gep --type restapi` on a clean project, **When** generation completes, **Then** no `main.py` file exists in the generated output.
2. **Given** an existing project that already has a `main.py` (created by a prior run of a different generator), **When** the restapi generator is run without `--force`, **Then** `main.py` is not touched or overwritten.
3. **Given** a developer inspects `pyproject.toml` scripts after generation, **When** the entry-point script is examined, **Then** it points to `server.py` (or its equivalent) and not `main.py`.

---

### User Story 4 - Every Generated File Has a Corresponding Test Template (Priority: P2)

As a developer, I want each file produced by `scaffold gep --type restapi` to have a matching test
file generated alongside it, so that the scaffolded project starts with a working test suite and
meaningful coverage from day one.

**Why this priority**: Lower priority than the structural split, but critical for quality. Missing
tests mean a developer must write them from scratch, defeating the value of the scaffold.

**Independent Test**: Can be fully tested by running the restapi generator and then executing
`pytest` inside the generated project — all generated test files must be discovered and pass.

**Acceptance Scenarios**:

1. **Given** a developer runs the restapi entry-point generator, **When** generation completes, **Then** a test file exists for each of the following: `application/app.py`, `server.py`, `api/v1/rest_controller.py`, `api/v1/exception_handler.py`, `api/v1/schemas.py`.
2. **Given** the generated test file for `application/app.py`, **When** the test suite is run, **Then** it verifies that the factory callable returns a correctly configured application instance and that the lifespan context manager wires the container.
3. **Given** all generated test files, **When** `pytest` is executed, **Then** every test passes without requiring any manual edits.
4. **Given** the generated test files, **When** a code-quality check is run, **Then** all test files pass linting and type-checking rules without errors.

---

### Edge Cases

- What happens when the target project already has an `application/app.py` from a previous run and `--force` is not supplied? The generator must not overwrite it.
- What happens when `server.py` already exists and `--force` is not supplied? The generator must not overwrite it.
- What happens when `main.py` already exists in the project (e.g., created manually)? The generator must not delete or modify it — only refrain from creating it.
- What happens when the `application/` directory does not yet exist? The generator must create it along with its `__init__.py`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The restapi generator MUST emit `application/app.py` containing the application factory callable and the lifecycle management (dependency-injection container wiring/unwiring).
- **FR-002**: The restapi generator MUST emit `server.py` as a thin entry point that imports from `application.app` and calls the start method; `server.py` MUST contain no factory or lifecycle logic of its own.
- **FR-003**: The restapi generator MUST NOT emit `main.py` as part of the restapi entry-point output.
- **FR-004**: The restapi generator MUST emit a test file for `application/app.py` that asserts the factory callable returns a configured application instance and that the lifespan context manager wires the container correctly.
- **FR-005**: The restapi generator MUST emit test files for `server.py`, `api/v1/rest_controller.py`, `api/v1/exception_handler.py`, and `api/v1/schemas.py`; each test file MUST be immediately executable by `pytest` without modification.
- **FR-006**: All generated source files and test files MUST pass the project's linting and static-type-checking rules without errors or warnings.
- **FR-007**: The generator MUST NOT overwrite any already-existing generated file unless the `--force` flag is provided.
- **FR-008**: The scaffold tool's own test suite (not the generated project's tests) MUST include template-rendering tests that verify the content of every new or modified Jinja2 template.

### Key Entities

- **AppFactory** (`application/app.py`): The generated module that owns the FastAPI application factory and lifecycle management. Key responsibilities: create and configure the application instance, manage container lifecycle via a context manager.
- **ServerEntryPoint** (`server.py`): The generated thin process-launch module. Single responsibility: import the application object from `application.app` and invoke its start method.
- **TestTemplate** (one per generated file): A Jinja2 template that renders a `pytest` test file asserting the correctness of the corresponding generated source file. One template per source template.
- **EntryPointGenerator**: The existing scaffold command that orchestrates file emission for the `restapi` type. Requires updates to add `app.py` emission, update `server.py` template, suppress `main.py` emission, and register the new test templates.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running `scaffold gep --type restapi` on a clean project produces exactly the expected set of files: `application/app.py`, `server.py`, `api/v1/rest_controller.py`, `api/v1/exception_handler.py`, `api/v1/schemas.py`, and one test file per source file — verified by an automated workflow test.
- **SC-002**: No `main.py` file is present anywhere in the generated restapi output — verified by a dedicated assertion in the workflow test.
- **SC-003**: All generated test files pass `pytest` without modification — verified by executing `pytest` inside a freshly generated project in CI.
- **SC-004**: The scaffold tool's overall test-suite passes (450+ tests) with no regressions after the feature is implemented.
- **SC-005**: All new and modified source files in the scaffold tool itself pass linting and static-type-checking with zero errors.
- **SC-006**: Template-rendering unit tests in the scaffold tool's test suite cover every new or modified Jinja2 template — verified by the coverage gate.

## Assumptions

- The `--force` overwrite guard is already implemented in the `FileWriter` component and applies to all emitted files; no new overwrite logic needs to be written.
- The `application/` directory with its `__init__.py` is already created by the `generate_project` command; the entry-point generator only needs to add `app.py` inside it.
- The `server.py` template currently used by feature 008 already exists and needs to be updated (not created from scratch).
- Test templates follow the naming convention `test_<source_file>.py.jinja2` and are placed in the same template sub-directory as the source template they test.
- The scaffold tool already has infrastructure (`TemplateRenderer`, `FileWriter`, `generate_entry_point.py`) that new templates can plug into without significant structural changes.
- Performance, scalability, and security concerns are out of scope; this feature is purely about code-generation structure.
- Mobile, web UI, and API versioning concerns are out of scope for this feature.
