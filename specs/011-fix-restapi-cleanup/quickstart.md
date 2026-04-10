# Quickstart: Fix RestAPI Entry Point Cleanup

**Feature**: 011-fix-restapi-cleanup | **Date**: 2026-04-10

## What Changes

After this feature, running `gep --type restapi` in a project created by `scaffold ca` will:

1. **Delete** `src/<pkg>/main.py` (was created by `scaffold ca` but is now superseded by `server.py`)
2. **Patch** `[project.scripts]` in `pyproject.toml` to point to `server:start_server`

## Before / After

### Before (feature 009 baseline)

```toml
# pyproject.toml — after gep --type restapi
[project.scripts]
my_app = "my_app.main:main"   # ← broken: main.py no longer contains start logic
```
```
src/my_app/
├── main.py          ← still present but stale
├── server.py        ← thin wrapper calling start_server()
└── application/
    └── app.py       ← factory + start_server()
```

### After (this feature)

```toml
# pyproject.toml — after gep --type restapi
[project.scripts]
my_app = "my_app.server:start_server"   # ← correct
```
```
src/my_app/
├── server.py        ← thin wrapper, registered as CLI entry point
└── application/
    └── app.py       ← factory + start_server()
# main.py deleted ✓
```

## Workflow

```bash
# 1. Create project
scaffold ca --name MyApp
cd my_app

# 2. Generate restapi entry point
scaffold gep --type restapi
# Output:
# ✓ Entry point api/v1 created. Created 11 file(s).
# ✓ Added fastapi>=0.135.2, uvicorn>=0.20 to [project.dependencies].
# ✓ Deleted src/my_app/main.py
# ✓ Updated [project.scripts]: my_app = "my_app.server:start_server"

# 3. Preview only (no writes)
scaffold gep --type restapi --dry-run
# Shows file tree + would-add deps + would delete main.py + would update scripts

# 4. Install and run
uv sync
my_app   # ← runs start_server() via uvicorn
```

## Dry-Run Preview

```
api/v1 (dry run)
├── src/my_app/application/app.py
├── src/my_app/infrastructure/entry_points/api/v1/__init__.py
├── ...
Would add to [project.dependencies]: fastapi>=0.135.2, uvicorn>=0.20
Would delete: src/my_app/main.py
Would update [project.scripts]: my_app = "my_app.server:start_server"
```

## Other Entry-Point Types are Unaffected

```bash
scaffold gep --type agent    # main.py overwritten as before; [project.scripts] unchanged
scaffold gep --type mcp      # main.py overwritten as before; [project.scripts] unchanged
scaffold gep --type generic  # main.py overwritten as before; [project.scripts] unchanged
```
