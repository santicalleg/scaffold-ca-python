# Feature Specification: Fix RestAPI Entry Point Cleanup

**Feature Branch**: `010-fix-restapi-cleanup`  
**Created**: 2026-04-10  
**Status**: Draft  
**Input**: User description: "fix some issues when create a restapi entry point: 1. Delete main.py file because restapi entry point creates a server.py module to execute the app. 2. Update pyproject.toml [project.scripts] to point to server:start_server"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - `main.py` Is Removed When a RestAPI Entry Point Is Scaffolded (Priority: P1)

A developer runs `scaffold ca` which creates a default `main.py`. Later they run `gep --type restapi`, which sets up a FastAPI application and a `server.py` entry point. The old `main.py` is now irrelevant and misleading — the project should no longer contain it after the restapi setup completes.

**Why this priority**: `main.py` left behind after `gep --type restapi` causes confusion: the project has two apparent entry points. Removing it is the single most visible correctness fix and is the prerequisite for the `pyproject.toml` scripts update to mean anything.

**Independent Test**: Run `scaffold ca --name MyApp`, then `gep --type restapi`. Assert that `src/my_app/main.py` does **not** exist immediately after the command completes.

**Acceptance Scenarios**:

1. **Given** a fresh CA project with `main.py` created by `scaffold ca`, **When** `gep --type restapi` runs, **Then** `src/<package>/main.py` no longer exists on disk.
2. **Given** a project where `main.py` was already manually deleted, **When** `gep --type restapi` runs, **Then** the command completes successfully without error (no-op delete).
3. **Given** a project with a restapi entry point already present, **When** `gep --type restapi` is run a second time, **Then** the command exits with an error (duplicate guard) and `main.py` is not re-created.

---

### User Story 2 - `pyproject.toml` `[project.scripts]` Points to `server:start_server` After RestAPI Scaffolding (Priority: P1)

After `gep --type restapi` runs, the executable entry point registered in `pyproject.toml` must call `start_server()` from `server.py` (not `main()` from `main.py`, which no longer exists). A developer must be able to install the package and run the project CLI command immediately.

**Why this priority**: Without this fix the installed CLI command points to a deleted module and crashes on every invocation. Equal priority to US1 — both are correctness bugs.

**Independent Test**: Run `scaffold ca --name MyApp`, then `gep --type restapi`. Inspect `pyproject.toml` — the `[project.scripts]` entry must read `my_app = "my_app.server:start_server"`.

**Acceptance Scenarios**:

1. **Given** a fresh CA project with `[project.scripts]` pointing to `main:main`, **When** `gep --type restapi` runs, **Then** `[project.scripts]` in `pyproject.toml` reads `<package> = "<package>.server:start_server"`.
2. **Given** `gep --type restapi --dry-run` is run, **Then** the output indicates the `pyproject.toml` scripts entry would be updated, but the file is not modified.
3. **Given** a project using any other entry point type (agent, mcp, generic), **When** the corresponding `gep --type <other>` runs, **Then** `[project.scripts]` is **not** changed (only the restapi type triggers this update).

---

### Edge Cases

- What if `pyproject.toml` does not contain a `[project.scripts]` section at all? → The section and entry must be created.
- What if the existing `[project.scripts]` entry already points to `server:start_server`? → No duplicate is written; the file remains unchanged.
- What if `main.py` does not exist when `gep --type restapi` runs (already deleted manually)? → The delete step is silently skipped; command succeeds.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: When `gep --type restapi` executes, the tool MUST delete `src/<package>/main.py` if it exists.
- **FR-002**: When `gep --type restapi` executes, the tool MUST update `[project.scripts]` in `pyproject.toml` so the package CLI entry reads `<package> = "<package>.server:start_server"`, replacing any prior value.
- **FR-003**: The `pyproject_toml.jinja2` template MUST NOT be changed to reference `server:start_server` — the update is applied at runtime by `gep --type restapi`, not at project creation time (project creation still generates `main:main`).
- **FR-004**: When `gep --type restapi --dry-run` is invoked, the tool MUST report the scripts update in its preview output without modifying `pyproject.toml`.
- **FR-005**: `gep` commands for non-restapi types (agent, mcp, generic) MUST NOT modify `[project.scripts]`.
- **FR-006**: If `main.py` is absent when `gep --type restapi` runs, the command MUST complete successfully (silent no-op for the delete step).
- **FR-007**: All other entry-point types continue to overwrite `main.py` as they do today; only the restapi type deletes it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After `gep --type restapi` completes, `src/<package>/main.py` does not exist in 100% of test runs.
- **SC-002**: After `gep --type restapi` completes, `pyproject.toml` contains exactly one `[project.scripts]` entry pointing to `<package>.server:start_server` — verified by test assertion.
- **SC-003**: All existing tests continue to pass (no regressions); the overall test count increases by the number of new tests added for this feature.
- **SC-004**: `gep --type agent`, `gep --type mcp`, and `gep --type generic` each still overwrite `main.py` and leave `[project.scripts]` pointing to `main:main`.
- **SC-005**: `gep --type restapi --dry-run` does not modify any file on disk.

## Assumptions

- The `scaffold ca` command always creates `main.py` when scaffolding a new project; `gep --type restapi` is always run in a project that originally had `main.py`.
- The `pyproject.toml` file always contains a `[project.scripts]` section after `scaffold ca` runs, because that section is included in the current `pyproject_toml.jinja2` template.
- The `server.py` module (thin wrapper calling `start_server()`) is already emitted by `gep --type restapi` as of feature 009; this feature assumes that is complete.
- The `start_server()` function is defined in `server.py` by the time `pyproject.toml` is updated; no further template changes to `server.py.jinja2` are needed.
- Non-restapi entry-point types are out of scope for both the delete and the scripts-update steps.
