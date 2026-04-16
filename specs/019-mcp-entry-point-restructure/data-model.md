# Data Model: MCP Entry Point Restructure

**Date**: 2026-04-16  
**Feature**: `019-mcp-entry-point-restructure`

---

## Modified Entities

### `EntryPointMcp` (factory)

**File**: `src/scaffold_ca_python/factory/entry_points/ep_mcp.py`

| Attribute | Type | Description |
|-----------|------|-------------|
| (class) | `ModuleFactory` | No new fields — behaviour changes only |

**`build(builder)` params read from builder**:

| Param key | Type | Default | Description |
|-----------|------|---------|-------------|
| `with_resources` | `bool` | `False` | Whether to generate `resources.py` + `test_resources.py` |
| `with_prompts` | `bool` | `False` | Whether to generate `prompts.py` + `test_prompts.py` |

**Files queued** (after restructure):

| Path | Condition | Template |
|------|-----------|----------|
| `src/<pkg>/infrastructure/entry_points/mcp_server/__init__.py` | always | `mcp/__init__.py.jinja2` |
| `src/<pkg>/infrastructure/entry_points/mcp_server/tools.py` | always | `mcp/tools.py.jinja2` |
| `src/<pkg>/infrastructure/entry_points/mcp_server/resources.py` | `with_resources=True` | `mcp/resources.py.jinja2` |
| `src/<pkg>/infrastructure/entry_points/mcp_server/prompts.py` | `with_prompts=True` | `mcp/prompts.py.jinja2` |
| `src/<pkg>/application/app.py` | always | `mcp/app.py.jinja2` |
| `src/<pkg>/server.py` | always (overwrites `main.py`) | `mcp/server.py.jinja2` |
| `tests/.../mcp_server/test_tools.py` | always | `mcp/test_tools.py.jinja2` |
| `tests/.../mcp_server/test_resources.py` | `with_resources=True` | `mcp/test_resources.py.jinja2` |
| `tests/.../mcp_server/test_prompts.py` | `with_prompts=True` | `mcp/test_prompts.py.jinja2` |

**Files deleted**:
- `src/<pkg>/main.py` (via `builder.delete_file`)

**Dependencies injected**:
- `mcp>=1.0`
- `uvicorn[standard]>=0.20`
- `starlette>=0.40`
- `dependency-injector>=4.49.0`
- `pydantic-settings>=2.13.1`

**Builder params set**:
- `scripts_entry = True`
- `scripts_entry_fn = "main"` ← new; causes `persist()` to write `<pkg>.server:main`

---

### `pyproject_writer` functions

**File**: `src/scaffold_ca_python/core/pyproject_writer.py`

#### `update_project_scripts(project_root, pkg, entry_fn="start_server")`

| Parameter | Type | Default | Notes |
|-----------|------|---------|-------|
| `project_root` | `Path` | — | Project root dir containing `pyproject.toml` |
| `pkg` | `str` | — | Python package name |
| `entry_fn` | `str` | `"start_server"` | **NEW** — function name in `server.py` |

Sets `[project.scripts][pkg]` = `"<pkg>.server:<entry_fn>"`. Idempotent. Returns `True` if written.

#### `dry_run_scripts_update(project_root, pkg, entry_fn="start_server")`

Same signature change as above. Returns `True` if change would occur.

---

### `ModuleBuilder.persist()`

**File**: `src/scaffold_ca_python/core/module_builder.py`

Updated `scripts_entry` handling block:
```python
if bool(self._params.get("scripts_entry", False)):
    pkg = self.project_ctx.python_package
    entry_fn: str = self._params.get("scripts_entry_fn", "start_server")
    if self.dry_run:
        dry_run_scripts_update(self.project_root, pkg, entry_fn)
    else:
        update_project_scripts(self.project_root, pkg, entry_fn)
```

---

## New Jinja2 Templates

### `mcp/tools.py.jinja2`

**Context variables**: `python_package`, `project.name` (from `ModuleContext.model_dump()`)

**Key content**:
- Import: `from dependency_injector.wiring import inject, Provide`
- Import: `from mcp.server.fastmcp import FastMCP`
- Import: `from {{ python_package }}.application.config.container import Container`
- Function: `async def bind_tools(mcp: FastMCP, ...) -> None:` decorated with `@inject`
- Inner tool: `@mcp.tool("example_tool")` stub

---

### `mcp/resources.py.jinja2`

**Context variables**: same as tools

**Key content**:
- Function: `async def bind_resources(mcp: FastMCP, ...) -> None:` with `@inject`
- Inner resource: `@mcp.resource("file://example_resource", mime_type="application/json")` stub

---

### `mcp/prompts.py.jinja2`

**Context variables**: same as tools

**Key content**:
- Function: `def bind_prompts(mcp: FastMCP, ...) -> None:` with `@inject`
- Inner prompt: `@mcp.prompt()` stub

---

### `mcp/app.py.jinja2`

**Context variables**: `python_package`, `project.name`, `with_resources: bool`, `with_prompts: bool`

**Key content**:
- `mcp = FastMCP("{{ project.name }}", stateless_http=True)`
- Async `lifespan(_app: Starlette)` context manager:
  - `container = Container()`
  - `container.wire(modules=[tools{% if with_resources %}, resources{% endif %}{% if with_prompts %}, prompts{% endif %}])`
  - `await tools.bind_tools(mcp)`
  - (conditional) `await resources.bind_resources(mcp)`
  - (conditional) `bind_prompts(mcp)`
  - `await container.resource_container.init_resources()`
  - `async with mcp.session_manager.run(): yield`
  - `await container.resource_container.shutdown_resources()`
- `def start_server() -> Starlette:` with `Mount("/", app=mcp.streamable_http_app())`

---

### `mcp/server.py.jinja2`

**Context variables**: `python_package`

**Key content**:
```python
import sys
import uvicorn

from {{ python_package }}.application.config.config import settings
from {{ python_package }}.application import app


def main() -> None:
    uvicorn.run(app.start_server(), host=settings.HOST, port=settings.PORT)


if __name__ == "__main__":
    sys.exit(main())
```

---

### Test stub templates

#### `mcp/test_tools.py.jinja2`
- Asserts `bind_tools` is an async callable
- Imports from `{{ python_package }}.infrastructure.entry_points.mcp_server.tools`

#### `mcp/test_resources.py.jinja2`
- Asserts `bind_resources` is an async callable

#### `mcp/test_prompts.py.jinja2`
- Asserts `bind_prompts` is callable

---

## Deleted Entities

| Entity | File | Reason |
|--------|------|--------|
| `mcp/server.py.jinja2` (old monolithic) | `templates/entry_point/mcp/server.py.jinja2` | Replaced by `tools.py.jinja2` + `app.py.jinja2` |
| `mcp/entrypoint_main.py.jinja2` | `templates/entry_point/mcp/entrypoint_main.py.jinja2` | Replaced by new `mcp/server.py.jinja2` |
| `mcp/test_server.py.jinja2` | `templates/entry_point/mcp/test_server.py.jinja2` | Replaced by `test_tools.py.jinja2` |

---

## Validation Rules

- `with_resources` and `with_prompts` are `bool`; no validation needed beyond the CLI flag guard.
- `entry_fn` in `pyproject_writer` functions must be a non-empty string matching a valid Python identifier; no runtime validation required (controlled by the factory, not user input).
- `app.py` target path (`application/app.py`) uses the standard no-overwrite guard in `ModuleBuilder.add_file`.
