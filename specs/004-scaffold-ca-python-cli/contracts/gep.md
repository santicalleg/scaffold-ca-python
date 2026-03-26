# Contract: `gep` / `generate-entry-point`

**Command**: `scaffold gep` (alias: `scaffold generate-entry-point`)  
**US**: US-5 — Scaffold entry point

---

## Purpose

Generates an entry-point adapter inside `infrastructure/entry_points/` and its test stub. Entry-point type determines the framework, template set, and dependencies added.

---

## Signature

```
scaffold gep --type <TYPE> [--swagger <FILE>] [--enable-kafka] [--enable-mcp-client] [--dry-run]
```

| Flag | Type | Required | Default | Description |
|---|---|---|---|---|
| `--type` | `str` | **Yes** | — | Entry-point type. One of: `restapi`, `agent`, `mcp`, `generic` |
| `--swagger` | `str` (path) | No | — | Path to an OpenAPI YAML/JSON file. Contract-first: generates typed routes+models from spec. Only valid with `--type restapi`. |
| `--enable-kafka` | `bool` | No | `False` | Add async Kafka consumer stub. Valid with `restapi` and `generic`. |
| `--enable-mcp-client` | `bool` | No | `False` | Add MCP tool-call client stub. Valid with `restapi` and `agent`. |
| `--dry-run` | `bool` | No | `False` | Preview files without writing any output |

---

## Type Behaviour

### `restapi` (FastAPI)

Generates a FastAPI async application:

```
src/my_project/infrastructure/entry_points/restapi/
    __init__.py
    main.py                    ← FastAPI app factory
    router.py                  ← APIRouter with async route stubs
    health.py                  ← /health endpoint
    schemas.py                 ← Pydantic request/response models (or generated from --swagger)
tests/infrastructure/entry_points/restapi/
    test_router.py
```

If `--swagger <FILE>` is provided, `schemas.py` and `router.py` are generated from the OpenAPI contract rather than empty stubs.

### `agent` (A2A)

Generates an Agent-to-Agent (A2A) protocol entry point:

```
src/my_project/infrastructure/entry_points/agent/
    __init__.py
    agent.py                   ← A2A async handler stub
    card.py                    ← AgentCard definition
tests/infrastructure/entry_points/agent/
    test_agent.py
```

### `mcp`

Generates a Model Context Protocol server entry point:

```
src/my_project/infrastructure/entry_points/mcp_server/
    __init__.py
    server.py                  ← MCP server stubs (tools, resources, prompts)
tests/infrastructure/entry_points/mcp_server/
    test_server.py
```

### `generic`

Generates an empty async entry-point with no framework:

```
src/my_project/infrastructure/entry_points/generic/
    __init__.py
    entry_point.py
tests/infrastructure/entry_points/generic/
    test_entry_point.py
```

---

## Dry-Run

Prints all file paths and their content to stdout; writes nothing.

---

## Prerequisites

Must be run inside a directory tree that contains a `pyproject.toml` with a `[tool.scaffold-ca-python]` section.

---

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Files created (or dry-run completed) successfully |
| `1` | Validation error |
| `2` | Internal/unexpected error |

---

## Errors

| Condition | Message | Exit |
|---|---|---|
| `--type` not in allowed list | `Unknown type 'X'. Allowed: restapi, agent, mcp, generic.` | `1` |
| `--swagger` used without `--type restapi` | `--swagger is only valid with --type restapi.` | `1` |
| `--swagger` path does not exist | `Swagger file 'X' not found.` | `1` |
| `--enable-mcp-client` used with `--type mcp` | `--enable-mcp-client is not valid with --type mcp.` | `1` |
| Target directory already exists | `Directory 'src/.../restapi/' already exists.` | `1` |
| No project root | `No scaffold-ca-python project found. Run 'scaffold ca' first.` | `1` |
