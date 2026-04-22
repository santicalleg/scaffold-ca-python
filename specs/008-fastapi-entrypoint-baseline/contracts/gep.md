# Contract: `scaffold gep --type restapi`

**Feature**: 008-fastapi-entrypoint-baseline  
**Command**: `scaffold gep` / `scaffold generate-entry-point`  
**Scope**: `--type restapi` behav changes only; other types unchanged.

---

## Command Signature

```
scaffold gep --type restapi [OPTIONS]

Options:
  --swagger PATH          Path to OpenAPI/Swagger spec file (optional)
  --enable-kafka          Include Kafka consumer wiring
  --enable-mcp-client     Include MCP async client wiring
  --dry-run               Print plan; create nothing
```

---

## Inputs

| Input | Type | Required | Description |
|-------|------|----------|-------------|
| `--type` | `str` | Yes | `"restapi"` |
| `--swagger` | `Path \| None` | No | OpenAPI spec; must exist if provided |
| `--enable-kafka` | `bool` | No | Default `False` |
| `--enable-mcp-client` | `bool` | No | Default `False` |
| `--dry-run` | `bool` | No | Default `False` |

---

## Pre-conditions

1. A `pyproject.toml` exists at or above the CWD (marks project root).
2. `src/<pkg>/` directory is discoverable via `find_project_root()`.
3. `src/<pkg>/infrastructure/entry_points/mcp_server/` does **not** exist.
4. `src/<pkg>/infrastructure/entry_points/agent/` does **not** exist.
5. `src/<pkg>/infrastructure/entry_points/api/v1/` does **not** exist.

---

## Outputs

### Files created (relative to project root)

| Path | Template used | Overwrite |
|------|--------------|-----------|
| `src/<pkg>/infrastructure/entry_points/api/v1/__init__.py` | `entry_point/restapi/__init__.py.jinja2` | No |
| `src/<pkg>/infrastructure/entry_points/api/v1/rest_controller.py` | `entry_point/restapi/rest_controller.py.jinja2` | No |
| `src/<pkg>/infrastructure/entry_points/api/v1/exception_handler.py` | `entry_point/restapi/exception_handler.py.jinja2` | No |
| `src/<pkg>/infrastructure/entry_points/api/v1/schemas.py` | `entry_point/restapi/schemas.py.jinja2` | No |
| `src/<pkg>/server.py` | `entry_point/restapi/server.py.jinja2` | No |
| `tests/infrastructure/entry_points/api/v1/test_rest_controller.py` | `entry_point/restapi/test_rest_controller.py.jinja2` | No |
| `main.py` | `entry_point/restapi/entrypoint_main.py.jinja2` | **Yes** |

### pyproject.toml mutations

Dependencies injected under `[project.dependencies]`:

```
fastapi[standard]>=0.135.2
uvicorn[standard]>=0.20
dependency-injector>=4.49.0
pydantic-settings>=2.13.1
```

---

## Error Conditions

| Condition | Message (Rich) | Exit code |
|-----------|---------------|-----------|
| Project root not found | `ScaffoldError: pyproject.toml not found` | 1 |
| `mcp_server/` dir exists | `Cannot add 'restapi' entry point. An 'mcp' entry point already exists at: …` | 1 |
| `agent/` dir exists | `Cannot add 'restapi' entry point. An 'agent' entry point already exists at: …` | 1 |
| `api/v1/` dir exists | `Entry-point directory already exists: …` | 1 |
| `--swagger` file missing | `Swagger file not found: …` | 1 |

---

## Dry-Run Behaviour

- Pre-conditions 1–4 are still validated.
- Pre-condition 5 (duplicate dir) is still validated.
- No files are written.
- No pyproject.toml mutations occur.
- Output: Rich tree of planned files + list of planned dependency additions.

---

## Template Rendering Context

All templates receive the standard `ModuleContext`:

| Key | Example |
|-----|---------|
| `python_package` | `order_service` |
| `module_name` | `OrderService` |
| `enable_kafka` | `False` |
| `enable_mcp_client` | `False` |

---

## Contract Stability

This contract governs the `--type restapi` path from feature 008 onward. The `router.py.jinja2` and `test_router.py.jinja2` templates are retained on disk for backward compatibility (existing generated projects) but are not emitted by `gep --type restapi` after this feature.
