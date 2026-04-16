# Tasks: MCP Entry Point Restructure

**Feature**: `019-mcp-entry-point-restructure`  
**Branch**: `019-mcp-entry-point-restructure`  
**Input**: Design documents from `/specs/019-mcp-entry-point-restructure/`  
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/ ✅

**Tests**: Per constitution Principle V, tests are MANDATORY and written BEFORE implementation (TDD).  
**Organization**: Grouped by user story — each story is independently testable.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no shared state)
- **[US1/US2/US3]**: Which user story the task belongs to
- Exact file paths included in every task

---

## Phase 1: Setup

**Purpose**: Confirm baseline is clean before any changes.

- [X] T001 Record baseline test count: `uv run pytest --ignore=tests/performance -q` and confirm all existing MCP tests pass

---

## Phase 2: Foundational

**Purpose**: Blocking prerequisite — generalize `pyproject_writer.py` and `module_builder.py` to support `scripts_entry_fn`. Needed by all three user stories; must land first.

- [X] T002 Update `src/scaffold_ca_python/core/pyproject_writer.py`: add `entry_fn: str = "start_server"` parameter to `update_project_scripts(project_root, pkg, entry_fn="start_server")` and update function body to use `f"{pkg}.server:{entry_fn}"` instead of hardcoded `"start_server"`
- [X] T003 [P] Update `src/scaffold_ca_python/core/pyproject_writer.py`: add same `entry_fn: str = "start_server"` parameter to `dry_run_scripts_update(project_root, pkg, entry_fn="start_server")` and update comparison logic to use parameterized value
- [X] T004 Update `src/scaffold_ca_python/core/module_builder.py`: in `persist()`, read `entry_fn: str = self._params.get("scripts_entry_fn", "start_server")` and pass it as kwarg to both `update_project_scripts(...)` and `dry_run_scripts_update(...)` calls
- [X] T005 [P] Add tests to `tests/core/test_pyproject_writer.py` (create file if absent): `test_update_project_scripts_default_uses_start_server` confirms existing behaviour unchanged; `test_update_project_scripts_custom_entry_fn_writes_main` confirms `update_project_scripts(..., entry_fn="main")` writes `<pkg>.server:main`; same pair for `dry_run_scripts_update`

**Checkpoint**: Foundational done — `pyproject_writer` is backward-compatible and supports custom `entry_fn`. All existing tests still pass.

---

## Phase 3: User Story 1 — MCP primitives as separate files (Priority: P1) 🎯 MVP

**Goal**: `scaffold gep --type mcp` generates `tools.py` (always), and optionally `resources.py` and `prompts.py`, with new `--with-resources`/`--with-prompts` CLI flags. Old monolithic `mcp_server/server.py` no longer generated.

**Independent Test**: `scaffold gep --type mcp` in a valid project creates `infrastructure/entry_points/mcp_server/tools.py` containing `bind_tools` and `@inject`. No file named `server.py` exists inside `mcp_server/`.

### Tests for User Story 1 *(write FIRST — must FAIL before implementation)*

- [X] T006 [US1] Update `tests/templates/test_entry_point_templates.py`: replace `test_mcp_server_has_list_tools` and `test_mcp_server_has_async_def` (reference old `mcp/server.py.jinja2`) with `test_mcp_tools_has_bind_tools` and `test_mcp_tools_has_inject_decorator` — render `entry_point/mcp/tools.py.jinja2` and assert `"bind_tools"` and `"@inject"` present
- [X] T007 [P] [US1] Add to `tests/templates/test_entry_point_templates.py`: `test_mcp_resources_has_bind_resources` — render `entry_point/mcp/resources.py.jinja2` assert `"bind_resources"` and `"@inject"` present; `test_mcp_prompts_has_bind_prompts` — render `entry_point/mcp/prompts.py.jinja2` assert `"bind_prompts"` and `"@inject"` present
- [X] T008 [P] [US1] Update `tests/factory/entry_points/test_ep_mcp.py`: update `test_mcp_files_queued_in_dry_run` to assert `tools.py` present and `server.py` (inside `mcp_server/`) absent in preview; add `test_mcp_with_resources_queues_resources_file` — set `builder.add_param("with_resources", True)` assert `resources.py` in preview; add `test_mcp_with_prompts_queues_prompts_file` — same pattern for `prompts.py`
- [X] T009 [P] [US1] Add to `tests/commands/test_generate_entry_point.py`: `test_mcp_creates_tools_py` — invoke `["gep", "--type", "mcp"]` assert `mcp_server/tools.py` exists; `test_mcp_with_resources_creates_resources_py` — invoke with `["gep", "--type", "mcp", "--with-resources"]` assert `resources.py` exists; `test_mcp_with_prompts_creates_prompts_py` — assert `prompts.py` exists; `test_mcp_flags_rejected_for_other_types` — invoke `["gep", "--type", "restapi", "--with-resources"]` assert exit_code==1 and `"only valid with --type mcp"` in output

### Pre-implementation: Delete stale templates that existing tests now reference as absent

- [X] T010 [US1] Delete `src/scaffold_ca_python/templates/entry_point/mcp/server.py.jinja2` (old monolithic MCP impl containing `list_tools`/`call_tool`)
- [X] T011 [P] [US1] Delete `src/scaffold_ca_python/templates/entry_point/mcp/entrypoint_main.py.jinja2` (old asyncio entrypoint superseded by new server.py template)
- [X] T012 [P] [US1] Delete `src/scaffold_ca_python/templates/entry_point/mcp/test_server.py.jinja2` (superseded by `test_tools.py.jinja2`)

### Implementation for User Story 1

- [X] T013 [US1] Create `src/scaffold_ca_python/templates/entry_point/mcp/tools.py.jinja2` — async `bind_tools(mcp: FastMCP, ...) -> None` decorated with `@inject`; imports: `from dependency_injector.wiring import inject, Provide`, `from mcp.server.fastmcp import FastMCP`, `from {{ python_package }}.application.config.container import Container`; inner `@mcp.tool("example_tool")` async stub with docstring placeholder
- [X] T014 [P] [US1] Create `src/scaffold_ca_python/templates/entry_point/mcp/resources.py.jinja2` — async `bind_resources(mcp: FastMCP, ...) -> None` with `@inject`; inner `@mcp.resource("file://example_resource", mime_type="application/json")` stub returning `dict`
- [X] T015 [P] [US1] Create `src/scaffold_ca_python/templates/entry_point/mcp/prompts.py.jinja2` — `def bind_prompts(mcp: FastMCP, ...) -> None` with `@inject`; inner `@mcp.prompt()` async stub
- [X] T016 [P] [US1] Create `src/scaffold_ca_python/templates/entry_point/mcp/test_tools.py.jinja2` — test stub: imports `bind_tools` from `{{ python_package }}.infrastructure.entry_points.mcp_server.tools`; `test_bind_tools_is_async_callable` asserts `asyncio.iscoroutinefunction(bind_tools.__wrapped__ if hasattr(bind_tools, "__wrapped__") else bind_tools)`
- [X] T017 [P] [US1] Create `src/scaffold_ca_python/templates/entry_point/mcp/test_resources.py.jinja2` — same pattern: imports `bind_resources`, asserts it is async callable
- [X] T018 [P] [US1] Create `src/scaffold_ca_python/templates/entry_point/mcp/test_prompts.py.jinja2` — imports `bind_prompts`, asserts it is callable (sync, not async)
- [X] T019 [US1] Rewrite `src/scaffold_ca_python/factory/entry_points/ep_mcp.py` `build()` method: read `with_resources = builder.get_param("with_resources", False)` and `with_prompts = builder.get_param("with_prompts", False)`; always queue `__init__.py`, `tools.py`, `test_tools.py`; conditionally queue `resources.py`+`test_resources.py` and `prompts.py`+`test_prompts.py`; set `builder.add_param("scripts_entry_fn", "main")`; add deps: `mcp>=1.0`, `uvicorn[standard]>=0.20`, `starlette>=0.40`, `dependency-injector>=4.49.0`, `pydantic-settings>=2.13.1`
- [X] T020 [P] [US1] Update `src/scaffold_ca_python/commands/generate_entry_point.py`: add `with_resources: Annotated[bool, typer.Option("--with-resources/--no-with-resources", help="Generate resources.py (mcp only).")] = False` and same pattern for `with_prompts`; add guard after type validation: `if (with_resources or with_prompts) and type_ != "mcp": console.print(...) raise typer.Exit(code=1)`; add `builder.add_param("with_resources", with_resources)` and `builder.add_param("with_prompts", with_prompts)` before `factory.build(builder)`

**Checkpoint**: US1 fully functional — `scaffold gep --type mcp` creates `tools.py`; `--with-resources` adds `resources.py`; `--with-prompts` adds `prompts.py`. T006–T009 pass.

---

## Phase 4: User Story 2 — Replace main.py with server.py entrypoint (Priority: P2)

**Goal**: `scaffold gep --type mcp` generates `src/<pkg>/server.py` (uvicorn + `app.start_server()`), deletes `main.py`, and updates `pyproject.toml` `[project.scripts]` to `<pkg>.server:main`.

**Independent Test**: After `scaffold gep --type mcp`, `src/<pkg>/server.py` exists and contains `uvicorn.run(app.start_server(), ...)`. `main.py` is absent. `pyproject.toml` scripts entry is `<pkg>.server:main`.

### Tests for User Story 2 *(write FIRST)*

- [X] T021 [US2] Add to `tests/templates/test_entry_point_templates.py`: `test_mcp_server_has_main_function` — render `entry_point/mcp/server.py.jinja2` assert `"def main"` present; `test_mcp_server_has_uvicorn_run` — assert `"uvicorn.run"` present; `test_mcp_server_imports_app` — assert `"from"` and `"import app"` present
- [X] T022 [P] [US2] Update `tests/factory/entry_points/test_ep_mcp.py`: update `test_mcp_main_py_overwritten` to assert `server.py` at `src/<pkg>/server.py` (package root, not inside `mcp_server/`) is in queued paths; add `test_mcp_scripts_entry_fn_param_is_main` — after `factory.build(builder)`, assert `builder.get_param("scripts_entry_fn") == "main"`
- [X] T023 [P] [US2] Add to `tests/commands/test_generate_entry_point.py`: `test_mcp_creates_server_py_at_package_root` — after live run assert `src/<pkg>/server.py` exists; `test_mcp_deletes_main_py` — create `main.py` before run, assert absent after; `test_mcp_updates_pyproject_scripts_to_server_main` — read pyproject.toml after live run assert `"server:main"` in scripts value

### Implementation for User Story 2

- [X] T024 [US2] Create `src/scaffold_ca_python/templates/entry_point/mcp/server.py.jinja2` (new uvicorn entrypoint) — content: `import sys`, `import uvicorn`, blank line, `from {{ python_package }}.application.config.config import settings`, `from {{ python_package }}.application import app`, blank line, `def main() -> None:`, `    uvicorn.run(app.start_server(), host=settings.HOST, port=settings.PORT)`, blank line, `if __name__ == "__main__":`, `    sys.exit(main())`
- [X] T025 [US2] Update `src/scaffold_ca_python/factory/entry_points/ep_mcp.py` — add after tools/resources/prompts file adds: `server_path = project_root / "src" / pkg / "server.py"`, `main_py = project_root / "src" / pkg / "main.py"`, `builder.add_file(server_path, builder.render(f"{base}/server.py.jinja2", ctx_dict), template_name=..., overwrite=True)`, `builder.delete_file(main_py)`, `builder.add_param("scripts_entry", True)` (note: `scripts_entry_fn = "main"` already set in T019)

**Checkpoint**: US2 done — `main.py` deleted, `server.py` created at package root, pyproject scripts updated to `<pkg>.server:main`.

---

## Phase 5: User Story 3 — Generate app.py composition root (Priority: P3)

**Goal**: `scaffold gep --type mcp` generates `src/<pkg>/application/app.py` with `FastMCP` instance, async `lifespan`, and `start_server() -> Starlette`. Jinja2 `{% if %}` blocks include `bind_resources`/`bind_prompts` only when the corresponding flags were used.

**Independent Test**: After `scaffold gep --type mcp`, `src/<pkg>/application/app.py` contains `FastMCP`, `lifespan`, `start_server`, `streamable_http_app`. After `--with-resources`, also contains `bind_resources`.

### Tests for User Story 3 *(write FIRST)*

- [X] T026 [US3] Add to `tests/templates/test_entry_point_templates.py` — render `entry_point/mcp/app.py.jinja2` with context `{**_ctx().model_dump(), "with_resources": False, "with_prompts": False}`: `test_mcp_app_has_fastmcp_instance` assert `"FastMCP"` present; `test_mcp_app_has_start_server` assert `"start_server"` present; `test_mcp_app_has_lifespan` assert `"lifespan"` and `"asynccontextmanager"` present; `test_mcp_app_has_streamable_http_app` assert `"streamable_http_app"` present
- [X] T027 [P] [US3] Add to `tests/templates/test_entry_point_templates.py`: `test_mcp_app_with_resources_includes_bind_resources` — render with `with_resources=True` assert `"bind_resources"` present; `test_mcp_app_without_resources_excludes_bind_resources` — render with `with_resources=False` assert `"bind_resources"` NOT in output; `test_mcp_app_with_prompts_includes_bind_prompts` / `test_mcp_app_without_prompts_excludes_bind_prompts` — same pair for prompts
- [X] T028 [P] [US3] Update `tests/factory/entry_points/test_ep_mcp.py`: `test_mcp_queues_app_py` — after dry-run factory build, assert `application/app.py` path is in preview; `test_mcp_app_py_not_overwritten` — write a sentinel `app.py` before build, run non-dry, assert sentinel content still present (no-overwrite guard)
- [X] T029 [P] [US3] Add to `tests/commands/test_generate_entry_point.py`: `test_mcp_creates_app_py` — after live `gep --type mcp` assert `application/app.py` exists; `test_mcp_app_py_with_resources_contains_bind_resources` — after live run with `--with-resources` read `app.py` assert `"bind_resources"` in content

### Implementation for User Story 3

- [X] T030 [US3] Create `src/scaffold_ca_python/templates/entry_point/mcp/app.py.jinja2` — full content per data-model.md: `FastMCP("{{ project.name }}", stateless_http=True)` module-level instance; async `lifespan(_app: Starlette)` context manager with `container = Container()`, `container.wire(modules=[tools{% if with_resources %}, resources{% endif %}{% if with_prompts %}, prompts{% endif %}])`, `await tools.bind_tools(mcp)`, `{% if with_resources %}await resources.bind_resources(mcp){% endif %}`, `{% if with_prompts %}bind_prompts(mcp){% endif %}`, `await container.resource_container.init_resources()`, `async with mcp.session_manager.run(): yield`, `await container.resource_container.shutdown_resources()`; `def start_server() -> Starlette:` returning `Starlette(routes=[Mount("/", app=mcp.streamable_http_app())], lifespan=lifespan)`; commented-out `TransportSecuritySettings` and `AuthContextMiddleware` examples
- [X] T031 [US3] Update `src/scaffold_ca_python/factory/entry_points/ep_mcp.py`: add `app_py_path = project_root / "src" / pkg / "application" / "app.py"`; build enriched context `app_ctx = {**ctx_dict, "with_resources": with_resources, "with_prompts": with_prompts}`; add `builder.add_file(app_py_path, builder.render(f"{base}/app.py.jinja2", app_ctx), template_name=f"{base}/app.py.jinja2")` (no `overwrite=True` — use no-overwrite default)

**Checkpoint**: US3 done — `app.py` generated with full composition root; conditional sections correct for all flag combinations.

---

## Phase 6: Polish & Quality Gates

- [X] T032 [P] Run `uv run ruff check src/ tests/` — fix any new violations introduced by T013–T031 (0 new violations expected)
- [X] T033 [P] Run `uv run mypy src/` — fix any new strict-mode errors introduced by T013–T031
- [X] T034 Run `uv run pytest --ignore=tests/performance -q` — confirm all previously passing tests still pass, all T005–T029 new tests pass, coverage ≥ 80%
- [X] T035 [P] Manual dry-run validation: `scaffold gep --type mcp --dry-run` in a temp project — confirm tree lists `application/app.py`, `mcp_server/tools.py`, `server.py`; dependency and scripts preview lines present; exit code 0; no files written

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1. T002–T004 must complete before US stories (T019/T025/T031 call `pyproject_writer` and `module_builder`)
- **Phase 3 (US1)**: Depends on Phase 2. TDD order within: T006–T009 (tests) → T010–T012 (delete stale) → T013–T020 (impl)
- **Phase 4 (US2)**: Depends on Phase 3 (`ep_mcp.py` partially rewritten in T019; T025 extends it)
- **Phase 5 (US3)**: Depends on Phase 4 (`app.py` imports `tools`/`resources`/`prompts` created in US1; calls `server.py`'s `main()` approach from US2)
- **Phase 6 (Quality Gates)**: Depends on all implementation tasks complete

### Parallel Opportunities Per Story

**Foundational**: T002 and T003 parallel (two separate functions). T004 depends on T002+T003. T005 parallel with T002–T004.  
**US1 tests**: T006, T007, T008, T009 all parallel (different test files).  
**US1 impl**: T010, T011, T012 parallel (delete 3 separate files). T013–T018 all parallel (6 separate new template files). T019 and T020 parallel (different source files).  
**US2**: T021, T022, T023 parallel. T024 parallel with T025 (T025 edits same file as T019 — apply sequentially).  
**US3**: T026, T027, T028, T029 all parallel. T030 and T031 parallel (T031 edits same file as T019+T025 — apply sequentially).  
**Quality gates**: T032 and T033 parallel.

---

## Implementation Strategy

**MVP scope**: Phase 3 (US1) alone is shippable — `gep --type mcp` produces `tools.py` instead of the old monolithic `server.py`. Project structure is correct even before `app.py` and new `server.py` entrypoint are added.

**Incremental delivery**:
1. Phase 2 → backward-compatible `pyproject_writer` generalization (safe to merge alone)
2. Phase 3 → MVP: new primitive files, new CLI flags, old templates removed
3. Phase 4 → New `server.py` entrypoint + pyproject scripts update
4. Phase 5 → `app.py` composition root
5. Phase 6 → All quality gates green

**Total tasks**: 35  
**Tasks per user story**: US1=15, US2=5, US3=6, Foundational=4, Setup+Quality=5  
**Parallel opportunities**: 22 tasks marked `[P]`
