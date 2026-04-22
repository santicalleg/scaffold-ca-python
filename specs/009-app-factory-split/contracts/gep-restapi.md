# Contract: `gep --type restapi` — Updated Output (Feature 009)

**Command**: `scaffold gep --type restapi`  
**Feature**: 009 — App Factory Split  
**Amends**: `specs/004-scaffold-ca-python-cli/contracts/gep.md` (restapi section only)

---

## Purpose

Documents the updated file output contract for `scaffold gep --type restapi` after the
app-factory split. The application factory (`create_app`, `lifespan`) moves from `server.py`
to `application/app.py`. `server.py` becomes a thin process entry point. `main.py` is no
longer emitted.

---

## Updated Output Tree

```
src/<project>/
├── application/
│   └── app.py                  ← NEW: factory + lifespan + start_server()
├── server.py                   ← UPDATED: thin wrapper (5 lines max)
└── infrastructure/
    └── entry_points/
        └── api/
            └── v1/
                ├── __init__.py
                ├── rest_controller.py
                ├── exception_handler.py
                └── schemas.py

tests/
├── application/
│   └── test_app.py             ← NEW: factory + lifespan tests
└── infrastructure/
    └── entry_points/
        └── api/
            └── v1/
                ├── test_rest_controller.py   (unchanged from feature 008)
                ├── test_server.py            ← NEW
                ├── test_exception_handler.py ← NEW
                └── test_schemas.py           ← NEW
```

**Not emitted** (removed from feature 008):
- `main.py` — no longer generated for `restapi` type

---

## `application/app.py` Contract

```python
# src/<project>/application/app.py

"""FastAPI application factory for <project>."""
from __future__ import annotations
# ... imports ...

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Wire DI container on startup; unwire on shutdown."""
    ...

def create_app() -> FastAPI:
    """Create and return a fully configured FastAPI application."""
    ...

def start_server() -> None:
    """Launch uvicorn in factory mode. Called from server.py."""
    uvicorn.run(
        "<pkg>.application.app:create_app",  # <-- updated path
        factory=True,
        ...
    )
```

**Invariants**:
- Importing `app.py` must not start a server (no module-level side-effects)
- `create_app()` must register: router, `http_exception_handler`, `validation_exception_handler`, `generic_exception_handler`
- `lifespan` must wire `<pkg>.infrastructure.entry_points.api.v1.rest_controller`
- `start_server()` factory path must reference `<pkg>.application.app:create_app`

---

## `server.py` Contract

```python
# src/<project>/server.py

"""Process entry point for <project>."""
from <pkg>.application.app import start_server

if __name__ == "__main__":
    start_server()
```

**Invariants**:
- ≤ 5 non-blank, non-comment lines
- No `uvicorn` import
- No `FastAPI` import
- No `Settings` or `Container` instantiation

---

## `--dry-run` Output Contract

Running `scaffold gep --type restapi --dry-run` MUST list all files including the new
`application/app.py` and all new test files, and write nothing to disk:

```
restapi (dry run)
├── src/<pkg>/application/app.py
├── src/<pkg>/server.py
├── src/<pkg>/infrastructure/entry_points/api/v1/__init__.py
├── src/<pkg>/infrastructure/entry_points/api/v1/rest_controller.py
├── src/<pkg>/infrastructure/entry_points/api/v1/exception_handler.py
├── src/<pkg>/infrastructure/entry_points/api/v1/schemas.py
├── tests/application/test_app.py
├── tests/infrastructure/entry_points/api/v1/test_rest_controller.py
├── tests/infrastructure/entry_points/api/v1/test_server.py
├── tests/infrastructure/entry_points/api/v1/test_exception_handler.py
└── tests/infrastructure/entry_points/api/v1/test_schemas.py
```

---

## Unchanged Flags

All flags from the base `gep` contract remain unchanged: `--swagger`, `--enable-kafka`,
`--enable-mcp-client`, `--dry-run`. None of the other `gep` types (`agent`, `mcp`,
`generic`) are affected by this feature.
