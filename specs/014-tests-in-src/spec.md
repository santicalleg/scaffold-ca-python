# Feature Specification: Move Tests to src/ Layout; Add Entrypoint Exclusivity Validation

**Feature Branch**: `014-tests-in-src`
**Created**: 2026-04-13
**Status**: Draft
**Input**: User description: "Move tests folder inside src; add restapi/mcp/agent entrypoint exclusivity validation; update ms_test reference project to match the new layout"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Generated Projects Place Tests Under `src/tests/` (Priority: P1)

A developer runs `scaffold ca --name MyApp` and then any `generate-*` command. The generated project always places test files under `src/tests/` (sibling of the package directory inside `src/`), not at the project root. When the developer runs `pytest`, the test runner discovers tests from `src/tests/` without additional configuration.

**Current state (broken)**: `scaffold ca` creates `tests/` at the project root. All `generate-*` commands (`gep`, `gm`, `guc`, `gda`, `gh`) write test files into `project_root/tests/...`. The `pyproject.toml` template sets `testpaths = ["tests"]`. This inconsistency means the generated project structure does not match the user-visible tree: `ms_test` example shows `tests/` inside `src/`, not at the root.

**Desired layout after this feature**:
```
project_root/
├── pyproject.toml
└── src/
    ├── my_app/         ← package (unchanged)
    │   ├── application/
    │   ├── domain/
    │   ├── infrastructure/
    │   └── server.py
    └── tests/          ← tests folder (new location: inside src/)
        ├── __init__.py
        ├── application/
        ├── domain/
        └── infrastructure/
```

**Why this priority**: The layout the user expects (`src/tests/`) is the reference blueprint from `ms_test`. Any generated project that deviates from this layout confuses developers and breaks `pytest` discovery without manual edits to `pyproject.toml`.

**Independent Test**: Run `scaffold ca --name TestApp`, then `scaffold gep --type restapi`, then inspect the generated `pyproject.toml` and assert `testpaths = ["src/tests"]`. Run `uv run pytest` in the generated project — exit 0 with all tests collected from `src/tests/`.

**Acceptance Scenarios**:

1. **Given** no existing project, **When** `scaffold ca --name MyApp` runs, **Then** `src/tests/__init__.py` is created and `tests/` does NOT appear at the project root.
2. **Given** a scaffolded CA project, **When** `scaffold gep --type restapi` runs, **Then** test files are created under `src/tests/infrastructure/entry_points/api/v1/`, not under `tests/infrastructure/...`.
3. **Given** a scaffolded CA project, **When** any `generate-*` command runs (`gm`, `guc`, `gda`, `gh`), **Then** the generated test file is placed under `src/tests/...`, mirroring the src-layout convention.
4. **Given** the generated `pyproject.toml`, **When** inspected, **Then** it satisfies FR-002 (`testpaths = ["src/tests"]` and ruff per-file-ignores reference `"src/tests/**/*.py"`).
5. **Given** a generated project with tests in `src/tests/`, **When** `uv run pytest` is run, **Then** the suite exits 0 with all generated tests discovered.

---

### User Story 2 — Bidirectional Exclusivity Between Entrypoint Types (Priority: P1)

A developer who has already generated a restapi entry point cannot add an mcp or agent entry point to the same project, and vice versa. The CLI detects the conflict before touching any files and exits with a descriptive error message and a resolution hint.

**Current state (partial)**: `gep --type restapi` already checks for existing `mcp_server/` and `agent/` directories and raises an error. The **reverse check is missing**: `gep --type mcp` or `gep --type agent` does NOT verify whether a restapi entry point already exists.

**Why this priority**: A partially-protected invariant is deceptive. Developers can corrupt their project by running `gep --type agent` after `gep --type restapi`, leaving the project in a mixed entrypoint state.

**Independent Test**: Run `scaffold ca --name ConflictTest && scaffold gep --type restapi && scaffold gep --type mcp`. The second `gep` must exit non-zero with a human-readable error naming the conflicting directory.

**Acceptance Scenarios**:

1. **Given** a project with a restapi entry point, **When** `gep --type mcp` is run, **Then** the command exits non-zero with an error explaining that a restapi entry point already exists and must be removed first.
2. **Given** a project with a restapi entry point, **When** `gep --type agent` is run, **Then** the command exits non-zero with the same class of error.
3. **Given** a project with an mcp entry point, **When** `gep --type restapi` is run, **Then** the command exits non-zero (existing behaviour; must not regress).
4. **Given** a project with an agent entry point, **When** `gep --type restapi` is run, **Then** the command exits non-zero (existing behaviour; must not regress).
5. **Given** a project with no entry points, **When** any `gep --type` is run, **Then** the command proceeds normally.
6. **Given** a project with a restapi entry point, **When** `gep --type generic` is run, **Then** the command proceeds normally — generic is not subject to exclusivity checks.

---

### User Story 3 — ms_test Reference Project Updated to src/tests/ Layout (Priority: P2)

The `ms_test` example project at the repository root is updated to match the new `src/tests/` layout. Its `pyproject.toml` is corrected (wrong coverage source, missing testpaths configuration), and meaningful test stubs are added under `src/tests/` for the existing restapi entry point.

**Why this priority**: `ms_test` is the living reference used to design and validate features. If it does not match the expected layout it misleads future feature development.

**Independent Test**: `cd ms_test && uv run pytest -q` exits 0. `uv run ruff check src/ && uv run mypy src/ms_test/` exit 0.

**Acceptance Scenarios**:

1. **Given** the `ms_test` project, **When** its directory tree is inspected, **Then** `src/tests/__init__.py` exists and there is no `tests/` at the project root.
2. **Given** `ms_test/pyproject.toml`, **When** inspected, **Then** `testpaths = ["src/tests"]`, `[tool.coverage.run] source = ["ms_test"]` (not the current wrong value), and `"src/tests/**/*.py"` in ruff per-file-ignores.
3. **Given** the `ms_test` project, **When** `uv run pytest` is run, **Then** at least one test for the health endpoint in `rest_controller.py` passes.
4. **Given** `ms_test/pyproject.toml`, **When** the dev dependency group is inspected, **Then** `pytest`, `pytest-cov`, and `httpx` are all present.

---

### Edge Cases

- What if a project was scaffolded before this feature (`tests/` still at the project root)? → All `generate-*` commands MUST probe for the layout: check `src/tests/` first; fall back to `tests/` if `src/tests/` is absent and `tests/` exists. (Emit a deprecation hint is deferred — see Assumptions.)
- What if `tests/` exists at both root and `src/tests/`? → `src/tests/` is authoritative; do not write new files to root `tests/`.
- What if `--dry-run` is used with `scaffold ca`? → The planned file list MUST show `src/tests/__init__.py`, not `tests/__init__.py`.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `scaffold ca` MUST create `src/tests/__init__.py` (not `tests/__init__.py` at the project root).
- **FR-002**: The `pyproject.toml.jinja2` template MUST emit `testpaths = ["src/tests"]` and the ruff per-file-ignores MUST reference `"src/tests/**/*.py"`.
- **FR-003**: All `generate-*` commands (`gep`, `gm`, `guc`, `gda`, `gh`) MUST resolve the tests root to `src/tests/` in newly generated projects, and MUST implement the backward-compatibility layout probe described in the edge cases for pre-existing projects.
- **FR-004**: `delete-module` (`dm`) MUST resolve `tests_root` using the same layout probe as FR-003.
- **FR-005**: `gep --type mcp` and `gep --type agent` MUST check for an existing restapi entry point directory (`infrastructure/entry_points/api/`) and exit non-zero with a descriptive error and resolution hint if one is found.
- **FR-006**: All exclusivity error messages MUST name the conflicting directory and provide a resolution hint.
- **FR-007**: `gep --type generic` MUST NOT be subject to exclusivity checks.
- **FR-008**: The `ms_test` example project MUST have `tests/` moved to `src/tests/`, with test stubs covering the health endpoint.
- **FR-009**: `ms_test/pyproject.toml` MUST have `[tool.coverage.run] source = ["ms_test"]`, `testpaths = ["src/tests"]`, and complete dev dependencies (pytest, pytest-cov, httpx).

### Key Entities

- **Layout probe**: A shared utility function (or inline detection) that, given a `project_root: Path`, returns the tests root path — `project_root / "src" / "tests"` if it exists, else `project_root / "tests"`. Used by all `generate-*` and `delete-module` commands for backward compatibility.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running `uv run pytest` in a freshly scaffolded restapi project exits 0 with all tests discovered under `src/tests/`.
- **SC-002**: Running `scaffold gep --type mcp` in a project that already has a restapi entry point exits non-zero within 1 second with a user-readable error message.
- **SC-003**: The CLI's own test suite passes with ≥ 80% coverage and no new failures beyond pre-existing tombstones.
- **SC-004**: The planned file list in `scaffold ca --dry-run` (or equivalent) shows `src/tests/__init__.py` not `tests/__init__.py`.
- **SC-005**: `cd ms_test && uv run pytest -q` exits 0.

## Assumptions

- The backward-compatibility probe (FR-003) is a safety net for externally-created or pre-feature projects. All projects scaffolded after this feature always use `src/tests/`.
- `gep --type generic` is excluded from exclusivity checks because it is a catch-all type with no framework-specific startup conflicts.
- `mcp` and `agent` entry points are not mutually exclusive with each other; only the restapi ↔ (mcp, agent) pairing is prohibited.
- `ms_test` is a first-party reference project inside the scaffold-ca-python repository, safe to modify directly.
- `httpx` is the correct HTTP test client for Starlette `TestClient`-based tests in generated FastAPI projects.
- The `scaffold up` (update-project) command is the migration path for existing projects; updating `tests/` path is out of scope for this feature. Emitting a deprecation hint when the fallback path is taken is also deferred to a future feature.
- Both directions of exclusivity are in scope: the existing `restapi→mcp/agent` check (implemented in feature 012) and the new reverse `mcp/agent→restapi` check (FR-005, this feature). The user-visible description naming only `mcp/agent→restapi` is not exhaustive.
- The `ms_test` layout TARGET is `src/tests/` (US3 AC1). Any reference showing `tests/` at the project root represents the CURRENT wrong state, not the intended outcome of this feature.
