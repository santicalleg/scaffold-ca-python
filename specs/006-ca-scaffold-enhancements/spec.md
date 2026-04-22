# Feature Specification: Clean Architecture Scaffold Enhancements

**Feature Branch**: `feature/006-ca-scaffold-enhancements`
**Created**: 2026-03-27
**Status**: Draft

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Simplified Project Bootstrapping (Priority: P1)

A developer runs `scaffold ca --name OrderService` and gets a production-ready project skeleton without being prompted for irrelevant metadata. The generated root contains all standard Python project files plus Docker and runtime pinning files out of the box. Ruff configuration lives inside `pyproject.toml` — no separate `.ruff.toml` file.

**Why this priority**: Removing `--package` reduces friction for the most common command. Adding Docker and Python version files means the project is immediately runnable in CI/CD without manual setup. Consolidating ruff config removes a spurious extra file.

**Independent Test**: Running `scaffold ca --name OrderService` on an empty directory produces an `order_service/` tree containing `pyproject.toml`, `README.md`, `.gitignore`, `.dockerignore`, `.python-version`, `Dockerfile`, and the full layer structure. No `.ruff.toml` file is present. Running the command twice exits 1.

**Acceptance Scenarios**:

1. **Given** an empty directory, **When** `scaffold ca --name OrderService` is run, **Then** the project root contains `pyproject.toml`, `README.md`, `.gitignore`, `.dockerignore`, `.python-version`, and `Dockerfile`
2. **Given** a generated project, **When** inspecting `pyproject.toml`, **Then** it contains a `[tool.ruff]` section and no `.ruff.toml` file exists at the project root
3. **Given** a generated project, **When** inspecting `.python-version`, **Then** it contains `3.13`
4. **Given** `scaffold ca --name OrderService` run twice in the same parent directory, **When** the second run executes, **Then** it exits 1 with a message that the directory already exists
5. **Given** the command `scaffold ca --name OrderService --package com.acme`, **When** it is run, **Then** it exits 1 with an "unrecognised option" error

---

### User Story 2 - Dependency Injection Scaffolding (Priority: P2)

A developer runs `scaffold ca --name OrderService` and gets a fully wired dependency injection skeleton in `application/config/` using the `dependency-injector` library, ready to connect driven adapters to use cases without writing boilerplate.

**Why this priority**: A DI container is foundational to any Clean Architecture project. Without it, developers must manually create and connect four boilerplate files before they can start writing business logic.

**Independent Test**: Running `scaffold ca --name OrderService` produces `src/order_service/application/config/` containing `__init__.py`, `config.py`, `driven_adapters_container.py`, `usecases_container.py`, and `container.py`. Each file passes `python -m py_compile`. `pyproject.toml` lists `dependency-injector` and `pydantic-settings` as project dependencies.

**Acceptance Scenarios**:

1. **Given** a newly scaffolded project, **When** inspecting `application/config/config.py`, **Then** it defines a `Settings(BaseSettings)` class with `ENV` and `LOG_LEVEL` string fields and a `settings = Settings()` module-level singleton
2. **Given** a newly scaffolded project, **When** inspecting `application/config/driven_adapters_container.py`, **Then** it defines `DAContainer(containers.DeclarativeContainer)` with a placeholder `providers.Singleton` stub and correct namespace imports using the project's `python_package`
3. **Given** a newly scaffolded project, **When** inspecting `application/config/usecases_container.py`, **Then** it defines `UseCaseContainer(containers.DeclarativeContainer)` with `da_container = providers.DependenciesContainer()` and a placeholder use case `providers.Singleton`
4. **Given** a newly scaffolded project, **When** inspecting `application/config/container.py`, **Then** it defines `Container(containers.DeclarativeContainer)` wiring `DAContainer` and `UseCaseContainer` via `providers.Container`
5. **Given** a newly scaffolded project, **When** inspecting `pyproject.toml`'s `[project.dependencies]`, **Then** it includes both `dependency-injector` and `pydantic-settings`

---

### User Story 3 - Entry-point `main.py` Lifecycle (Priority: P3)

A developer gets a working `main.py` on project creation so that `uv run <pkg>` works immediately. When they later scaffold an entry-point (`scaffold gep`), `main.py` is updated to bootstrap that entry-point automatically.

**Why this priority**: Without `main.py`, the `[project.scripts]` entry in `pyproject.toml` points to a non-existent file, breaking `uv run` immediately after scaffolding.

**Independent Test**: Running `scaffold ca --name OrderService` creates `src/order_service/main.py` with a `main()` function that prints "Hello, World!". The `[project.scripts]` section in `pyproject.toml` contains `order-service = "order_service.main:main"`. Running `scaffold gep --type restapi` replaces `main.py` with a uvicorn startup entrypoint.

**Acceptance Scenarios**:

1. **Given** a newly scaffolded project, **When** inspecting `src/<pkg>/main.py`, **Then** it defines `def main() -> None` that prints "Hello, World!"
2. **Given** a project with default `main.py`, **When** `scaffold gep --type restapi` runs, **Then** `main.py` is updated to start the FastAPI app via `uvicorn.run()`
3. **Given** a project with default `main.py`, **When** `scaffold gep --type agent` runs, **Then** `main.py` is updated to invoke the agent entry-point's run function
4. **Given** a project with default `main.py`, **When** `scaffold gep --type mcp` runs, **Then** `main.py` is updated to start the MCP server
5. **Given** a project with default `main.py`, **When** `scaffold gep --type generic` runs, **Then** `main.py` is updated to call the generic handler's `run()` method
6. **Given** a scaffolded project, **When** inspecting `pyproject.toml`'s `[project.scripts]`, **Then** it contains `<python_package> = "<python_package>.main:main"`

---

### User Story 4 - Auto-inject Dependencies on Adapter/Entry-point Creation (Priority: P4)

A developer runs `scaffold gda --type rest-consumer` or `scaffold gep --type restapi` and the required third-party packages are automatically appended to `[project.dependencies]` in `pyproject.toml`, removing the need to manually look up library names.

**Why this priority**: Without this, developers must manually add packages after every scaffold command — this is repetitive, error-prone, and inconsistent with the "zero friction" promise of the tool.

**Independent Test**: Running `scaffold gep --type restapi` on a scaffolded project adds `fastapi` and `uvicorn[standard]` to `[project.dependencies]` in `pyproject.toml`. Running the same command a second time does not duplicate those entries. Running `scaffold gda --type rest-consumer` adds `httpx`. `--dry-run` prints the packages that would be added without modifying the file.

**Acceptance Scenarios**:

1. **Given** a scaffolded project, **When** `scaffold gep --type restapi` runs, **Then** `pyproject.toml` gains `fastapi` and `uvicorn[standard]` in `[project.dependencies]`
2. **Given** a scaffolded project, **When** `scaffold gep --type agent` runs, **Then** `pyproject.toml` gains `a2a-sdk` in `[project.dependencies]`
3. **Given** a scaffolded project, **When** `scaffold gep --type mcp` runs, **Then** `pyproject.toml` gains `mcp` in `[project.dependencies]`
4. **Given** a scaffolded project, **When** `scaffold gda --type rest-consumer` runs, **Then** `pyproject.toml` gains `httpx` in `[project.dependencies]`
5. **Given** a scaffolded project, **When** `scaffold gda --type secrets` runs, **Then** `pyproject.toml` gains `boto3` in `[project.dependencies]`
6. **Given** `scaffold gep --type restapi --dry-run`, **When** the command runs, **Then** it prints the packages that would be added but does not modify `pyproject.toml`
7. **Given** `fastapi` already present in `[project.dependencies]`, **When** `scaffold gep --type restapi` runs again, **Then** `fastapi` is not duplicated

---

### Edge Cases

- What happens when `--name` starts with a digit? → exits 1 with validation error (existing behaviour preserved).
- What happens when `scaffold gep` is run outside a scaffolded project? → exits 1 with "No scaffold-ca-python project found" (existing behaviour).
- What happens when `main.py` has been manually modified and `scaffold gep` tries to overwrite it? → a warning is printed that `main.py` will be replaced; `--dry-run` shows the new content without writing.
- What happens when `pyproject.toml` is malformed when injecting dependencies? → exits 1 with a clear parse error and a hint to fix the file manually.
- What happens when `application/config/` already exists when running `scaffold ca`? → command exits 1 with a duplicate-directory hint (consistent with existing duplicate-guard pattern across all commands).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The `ca` command MUST NOT accept a `--package` flag; any invocation with `--package` MUST exit 1 with an unrecognised-option error
- **FR-002**: The `ca` command MUST generate a `.python-version` at the project root containing the target Python version (e.g., `3.13`)
- **FR-003**: The `ca` command MUST generate a `Dockerfile` at the project root with a minimal multi-stage Python image stub
- **FR-004**: The `ca` command MUST generate a `.dockerignore` at the project root with standard Python/venv/coverage exclusion patterns
- **FR-005**: The `ca` command MUST embed ruff configuration inside `[tool.ruff]` in `pyproject.toml` and MUST NOT create a separate `.ruff.toml` file
- **FR-006**: The `ca` command MUST create `src/<pkg>/application/config/` containing `__init__.py`, `config.py`, `driven_adapters_container.py`, `usecases_container.py`, and `container.py`
- **FR-007**: `config.py` MUST define a `Settings(BaseSettings)` class with `ENV` and `LOG_LEVEL` string fields and a module-level `settings = Settings()` instance
- **FR-008**: `driven_adapters_container.py` MUST define `DAContainer(containers.DeclarativeContainer)` with placeholder provider stubs and package-namespace imports using the project's `python_package`
- **FR-009**: `usecases_container.py` MUST define `UseCaseContainer(containers.DeclarativeContainer)` with `da_container = providers.DependenciesContainer()` and a placeholder use-case provider
- **FR-010**: `container.py` MUST define `Container(containers.DeclarativeContainer)` wiring `DAContainer` and `UseCaseContainer` via `providers.Container`
- **FR-011**: `pyproject.toml` generated by `ca` MUST list `dependency-injector` and `pydantic-settings` in `[project.dependencies]`
- **FR-012**: The `ca` command MUST create `src/<pkg>/main.py` defining `def main() -> None` that prints "Hello, World!" and register it under `[project.scripts]` as `<python_package> = "<python_package>.main:main"`
- **FR-013**: The `gep` command MUST overwrite `src/<pkg>/main.py` with the entry-point bootstrap appropriate for the selected type (`restapi`, `agent`, `mcp`, `generic`), printing a warning that the file is being replaced
- **FR-014**: The `gep` and `gda` commands MUST append required third-party package names to `[project.dependencies]` in `pyproject.toml` after successful file generation
- **FR-015**: Dependency injection into `pyproject.toml` MUST be idempotent — a package already present in `[project.dependencies]` MUST NOT be added a second time
- **FR-016**: The `--dry-run` flag on `gep` and `gda` MUST print the packages that would be added without modifying `pyproject.toml`. MUST also suppress the main.py overwrite when gep --dry-run is used
- **FR-017**: `mypy.ini` MUST continue to be generated at the project root (no change to existing behaviour)

### Key Entities

- **`ProjectContext`**: Loses the `package` field. All other fields (`name`, `python_package`, `created_at`) are preserved.
- **Dependency map**: A static mapping of `(command, subtype) → list[str]` that drive the package injection logic for `gep` and `gda`.
- **`main.py` template set**: One Jinja2 template per entry-point type (`restapi`, `agent`, `mcp`, `generic`) plus a default "Hello, World!" template used at project creation.
- **DI config templates**: Five Jinja2 templates under `project/application/config/` producing the four Python modules and their `__init__.py`.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `scaffold ca --name X` completes in under 3 seconds and produces at least 22 files (existing count plus the new Docker, DI config, and main.py files)
- **SC-002**: Zero occurrences of `.ruff.toml` in any project created by `scaffold ca`; ruff configuration is always found inside `pyproject.toml`
- **SC-003**: 100% of generated Python files (`config.py`, `container.py`, `main.py`, etc.) pass `python -m py_compile` without syntax errors
- **SC-004**: Manual validation running `uv run <python_package>` on a freshly scaffolded project prints "Hello, World!" without any additional manual setup
- **SC-005**: Running `scaffold gep --type restapi` on a scaffolded project adds `fastapi` and `uvicorn[standard]` exactly once to `pyproject.toml`, with no duplicates on a second run. See FR-015 cross-reference.
- **SC-006**: All existing passing tests continue to pass after these changes (no regression)

---

## Assumptions

- The target Python version embedded in `.python-version` is hardcoded to `3.13` (matching the project's existing tooling) and is not a configurable CLI flag.
- The `Dockerfile` is a minimal multi-stage stub (`python:3.13-slim`) intended as a starting point; developers are expected to customise it for their workloads.
- The agent entry-point dependency is `a2a-sdk`, consistent with the existing agent template.
- The secrets driven adapter injects `boto3` as its default dependency (AWS Secrets Manager is the most common backend in the target ecosystem); developers targeting other providers add their own packages.
- `main.py` is treated as a scaffold-managed file: `scaffold gep` always overwrites it without confirmation, but prints a console warning. Developers who customise `main.py` are responsible for preserving their changes before running `scaffold gep`.
- `pyproject.toml` dependency injection uses `tomllib` for parsing and `tomli-w` for writing, without reformatting unrelated sections.
- The `--package` option is removed entirely (not deprecated); no migration path is required because it was stored metadata only and was never referenced in file generation logic.
