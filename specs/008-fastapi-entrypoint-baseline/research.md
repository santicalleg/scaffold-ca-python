# Research: FastAPI Entry Point Baseline Alignment

**Feature**: 008-fastapi-entrypoint-baseline  
**Date**: 2026-03-31

---

## Decision 1: What does `clean-architecture` already produce?

**Context**: FR-001/FR-005 mention generating `Dockerfile`, `mypy.ini`, and `application/config/`. Before deciding whether `gep --type restapi` must re-emit these, we need to know whether they already exist from the initial project scaffold.

**Finding** (from `generate_project.py` inspection):

`scaffold ca --name <Name>` already emits ALL of the following:

| File | Template |
|------|----------|
| `Dockerfile` | `project/dockerfile.jinja2` |
| `mypy.ini` | `project/mypy_ini.jinja2` |
| `application/config/__init__.py` | `project/application/config/__init__.py.jinja2` |
| `application/config/config.py` | `project/application/config/config.py.jinja2` |
| `application/config/container.py` | `project/application/config/container.py.jinja2` |
| `application/config/driven_adapters_container.py` | `project/application/config/driven_adapters_container.py.jinja2` |
| `application/config/usecases_container.py` | `project/application/config/usecases_container.py.jinja2` |

**Decision**: `gep --type restapi` MUST NOT re-emit `Dockerfile`, `mypy.ini`, or any `application/config/` file — the user already has them. This changes FR-001/FR-005 to infrastructure-only scope: only `infrastructure/entry_points/api/v1/` and `server.py` are new file obligations for `gep`.

**Alternatives considered**: Re-emitting all baseline files on every `gep` call — rejected because it would silently overwrite user-modified config files.

---

## Decision 2: `resource_container.py` — missing template

**Context**: ms_test `container.py` references `ResourceContainer` from `resource_container.py`. The current `generate_project.py` emits five `config/` files but the `resource_container.py.jinja2` template is absent from the template set.

**Finding**: `ls src/scaffold_ca_python/templates/project/application/config/` → no `resource_container.py.jinja2`. The ms_test file exists and wires settings into the DI container.

**Decision**: Add `resource_container.py.jinja2` to `src/scaffold_ca_python/templates/project/application/config/` and include it in `generate_project.py`'s emission list. This is a fix that belongs to feature 008 because feature 008 is the first to explicitly require it. Its content is a stub `ResourceContainer` that loads settings via `pydantic-settings`.

**Rationale**: Without `resource_container.py`, the full DI wiring in `container.py` breaks at import time.

---

## Decision 3: `api/v1/` versioned path vs flat `restapi/`

**Context**: Current `gep --type restapi` generates into `infrastructure/entry_points/restapi/`. ms_test uses `infrastructure/entry_points/api/v1/`.

**Decision**: Switch the `restapi` subdir from `"restapi"` to `"api/v1"` (two levels deep). The `_build_operations` function must use `src_dir = project_root / "src" / pkg / "infrastructure" / "entry_points" / "api" / "v1"`.

**Impact on tests**: Existing fixture-based tests assert on `entry_points/restapi/` paths — those tests must be updated to assert on `entry_points/api/v1/`.

**Alternatives considered**: Keeping `restapi/` and adding a symlink — rejected as non-portable and fragile.

---

## Decision 4: `server.py` — scope and conflict with existing `main.py`

**Context**: Current `gep --type restapi` overwrites `main.py` via `entrypoint_main.py.jinja2`. ms_test uses `server.py` (not `main.py`) as the uvicorn launcher. `main.py` in ms_test is the `__main__` dispatch: `import sys; from ms_test.server import main; sys.exit(main())`.

**Decision**: Keep the existing `entrypoint_main.py.jinja2` overwrite behaviour for `main.py` (unchanged). Add a NEW `server.py.jinja2` template that is emitted into the package root (`src/<pkg>/server.py`) alongside the existing `main.py` overwrite. `server.py` contains the `start_server()` factory + lifespan DI wiring. The existing `entrypoint_main.py.jinja2` becomes a thin wrapper that calls `server.main()`.

**Rationale**: ms_test's split between `server.py` (factory) and `server:main` entrypoint is the correct CA pattern. `main.py` is the `[project.scripts]` entry point; `server.py` is where the FastAPI app factory lives.

---

## Decision 5: `exception_handler.py` — new template

**Context**: ms_test has `infrastructure/entry_points/api/v1/exception_handler.py` with three handlers. Current templates do not include this.

**Decision**: Add `exception_handler.py.jinja2` under `src/scaffold_ca_python/templates/entry_point/restapi/`. It is emitted alongside `rest_controller.py` into `infrastructure/entry_points/api/v1/`. It registers handlers for `Exception`, `HTTPException`, and `RequestValidationError`.

**Note**: The template uses no Jinja2 variables (pure Python code), so it can be a near-verbatim copy of the ms_test file with only the `logging` module reference kept generic.

---

## Decision 6: `rest_controller.py` replaces `router.py`

**Context**: ms_test uses `rest_controller.py` (not `router.py`). The controller uses `APIRouter(prefix="/v1")` and a `GET /health` endpoint.

**Decision**: Rename the conceptual role — add `rest_controller.py.jinja2` as the primary emitted file. The existing `router.py.jinja2` template is kept on disk (no breaking change) but is no longer emitted by the `restapi` case in `_build_operations`. The `health.py.jinja2` logic is merged into `rest_controller.py.jinja2` (one router with a `/health` route), removing the separate health.py file from emission as well.

**Alternatives considered**: Keeping `router.py` and renaming at emit time — rejected as confusing; template name should match content.

---

## Decision 7: Compatibility guard — implementation approach

**Context**: The current guard only checks `src_dir.exists()` (duplicate directory). FR-009/FR-010 require failing early if `mcp/` or `agent/` entry point directories already exist when `--type restapi` is requested.

**Decision**: Add a pre-check in `_generate_entry_point_impl` immediately after project root discovery and before the duplicate-directory guard:

```python
for incompatible in ("mcp_server", "agent"):
    conflict_dir = project_root / "src" / pkg / "infrastructure" / "entry_points" / incompatible
    if conflict_dir.exists():
        console.print(f"[red]Error:[/red] Incompatible entry point '{incompatible}' already exists...")
        raise typer.Exit(code=1)
```

The check runs even in `--dry-run` mode.

**Note**: MCP directory is named `mcp_server` (from `subdir = "mcp_server" if type_ == "mcp"`); agent directory is named `agent`. Both are checked.

---

## Decision 8: Dependency map update

**Finding**: `_DEP_MAP["restapi"]` = `["fastapi>=0.100", "uvicorn[standard]>=0.20"]`. ms_test needs two more: `dependency-injector>=4.49.0` and `pydantic-settings>=2.13.1`. Both are already present in `clean-architecture`-generated projects but not guaranteed to be pinned in `pyproject.toml` at the right version. The `inject_dependencies` function is idempotent (skips already-present entries), making it safe to add both.

**Decision**: Update `_DEP_MAP["restapi"]` to include all four dependencies.

---

## Decision 9: Template test coverage

**Requirement**: Principle II requires `tests/templates/` to have tests for every new template.

**Existing file**: `tests/templates/test_entry_point_templates.py` already has restapi tests. New tests needed:
- `rest_controller.py.jinja2` — must contain `APIRouter`, `GET /health`, `async def`
- `exception_handler.py.jinja2` — must contain `HTTPException`, `RequestValidationError`
- `server.py.jinja2` — must contain `FastAPI`, `lifespan`, `Container`, `start_server`
- `test_rest_controller.py.jinja2` — must contain `TestClient`, `GET /v1/health`

**Decision**: Add these four test functions to `tests/templates/test_entry_point_templates.py`.
