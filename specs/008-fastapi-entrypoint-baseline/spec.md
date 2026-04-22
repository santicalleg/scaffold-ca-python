# Feature Specification: FastAPI Entry Point Baseline Alignment

**Feature Branch**: `008-fastapi-entrypoint-baseline`  
**Created**: 2026-03-31  
**Status**: Draft  
**Input**: User description: "Improve FastAPI entry point generation aligned with ms_test baseline"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Baseline Structure Alignment (Priority: P1)

As a developer, I want `scaffold gep --type restapi` to produce a project layout that matches the ms_test reference baseline — including versioned API routing (`api/v1/`), an application config layer with DI containers, custom exception handling, and a uvicorn server entry point driven by environment settings — so that the scaffolded project is runnable without manual adjustments.

**Why this priority**: The generated project is currently not runnable as-is because it lacks the `application/config/` DI wiring, versioned routing, settings-driven server launch, and `Dockerfile`/`mypy.ini` prerequisite files. This is the highest-risk gap and blocks all downstream use.

**Independent Test**: Run `scaffold gep --type restapi` on a fresh CA project; the resulting project must start with `uvicorn` and respond to `GET /v1/health` with HTTP 200 without any manual edits.

**Acceptance Scenarios**:

1. **Given** a fresh CA project with no entry points, **When** `scaffold gep --type restapi` runs, **Then** the following files are created: `infrastructure/entry_points/api/v1/__init__.py`, `infrastructure/entry_points/api/v1/rest_controller.py`, `infrastructure/entry_points/api/v1/exception_handler.py`, `infrastructure/entry_points/api/v1/schemas.py`, `src/<package>/server.py`. Note: `application/config/`, `Dockerfile`, and `mypy.ini` are already emitted by `scaffold ca` and are not re-emitted by `gep`.
2. **Given** a generated project, **When** the server starts, **Then** `GET /v1/health` returns `{"status": "app is online"}` with HTTP 200.
3. **Given** generation completes, **When** `pyproject.toml` is inspected, **Then** `dependency-injector>=4.49.0`, `fastapi[standard]>=0.135.2`, and `pydantic-settings>=2.13.1` are present in the runtime dependency list.
4. **Given** any file already exists at a target path, **When** `scaffold gep --type restapi` runs without `--force`, **Then** the existing file is not overwritten and a notice is shown.
5. **Given** `--dry-run` is passed, **When** the command runs, **Then** all planned file operations are printed but no files are written.

---

### User Story 2 — Test Template Scaffolding (Priority: P2)

As a developer, I want `scaffold gep --type restapi` to generate test templates for the health endpoint and application bootstrap so that the project supports TDD immediately after scaffolding.

**Why this priority**: Without test templates, developers must write boilerplate before writing their first test. This reduces time-to-first-test but does not block the project from running, so it is P2.

**Independent Test**: After generation, `uv run pytest` in the generated project discovers and runs the generated test files without configuration changes.

**Acceptance Scenarios**:

1. **Given** FastAPI entry point generation completes, **When** pytest discovers tests, **Then** `tests/infrastructure/entry_points/api/v1/test_rest_controller.py` is found and contains at least one runnable test.
2. **Given** the generated test file, **When** a developer reads it, **Then** it includes: a `TestClient` fixture with DI override placeholder, a test for `GET /v1/health` asserting HTTP 200, and a comment block marking where custom assertions should be added.
3. **Given** the test file already exists, **When** `scaffold gep --type restapi` is run again, **Then** the test file is not overwritten and a "skipped — already exists" message is shown.
4. **Given** `--dry-run` is passed, **When** the command runs, **Then** the planned test file path is listed in the output but not created.

---

### User Story 3 — Entry Point Compatibility Guard (Priority: P1)

As a developer, I want the generator to block FastAPI entry point creation when an MCP or Agent entry point already exists in the project so that incompatible runtime compositions are caught before any files are written.

**Why this priority**: Allowing mixed FastAPI + MCP or FastAPI + Agent in one project creates an unrunnable artefact. Blocking this early prevents silent corruption of the project structure.

**Independent Test**: Run `scaffold gep --type restapi` in a project that already has an `mcp` or `agent` entry point; the command must exit 1 with a clear error message and leave the filesystem unchanged.

**Acceptance Scenarios**:

1. **Given** `infrastructure/entry_points/mcp_server/` exists, **When** `scaffold gep --type restapi` is invoked, **Then** the command exits 1 with "Incompatible entry point: mcp_server already exists" and a hint to remove it first.
2. **Given** `infrastructure/entry_points/agent/` exists, **When** `scaffold gep --type restapi` is invoked, **Then** the command exits 1 with "Incompatible entry point: agent already exists" and a resolution hint.
3. **Given** neither mcp nor agent entry points exist, **When** `scaffold gep --type restapi` is invoked, **Then** generation proceeds normally.
4. **Given** a compatibility failure, **When** the user reads the output, **Then** the message specifies which conflicting entry point was found and which actions resolve it.
5. **Given** `--dry-run` is passed alongside a conflict, **When** the command runs, **Then** the conflict is still detected and reported as an error (dry run does not bypass guards).

---

### Edge Cases

- What happens when `pyproject.toml` already has a `dependency-injector` entry at a different version? Generation must not add a duplicate; it should check for presence and skip or warn.
- What happens when only some files from the baseline exist (partial previous generation)? Missing files are created; existing files are skipped; a per-file status summary is printed.
- What happens when the project root cannot be detected (not inside a scaffold project)? Command exits 1 with the standard "run `scaffold ca` first" hint.
- What happens when `--dry-run` is combined with `--swagger`? Swagger parsing occurs (to list planned routes) but no files are written.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The generator MUST produce the following files under `infrastructure/entry_points/api/v1/` when `--type restapi` is used: `__init__.py`, `rest_controller.py`, `exception_handler.py`, `schemas.py`. Note: `application/config/` is already emitted by `scaffold ca`; `gep` MUST NOT re-emit those files.
- **FR-002**: The generator MUST place the REST controller under `infrastructure/entry_points/api/v1/rest_controller.py` (versioned path, replacing the current flat `restapi/router.py` path).
- **FR-003**: The generator MUST create `infrastructure/entry_points/api/v1/exception_handler.py` with handlers for `Exception`, `HTTPException`, and `RequestValidationError`.
- **FR-004**: The generator MUST create `server.py` at the project package root (`src/<package>/server.py`) as the uvicorn launch entry point, reading `HOST` and `PORT` from settings.
- **FR-005**: The generator MUST create `server.py` at the project package root (`src/<package>/server.py`) as the uvicorn/FastAPI application factory. Note: `Dockerfile` and `mypy.ini` are already emitted by `scaffold ca`; `gep` MUST NOT re-emit them.
- **FR-006**: The generator MUST inject `dependency-injector>=4.49.0` and `pydantic-settings>=2.13.1` into `pyproject.toml` (alongside the existing `fastapi[standard]>=0.135.2`) without duplicating already-present entries.
- **FR-007**: The generator MUST create test templates under `tests/infrastructure/entry_points/api/v1/test_rest_controller.py` including a `TestClient` fixture and a health endpoint test.
- **FR-008**: Generated test files MUST be pytest-discoverable without additional configuration.
- **FR-009**: If `infrastructure/entry_points/mcp_server/` exists in the project, `scaffold gep --type restapi` MUST exit 1 before writing any file.
- **FR-010**: If `infrastructure/entry_points/agent/` exists in the project, `scaffold gep --type restapi` MUST exit 1 before writing any file.
- **FR-011**: Compatibility guard errors MUST include actionable resolution hints naming the conflicting path and suggesting removal.
- **FR-012**: No existing file MUST be overwritten unless `--force` is passed; each skipped file MUST be noted in output.
- **FR-013**: `--dry-run` MUST report all planned file operations (including test templates and `pyproject.toml` injections) without writing anything; compatibility guards still run in dry-run mode.
- **FR-014**: All error paths (missing project root, dependency drift, compatibility violation) MUST exit with a non-zero code and a human-readable message.

### Key Entities

- **EntryPointType**: The type discriminant for `scaffold gep --type`; values `restapi`, `mcp`, `agent`, `generic`. This feature focuses on `restapi`.
- **ProjectBaseline**: The required file and directory set derived from `ms_test`; used as the authoritative reference for what a runnable FastAPI CA project must contain.
- **DependencySet**: The set of runtime dependencies required for a FastAPI project — `fastapi[standard]`, `dependency-injector`, `pydantic-settings` — injected idempotently into `pyproject.toml`.
- **CompatibilityViolation**: A detected state where `mcp_server/` or `agent/` entry point directories already exist and `restapi` generation is therefore blocked.
- **TestTemplate**: a generated pytest file placed in the test mirror tree, providing a `TestClient` fixture and at least one passing health test.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A project generated with `scaffold gep --type restapi` starts with `uvicorn` and returns HTTP 200 on `GET /v1/health` without any manual edits to the generated files.
- **SC-002**: `uv run pytest` in the generated project discovers and passes the generated health test with zero configuration steps beyond `uv sync`.
- **SC-003**: 100% of compatibility guard tests pass — every MCP or Agent conflict scenario results in exit code 1 and no file writes.
- **SC-004**: All error messages produced by the generator include a specific resolution hint (no bare "Error" messages without guidance).
- **SC-005**: `--dry-run` produces a complete list of planned operations and writes zero files across all code paths, verified by the test suite.

## Assumptions

- The generated project uses `uv` for dependency management; `pyproject.toml` is present and writable.
- The `dependency-injector` version constraint (`>=4.49.0`) and `pydantic-settings` constraint (`>=2.13.1`) are treated as the minimum acceptable versions; tighter pinning is left to the developer.
- `application/config/` files contain stub implementations (placeholder comments) rather than real business logic; the developer fills them in.
- `Dockerfile` uses a multi-stage Python build targeting Python 3.13; the exact base image is chosen to stay consistent with the `ms_test` baseline.
- `mypy.ini` is generated with strict mode enabled and `python_version = 3.13`, matching the `ms_test` baseline.
- The compatibility guard checks for the presence of the entry point directory (`mcp_server/` or `agent/`) rather than inspecting file contents, which is consistent with how the existing generator creates those directories.
- MCP + Agent coexistence (without FastAPI) is not affected by this feature; only FastAPI-vs-others conflicts are guarded.
- Swagger (`--swagger`) support is preserved and continues to inject routes into the versioned controller; this feature does not remove that capability.

