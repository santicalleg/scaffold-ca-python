# Research: MCP Entry Point Restructure

**Date**: 2026-04-16  
**Feature**: `019-mcp-entry-point-restructure`

---

## R-001: Conditional file generation pattern (from EntryPointRestApi)

**Decision**: Use `builder.get_param(key, default)` for conditional logic inside `EntryPointMcp.build()`. The factory reads `with_resources` and `with_prompts` boolean params set by `generate_entry_point.py` via `builder.add_param(...)` before calling `factory.build(builder)`.

**Rationale**: This is the established pattern for `enable_kafka` and `enable_mcp_client` in `generate_entry_point.py`. The CLI command sets the params; the factory reads them. No changes to `ModuleBuilder` internals are required.

**Implementation**:
```python
# In generate_entry_point.py (CLI command)
builder.add_param("with_resources", with_resources)
builder.add_param("with_prompts", with_prompts)

# In ep_mcp.py (factory)
with_resources: bool = builder.get_param("with_resources", False)
with_prompts: bool = builder.get_param("with_prompts", False)
if with_resources:
    builder.add_file(src_dir / "resources.py", ...)
```

**Alternatives considered**: Template-level Jinja2 conditionals (`{% if with_resources %}`). Rejected because the conditional is about *which files to create*, not about *content within a file* — factory-level logic is the right layer.

---

## R-002: pyproject.toml scripts update pattern

**Decision**: Generalize `update_project_scripts(project_root, pkg, entry_fn="start_server")` and `dry_run_scripts_update(project_root, pkg, entry_fn="start_server")` to accept an optional `entry_fn` parameter. The MCP factory sets `builder.add_param("scripts_entry", True)` and `builder.add_param("scripts_entry_fn", "main")`. `ModuleBuilder.persist()` reads `scripts_entry_fn` and passes it through.

**Rationale**: The current `update_project_scripts` hardcodes `<pkg>.server:start_server`. The MCP entrypoint uses `main()` (not `start_server()`). Parameterizing preserves backward compatibility for restapi (default `entry_fn="start_server"`) while allowing MCP to use `entry_fn="main"`.

**Files affected**:
- `src/scaffold_ca_python/core/pyproject_writer.py` — add `entry_fn` param to both functions
- `src/scaffold_ca_python/core/module_builder.py` — read `scripts_entry_fn` param in `persist()`

**Alternatives considered**: Separate `update_project_scripts_mcp()` function. Rejected — unnecessary duplication. Using `start_server` as the MCP function name. Rejected — contradicts the user's example and is confusing since `app.py` already exposes `start_server()`.

---

## R-003: app.py template context (conditional imports/calls)

**Decision**: Pass `with_resources: bool` and `with_prompts: bool` into the `app.py.jinja2` render context. The template uses Jinja2 `{% if %}` blocks for the conditional import lines and `bind_*` call sites inside `lifespan`.

**Rationale**: `app.py` is a single file whose *content* varies based on whether resources/prompts are selected. This is content-level variation, which is the correct use case for Jinja2 conditionals (as opposed to file-existence conditionals which live in the factory).

**Template pattern**:
```jinja2
{% if with_resources %}
from {{ python_package }}.infrastructure.entry_points.mcp_server import resources
{% endif %}
```

**Alternatives considered**: Generating separate `app.py` templates for each combination. Rejected — combinatorial explosion (4 variants).

---

## R-004: FastMCP + Starlette HTTP transport API

**Decision**: Use `mcp.server.fastmcp.FastMCP` for the server instance and `mcp.server.transport_security.TransportSecuritySettings` for optional security. The Starlette app mounts `mcp.streamable_http_app()`. The `lifespan` context manager uses `async with mcp.session_manager.run()`.

**Rationale**: Based on the user-provided reference implementation (`app.py` from `mcp_server_code_review`). The template includes `TransportSecuritySettings` as commented-out optional customisation and `AuthContextMiddleware` as a commented-out middleware example.

**Template imports**:
```python
from mcp.server import FastMCP
from starlette.applications import Starlette
from starlette.routing import Mount
```

---

## R-005: Template file cleanup

**Decision**: The two existing MCP templates — `server.py.jinja2` (monolithic MCP impl) and `entrypoint_main.py.jinja2` (asyncio main) — are **deleted**. They are replaced by:

| Old file | New file | Purpose |
|----------|----------|---------|
| `mcp/server.py.jinja2` | `mcp/tools.py.jinja2` | `bind_tools(mcp)` stub |
| (none) | `mcp/resources.py.jinja2` | `bind_resources(mcp)` stub |
| (none) | `mcp/prompts.py.jinja2` | `bind_prompts(mcp)` stub |
| `mcp/entrypoint_main.py.jinja2` | `mcp/server.py.jinja2` | uvicorn entrypoint |
| (none) | `mcp/app.py.jinja2` | Starlette/FastMCP factory |
| `mcp/test_server.py.jinja2` | `mcp/test_tools.py.jinja2` | tools test stub |
| (none) | `mcp/test_resources.py.jinja2` | resources test stub (optional) |
| (none) | `mcp/test_prompts.py.jinja2` | prompts test stub (optional) |

**Note**: The `mcp/__init__.py.jinja2` is unchanged.
