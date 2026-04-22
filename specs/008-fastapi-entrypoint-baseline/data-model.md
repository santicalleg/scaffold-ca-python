# Data Model: FastAPI Entry Point Baseline Alignment

**Feature**: 008-fastapi-entrypoint-baseline  
**Date**: 2026-03-31

---

## Entities

### EntryPointType (existing — extended)

Discriminant string passed via `--type`. No model change needed; the `restapi` branch logic changes internally.

```
"restapi" | "mcp" | "agent" | "generic"
```

### CompatibilityViolation (new — runtime-only, no model file)

Detected during `_generate_entry_point_impl` when `--type restapi` is requested.

| Field | Type | Description |
|-------|------|-------------|
| `conflicting_type` | `str` | `"mcp_server"` or `"agent"` |
| `conflicting_path` | `Path` | Absolute path of the conflicting directory |
| `resolution_hint` | `str` | Human-readable message |

Not persisted; raised as a `typer.Exit(code=1)` with Rich output.

### DependencySet (updated constant — no model file)

`_DEP_MAP["restapi"]` in `generate_entry_point.py`:

```python
_DEP_MAP["restapi"] = [
    "fastapi[standard]>=0.135.2",
    "uvicorn[standard]>=0.20",
    "dependency-injector>=4.49.0",
    "pydantic-settings>=2.13.1",
]
```

> **Note**: `fastapi>=0.100` → `fastapi[standard]>=0.135.2` to match ms_test baseline exactly.

### Emitted File Set for `--type restapi` (new)

Files emitted by `_build_operations("restapi", ...)`:

| Template path | Emitted to (relative to `src/<pkg>/`) | Role |
|---|---|---|
| `entry_point/restapi/__init__.py.jinja2` | `infrastructure/entry_points/api/v1/__init__.py` | Package marker |
| `entry_point/restapi/rest_controller.py.jinja2` | `infrastructure/entry_points/api/v1/rest_controller.py` | APIRouter with `/health` |
| `entry_point/restapi/exception_handler.py.jinja2` | `infrastructure/entry_points/api/v1/exception_handler.py` | Exception handlers |
| `entry_point/restapi/schemas.py.jinja2` | `infrastructure/entry_points/api/v1/schemas.py` | Pydantic schemas |
| `entry_point/restapi/server.py.jinja2` | `server.py` (package root) | FastAPI factory + lifespan |
| `entry_point/restapi/test_rest_controller.py.jinja2` | `tests/infrastructure/entry_points/api/v1/test_rest_controller.py` | Health test |

> **Removed from emission** (still on disk for backward compat): `router.py.jinja2`, `health.py.jinja2`, `main.py.jinja2`, `test_router.py.jinja2`. The `entrypoint_main.py.jinja2` continues to overwrite `main.py` as before.

### resource_container.py Template (new file)

Path: `src/scaffold_ca_python/templates/project/application/config/resource_container.py.jinja2`

Emitted by: `generate_project.py` (added to the `_di_cfg` emission loop).

Content: stub `ResourceContainer(containers.DeclarativeContainer)` that loads `settings` from `{{ python_package }}.application.config.config`.

---

## State Transitions

### `gep --type restapi` execution flow (updated)

```
1. Validate --type
2. Check --swagger / --enable-mcp-client guards (unchanged)
3. Validate swagger path (unchanged)
4. find_project_root() → ScaffoldError → exit 1
5. [NEW] Compatibility guard: check mcp_server/ and agent/ dirs → exit 1 if found
6. Duplicate guard: check api/v1/ exists → exit 1 if found
7. Build ctx_dict + operations list (updated file list)
8. Dry-run path: print tree + planned deps → return
9. writer.execute(operations)
10. inject_dependencies(project_root, deps)  ← updated dep list
11. Overwrite main.py via entrypoint_main.py.jinja2 (unchanged)
```

---

## Validation Rules

| Rule | Where enforced |
|------|----------------|
| `--type restapi` blocked when `mcp_server/` exists | `_generate_entry_point_impl` step 5 |
| `--type restapi` blocked when `agent/` exists | `_generate_entry_point_impl` step 5 |
| Duplicate `api/v1/` dir blocked | `_generate_entry_point_impl` step 6 |
| No file overwrite by default | `FileWriter` — `overwrite=False` on `CreateFile` |
| Dry-run emits no files | `writer.execute(dry_run=True)` |
| Compatibility guard runs in dry-run | Guard check precedes dry-run branch |
