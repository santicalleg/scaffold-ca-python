# Quickstart: FastAPI Entry Point for Scaffold CA Projects

**Feature**: 008-fastapi-entrypoint-baseline  
**Audience**: Developer implementing or testing feature 008

---

## Prerequisites

- A project scaffolded with `scaffold ca` (provides `Dockerfile`, `mypy.ini`, `application/config/`)
- Python 3.13, uv

---

## Happy Path — Full Workflow

### 1. Scaffold a clean CA project

```bash
scaffold ca --name OrderService
cd order_service
```

Resulting structure (relevant paths):
```
order_service/
├── pyproject.toml
├── Dockerfile
├── mypy.ini
├── main.py
└── src/
    └── order_service/
        ├── __init__.py
        ├── application/
        │   └── config/
        │       ├── __init__.py
        │       ├── config.py
        │       ├── container.py
        │       ├── driven_adapters_container.py
        │       ├── resource_container.py   ← NEW in this feature
        │       └── usecases_container.py
        └── infrastructure/
            └── entry_points/               ← empty
```

### 2. Generate the FastAPI entry point

```bash
scaffold gep --type restapi
```

After generation:
```
src/order_service/
├── server.py                                     ← NEW (FastAPI factory + lifespan)
└── infrastructure/
    └── entry_points/
        └── api/
            └── v1/
                ├── __init__.py
                ├── rest_controller.py            ← NEW (APIRouter with /health)
                ├── exception_handler.py          ← NEW
                └── schemas.py                    ← NEW
main.py                                           ← overwritten (imports from server.py)
tests/
└── infrastructure/
    └── entry_points/
        └── api/
            └── v1/
                └── test_rest_controller.py       ← NEW
pyproject.toml                                    ← updated with new deps
```

### 3. Install dependencies and run

```bash
uv sync
uv run uvicorn order_service.server:create_app --reload --factory
```

Test the health endpoint:
```bash
curl http://localhost:8000/v1/health
# {"status": "app is online"}
```

---

## Error Flows

### Conflict: project already has an MCP server

If `src/order_service/infrastructure/entry_points/mcp_server/` exists:

```bash
scaffold gep --type restapi
# ERROR: Cannot add 'restapi' entry point.
#        An 'mcp' entry point already exists at:
#        src/order_service/infrastructure/entry_points/mcp_server
#        A project may have only one entry-point type.
# Exit code: 1
```

### Conflict: project already has an agent server

If `src/order_service/infrastructure/entry_points/agent/` exists:

```bash
scaffold gep --type restapi
# ERROR: Cannot add 'restapi' entry point.
#        An 'agent' entry point already exists at:
#        src/order_service/infrastructure/entry_points/agent
#        A project may have only one entry-point type.
# Exit code: 1
```

### Conflict: api/v1/ already exists

```bash
scaffold gep --type restapi
# ERROR: Entry-point directory already exists: .../infrastructure/entry_points/api/v1
# Exit code: 1
```

### Preview only (dry-run)

```bash
scaffold gep --type restapi --dry-run
```

Prints the planned file tree and dependency additions, creates nothing.

---

## Testing

```bash
uv run pytest tests/commands/test_generate_entry_point.py -v
uv run pytest tests/templates/test_entry_point_templates.py -v
```

---

## Notes for Implementors

- `generate_project.py` already emits `Dockerfile`, `mypy.ini`, and the `application/config/` DI stack. **`gep` must not re-emit those.**
- Add `resource_container.py.jinja2` to `templates/project/application/config/` and register it in `generate_project.py`'s emission loop; the template file is missing from the current set.
- The `router.py.jinja2` and `test_router.py.jinja2` templates remain on disk but are **not emitted** by the updated `_build_operations`.
