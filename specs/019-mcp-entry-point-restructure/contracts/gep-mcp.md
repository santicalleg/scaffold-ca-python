# CLI Contract: `gep --type mcp` (MCP Entry Point Restructure)

**Feature**: `019-mcp-entry-point-restructure`  
**Command**: `scaffold generate-entry-point` / `scaffold gep`  
**Scope**: Changes affecting `--type mcp` only

---

## Command Signature

```
scaffold gep --type mcp [--with-resources] [--with-prompts] [--dry-run]
scaffold generate-entry-point --type mcp [--with-resources] [--with-prompts] [--dry-run]
```

---

## Flags

| Flag | Type | Default | Valid with types | Description |
|------|------|---------|-----------------|-------------|
| `--type` | str | — | all | Entry-point type: `restapi`, `agent`, `mcp`, `generic` |
| `--with-resources` | bool (flag) | `False` | `mcp` only | Generate `resources.py` primitive + `test_resources.py` |
| `--with-prompts` | bool (flag) | `False` | `mcp` only | Generate `prompts.py` primitive + `test_prompts.py` |
| `--dry-run` | bool (flag) | `False` | all | Preview all changes without writing to disk |

### Existing flags (unchanged)

| Flag | Valid with `mcp` | Notes |
|------|-----------------|-------|
| `--swagger` | No | restapi only — existing guard preserved |
| `--enable-kafka` | No | agent only — existing guard preserved |
| `--enable-mcp-client` | No | not valid with mcp — existing guard preserved |

---

## Guard Rules

### New guards (this feature)

1. **`--with-resources` / `--with-prompts` type guard**

   If `--with-resources` or `--with-prompts` is passed with any `--type` other than `mcp`:
   ```
   Error: --with-resources and --with-prompts are only valid with --type mcp.
   ```
   Exit code: `1`

### Existing guards (unchanged)

2. Duplicate `mcp_server/` directory guard — exits 1 with hint.
3. Incompatible `restapi` entry point guard — exits 1 with hint.

---

## Output: Files Generated

### `scaffold gep --type mcp` (base, no optional flags)

```text
src/<pkg>/
├── application/
│   └── app.py                                         ← NEW
├── infrastructure/
│   └── entry_points/
│       └── mcp_server/
│           ├── __init__.py                            ← unchanged
│           └── tools.py                               ← NEW (replaces server.py)
└── server.py                                          ← NEW (replaces main.py)

src/tests/
└── infrastructure/
    └── entry_points/
        └── mcp_server/
            └── test_tools.py                          ← NEW (replaces test_server.py)
```

### `scaffold gep --type mcp --with-resources`

Adds:
```text
src/<pkg>/infrastructure/entry_points/mcp_server/resources.py
src/tests/infrastructure/entry_points/mcp_server/test_resources.py
```

### `scaffold gep --type mcp --with-prompts`

Adds:
```text
src/<pkg>/infrastructure/entry_points/mcp_server/prompts.py
src/tests/infrastructure/entry_points/mcp_server/test_prompts.py
```

---

## Output: pyproject.toml Changes

### `[project.scripts]` update

Before:
```toml
[project.scripts]
my_project = "my_project.main:main"
```

After:
```toml
[project.scripts]
my_project = "my_project.server:main"
```

### `[project.dependencies]` additions

```
mcp>=1.0
uvicorn[standard]>=0.20
starlette>=0.40
dependency-injector>=4.49.0
pydantic-settings>=2.13.1
```

---

## Dry-Run Output Contract

When `--dry-run` is used, the command MUST:

1. Print a Rich file tree of all files that would be created (same structure as live run)
2. Print: `Would add to [project.dependencies]: mcp>=1.0, uvicorn[standard]>=0.20, starlette>=0.40, ...`
3. Print: `Would update [project.scripts]: <pkg> = "<pkg>.server:main"`
4. Print: `main.py will be replaced with mcp entrypoint.`
5. Exit code: `0`
6. Write nothing to disk

---

## Generated File Interfaces

### `tools.py` — public interface

```python
@inject
async def bind_tools(
    mcp: FastMCP,
    usecase: SomeUseCase = Provide[Container.usecase_container.some_usecase]
) -> None: ...
```

### `resources.py` — public interface

```python
@inject
async def bind_resources(
    mcp: FastMCP,
    usecase: SomeUseCase = Provide[Container.usecase_container.some_usecase]
) -> None: ...
```

### `prompts.py` — public interface

```python
@inject
def bind_prompts(
    mcp: FastMCP,
    prompt_usecase: SomeUseCase = Provide[Container.some_usecase]
) -> None: ...
```

### `application/app.py` — public interface

```python
def start_server() -> Starlette: ...
```

### `server.py` — public interface

```python
def main() -> None: ...  # called by [project.scripts] entry
```
