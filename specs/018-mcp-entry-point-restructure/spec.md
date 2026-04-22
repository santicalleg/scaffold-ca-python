# Feature Specification: MCP Entry Point Restructure

**Feature Branch**: `019-mcp-entry-point-restructure`  
**Created**: 2026-04-16  
**Status**: Draft  
**Input**: User description: "Restructure MCP Entry Point — split server.py into tools/resources/prompts primitives, add app.py factory, replace main.py with server.py"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Generate MCP primitives as separate files (Priority: P1)

As a developer scaffolding an MCP server project, when I run `scaffold gep --type mcp`, the tool generates MCP server primitives as individual focused files (`tools.py`, and optionally `resources.py` and `prompts.py`) inside the `mcp_server/` folder, instead of a single monolithic `server.py`.

**Why this priority**: This is the core structural change. The current `server.py` bundles all MCP concerns into one file; splitting them enables independent development and testing of tools, resources, and prompts. All other stories depend on this structure.

**Independent Test**: Running `scaffold gep --type mcp` produces `infrastructure/entry_points/mcp_server/tools.py` with a `bind_tools(mcp)` async function stub, and no monolithic `server.py` inside `mcp_server/`.

**Acceptance Scenarios**:

1. **Given** a valid scaffold project, **When** `scaffold gep --type mcp` is run, **Then** `infrastructure/entry_points/mcp_server/tools.py` is created with an async `bind_tools(mcp: FastMCP)` stub decorated with `@inject`.
2. **Given** `scaffold gep --type mcp` without extra flags, **Then** no `resources.py` or `prompts.py` are created inside `mcp_server/`.
3. **Given** `scaffold gep --type mcp --with-resources`, **Then** `infrastructure/entry_points/mcp_server/resources.py` is created with an async `bind_resources(mcp: FastMCP)` stub.
4. **Given** `scaffold gep --type mcp --with-prompts`, **Then** `infrastructure/entry_points/mcp_server/prompts.py` is created with a `bind_prompts(mcp: FastMCP)` stub.
5. **Given** `scaffold gep --type mcp --with-resources --with-prompts`, **Then** all three primitive files are generated.
6. **Given** an existing `mcp_server/` directory, **When** `scaffold gep --type mcp` is run again, **Then** command exits with code 1 and prints a hint about the existing directory.

---

### User Story 2 — Replace main.py with server.py as the application entrypoint (Priority: P2)

As a developer, when `scaffold gep --type mcp` is run, `main.py` at the package root is replaced by `server.py` which starts the Starlette application with uvicorn.

**Why this priority**: The existing `entrypoint_main.py` template calls `asyncio.run(run())` — incompatible with the FastMCP + Starlette HTTP transport. The new `server.py` entrypoint must be consistent with the `app.py` factory.

**Independent Test**: After running `scaffold gep --type mcp`, `src/<pkg>/server.py` exists with a `main()` function calling `uvicorn.run(app.start_server(), ...)`, and `pyproject.toml` scripts entry points to `<pkg>.server:main`.

**Acceptance Scenarios**:

1. **Given** a valid scaffold project with `main.py`, **When** `scaffold gep --type mcp` is run, **Then** `main.py` is deleted and `server.py` is created with `uvicorn.run(app.start_server(), host=settings.HOST, port=settings.PORT)`.
2. **Given** `scaffold gep --type mcp` runs successfully, **Then** `pyproject.toml` `[project.scripts]` points to `<pkg>.server:main`.
3. **Given** `scaffold gep --type mcp --dry-run`, **Then** output indicates `main.py` would be replaced by `server.py` and `pyproject.toml` would be updated, without writing files.

---

### User Story 3 — Generate app.py application factory in the application package (Priority: P3)

As a developer, when `scaffold gep --type mcp` is run, `src/<pkg>/application/app.py` is generated with a `start_server()` factory function that wires DI, binds MCP primitives, and returns a Starlette application.

**Why this priority**: `app.py` is the composition root connecting DI container, primitive files, and the HTTP transport. Without it, `server.py` has nothing to call.

**Independent Test**: After `scaffold gep --type mcp`, `src/<pkg>/application/app.py` exists with a `FastMCP` instance, an async `lifespan` context manager, and a `start_server() -> Starlette` function.

**Acceptance Scenarios**:

1. **Given** `scaffold gep --type mcp`, **Then** `src/<pkg>/application/app.py` is created with a `FastMCP` instance, `lifespan` async context manager wiring the DI `Container`, and `start_server()` returning a `Starlette` app with `mcp.streamable_http_app()` mounted.
2. **Given** `--with-resources` was used, **Then** `app.py` includes `await resources.bind_resources(mcp)` inside `lifespan`.
3. **Given** `--with-prompts` was used, **Then** `app.py` includes a `bind_prompts(mcp)` call in `lifespan` or `start_server`.
4. **Given** `scaffold gep --type mcp --dry-run`, **Then** `application/app.py` appears in the preview file list.

---

### Edge Cases

- If `application/app.py` already exists, it is not overwritten (standard no-overwrite guard applies).
- If `main.py` does not exist when `gep --type mcp` runs, `server.py` generation still succeeds.
- `--with-resources` or `--with-prompts` combined with any type other than `mcp` exits with code 1 and an error message.
- `--dry-run` with `--with-resources --with-prompts` shows all would-be-created files including optional primitives.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `scaffold gep --type mcp` MUST generate `infrastructure/entry_points/mcp_server/tools.py` with an async `bind_tools(mcp: FastMCP)` stub decorated with `@inject`.
- **FR-002**: `scaffold gep --type mcp --with-resources` MUST additionally generate `infrastructure/entry_points/mcp_server/resources.py` with an async `bind_resources(mcp: FastMCP)` stub.
- **FR-003**: `scaffold gep --type mcp --with-prompts` MUST additionally generate `infrastructure/entry_points/mcp_server/prompts.py` with a `bind_prompts(mcp: FastMCP)` stub.
- **FR-004**: The existing monolithic `mcp_server/server.py` template MUST be replaced by the primitive files; `server.py` inside `mcp_server/` must no longer be generated.
- **FR-005**: `scaffold gep --type mcp` MUST generate `src/<pkg>/application/app.py` with a `FastMCP` instance, async `lifespan` context manager, and `start_server() -> Starlette` factory function.
- **FR-006**: `app.py` MUST wire the DI `Container` and call `await tools.bind_tools(mcp)` inside `lifespan`, mounting `mcp.streamable_http_app()` via `starlette.routing.Mount`.
- **FR-007**: When `--with-resources` is used, `app.py` MUST include `await resources.bind_resources(mcp)` inside `lifespan`.
- **FR-008**: When `--with-prompts` is used, `app.py` MUST include a `bind_prompts(mcp)` call.
- **FR-009**: `scaffold gep --type mcp` MUST generate `src/<pkg>/server.py` (replacing `main.py`) with a `main()` function calling `uvicorn.run(app.start_server(), host=settings.HOST, port=settings.PORT)`.
- **FR-010**: `scaffold gep --type mcp` MUST update `pyproject.toml` `[project.scripts]` to point to `<pkg>.server:main`.
- **FR-011**: `scaffold gep --type mcp --dry-run` MUST preview all file creations and the `pyproject.toml` script change without writing.
- **FR-012**: `--with-resources` and `--with-prompts` flags MUST only be valid with `--type mcp`; any other type MUST exit code 1 with an informative error.
- **FR-013**: `mcp>=1.0`, `uvicorn`, and `starlette` MUST be added to `[project.dependencies]` when running (non-dry-run) `scaffold gep --type mcp`.
- **FR-014**: Test stubs MUST be generated for `tools.py` always, and for `resources.py`/`prompts.py` when the corresponding flags are used.

### Key Entities

- **MCP Primitive File**: A generated Python module (`tools.py`, `resources.py`, or `prompts.py`) binding one category of MCP capabilities via a top-level `bind_*` function using `@inject`.
- **app.py Factory**: Composition root at `src/<pkg>/application/app.py` wiring DI, binding primitives, and exposing `start_server() -> Starlette`.
- **server.py Entrypoint**: Package-root module `src/<pkg>/server.py` starting the HTTP server with `uvicorn`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: After `scaffold gep --type mcp`, a developer can implement their first MCP tool by editing only `tools.py` without touching any other generated file.
- **SC-002**: `scaffold gep --type mcp --with-resources --with-prompts` generates all five new files (`tools.py`, `resources.py`, `prompts.py`, `app.py`, `server.py`) plus test stubs in a single command.
- **SC-003**: All existing tests for `gep --type mcp` continue to pass after the restructure with zero regressions.
- **SC-004**: The generated project has no cross-file import errors between `app.py`, `server.py`, and the primitive files.
- **SC-005**: `scaffold gep --type mcp --dry-run` output matches the set of files actually created on a live run.

## Assumptions

- `dependency-injector` is already in the default project `pyproject.toml` (it is included by the scaffold's project template).
- `settings.HOST` and `settings.PORT` are expected by convention in the generated `config.py`; the template uses these names as placeholders.
- `TransportSecuritySettings` and `AuthContextMiddleware` from the user's example are optional developer customisations — the generated `app.py` includes them as commented-out examples.
- `mcp_server/` remains the folder name for the entry-point directory.
- The `entrypoint_main.py.jinja2` template is removed and superseded by the new `server.py` project-root template.
- Each `bind_*` stub imports only from `mcp.server.fastmcp` and `dependency_injector.wiring`; domain-specific imports are shown as comments/placeholders.
- The `routes.py` file shown in the user's example (`routes.bind_routes(mcp)`) is out of scope for this feature — it belongs to a separate routing concern.
