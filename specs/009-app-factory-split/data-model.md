# Data Model: App Factory Split (Feature 009)

**Status**: Complete
**Date**: 2026-04-10

---

## Entities

### 1. `AppFactory` — `application/app.py` (new generated file)

**What it represents**: The composition root for the FastAPI application. Owns factory creation and lifecycle management.

| Attribute / Element | Type | Notes |
|---|---|---|
| `lifespan(app)` | `async` context manager | Wires `Container` on startup, unwires on shutdown |
| `create_app()` | `→ FastAPI` | Instantiates `Settings`, `Container`, `FastAPI`; attaches exception handlers and router |
| `start_server()` | `→ None` | Reads `Settings`, calls `uvicorn.run()` in factory mode pointing at `<pkg>.application.app:create_app` |

**State transitions**: none (stateless factory functions)

**Validation rules**:
- Template context must supply `project.python_package` and `project.name`
- `create_app()` must register at minimum: `router`, `http_exception_handler`, `validation_exception_handler`, `generic_exception_handler`
- `lifespan` must wire the controller module path `<pkg>.infrastructure.entry_points.api.v1.rest_controller`

---

### 2. `ServerEntryPoint` — `server.py` (updated generated file)

**What it represents**: The thin process launch module at the project root. Single responsibility: delegate to `AppFactory.start_server()`.

| Attribute / Element | Type | Notes |
|---|---|---|
| import | static | `from <pkg>.application.app import start_server` |
| guard | `if __name__ == "__main__"` | Calls `start_server()` |

**Constraint**: Must contain ≤ 5 non-blank, non-comment lines. No factory logic, no Settings instantiation, no uvicorn import.

---

### 3. `TestTemplate` — one per generated source file

**What it represents**: A Jinja2 template that renders a `pytest` test file verifying structural correctness of the corresponding source.

| Template file | Generated test path | Key assertions |
|---|---|---|
| `test_app.py.jinja2` | `tests/application/test_app.py` | `create_app()` returns `FastAPI`; router registered; exception handlers registered; lifespan wires container |
| `test_server.py.jinja2` | `tests/infrastructure/entry_points/api/v1/test_server.py` | `start_server` importable from `application.app`; module-level code does not start a server on import |
| `test_exception_handler.py.jinja2` | `tests/infrastructure/entry_points/api/v1/test_exception_handler.py` | Returns JSON responses with correct status codes for `HTTPException`, `RequestValidationError`, `Exception` |
| `test_schemas.py.jinja2` | `tests/infrastructure/entry_points/api/v1/test_schemas.py` | `ErrorResponse` (or equivalent schema) importable and has expected fields |
| `test_rest_controller.py.jinja2` | `tests/infrastructure/entry_points/api/v1/test_rest_controller.py` | `GET /v1/health` → 200 (already exists, no change) |

---

### 4. `EntryPointGenerator` — `generate_entry_point.py` (updated command)

**What it represents**: The scaffold command that orchestrates all `gep --type restapi` file emissions.

| Change | Location | Description |
|---|---|---|
| Add `app.py` emission | `_build_operations` restapi branch | New `CreateFile` for `project_root/src/<pkg>/application/app.py` |
| Add `test_app.py` emission | `_build_operations` restapi branch | New test `CreateFile` for `tests/application/test_app.py` |
| Add 3 new test emissions | `_build_operations` restapi branch | `test_server.py`, `test_exception_handler.py`, `test_schemas.py` in `test_dir` |
| Update `server.py` template | `_build_operations` restapi branch | Points to thin-wrapper template (same filename, updated content) |
| Remove `main.py` overwrite | `_generate_entry_point_impl` | Delete the `"Overwrite main.py"` block (~7 lines at end of function) |
| Update `--dry-run` output | Implicitly via operations list | `app.py` and all test files should appear in dry-run tree |

---

## Relationships

```
EntryPointGenerator
  emits ──► AppFactory            (application/app.py)
  emits ──► ServerEntryPoint       (server.py)
  emits ──► api/v1/__init__.py
  emits ──► api/v1/rest_controller.py
  emits ──► api/v1/exception_handler.py
  emits ──► api/v1/schemas.py
  emits ──► tests/application/test_app.py
  emits ──► tests/.../test_server.py
  emits ──► tests/.../test_rest_controller.py
  emits ──► tests/.../test_exception_handler.py
  emits ──► tests/.../test_schemas.py
  does NOT emit ──► main.py  (removed)

AppFactory (application/app.py)
  imports ◄── Container            (application/config/container.py)
  imports ◄── Settings             (application/config/config.py)
  imports ◄── router               (infrastructure/entry_points/api/v1/rest_controller.py)
  imports ◄── exception handlers   (infrastructure/entry_points/api/v1/exception_handler.py)

ServerEntryPoint (server.py)
  imports ◄── start_server         (application/app.py)
```

---

## No New Domain Data Storage

This feature involves code-generation templates only. There are no new database entities,
persistent state, or data migrations.
