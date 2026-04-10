# Quickstart: App Factory Split (Feature 009)

**Audience**: Developer implementing Feature 009
**Date**: 2026-04-10

---

## Prerequisites

- Python 3.13+, `uv`, `ruff`, `mypy` configured in the workspace
- Feature 008 branch merged or branch `009-app-factory-split` checked out
- Tests passing: `uv run pytest tests/` (expect ~450 passing)

---

## What Changes

Feature 009 splits the current monolithic `server.py` template into two generated files:

| Before (feature 008) | After (feature 009) |
|---|---|
| `server.py` — factory + lifecycle + process start | `application/app.py` — factory + lifecycle + process start |
| *(nothing)* | `server.py` — thin wrapper, 5 lines |
| `main.py` overwritten by gep | `main.py` NOT emitted |
| 1 test file (`test_rest_controller.py`) | 5 test files (one per source file) |

---

## Step-by-step Implementation Order

### Step 1 — Create `app.py.jinja2` (new template)

**File**: `src/scaffold_ca_python/templates/entry_point/restapi/app.py.jinja2`

Move `lifespan`, `create_app`, `start_server` from `server.py.jinja2` into this new template. Update the `uvicorn.run()` factory path to `{{ project.python_package }}.application.app:create_app`.

### Step 2 — Update `server.py.jinja2` (thin wrapper)

**File**: `src/scaffold_ca_python/templates/entry_point/restapi/server.py.jinja2`

Replace the entire content with the thin wrapper:

```python
"""Process entry point for {{ project.name }}."""
from {{ project.python_package }}.application.app import start_server

if __name__ == "__main__":
    start_server()
```

### Step 3 — Create four new test templates

**Files** (all in `src/scaffold_ca_python/templates/entry_point/restapi/`):
- `test_app.py.jinja2` — asserts `create_app()` returns `FastAPI`, router+handlers registered, lifespan wires container
- `test_server.py.jinja2` — asserts `start_server` is importable from `application.app`; `server.py` does not start server on import
- `test_exception_handler.py.jinja2` — asserts correct JSON + status codes for all three handler types
- `test_schemas.py.jinja2` — asserts `ErrorResponse` (or equivalent schema class) is importable and has expected fields

### Step 4 — Update `_build_operations` in `generate_entry_point.py`

Add `application/app.py`  and all four new test files to the `restapi` branch of `_build_operations`. The `application/` path uses `project_root / "src" / pkg / "application" / "app.py"`.

```
tests/application/test_app.py   ← use path: project_root / "tests" / "application" / "test_app.py"
```

### Step 5 — Remove `main.py` overwrite block

In `_generate_entry_point_impl`, delete the `"Overwrite main.py with type-specific entrypoint"` block (~7 lines, including the console warning and `writer.execute` call).

### Step 6 — Write RED tests first (TDD)

Add assertions to:
- `tests/commands/test_generate_entry_point.py` — `test_restapi_creates_app_py`, `test_restapi_no_main_py`, `test_restapi_server_py_is_thin_wrapper`, new test-file existence checks
- `tests/templates/test_entry_point_templates.py` — rendering tests for all 4 new templates + updated `server.py` template

Run `uv run pytest tests/` → confirm new tests are RED before implementing.

### Step 7 — Implement (GREEN)

Execute steps 1–5 above. Run `uv run pytest tests/` → confirm all tests GREEN.

### Step 8 — Quality gates

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run mypy src/
uv run pytest tests/ --cov=src --cov-fail-under=80
```

All must pass with zero errors.

---

## Verify end-to-end

```bash
# Bootstrap a test project
cd /tmp && scaffold ca --name demo_api
cd demo_api

# Run gep
scaffold gep --type restapi

# Confirm app.py exists and main.py does not
test -f src/demo_api/application/app.py && echo "app.py OK"
test ! -f src/demo_api/main.py && echo "no main.py OK"

# Confirm server.py is thin (≤ 5 non-blank lines)
grep -v '^\s*$' src/demo_api/server.py | grep -v '^#' | wc -l

# Run generated tests (requires project deps installed)
cd /tmp/demo_api && uv sync && uv run pytest tests/
```

---

## File Touch Summary

| File | Action |
|---|---|
| `src/scaffold_ca_python/templates/entry_point/restapi/app.py.jinja2` | **CREATE** |
| `src/scaffold_ca_python/templates/entry_point/restapi/server.py.jinja2` | **UPDATE** |
| `src/scaffold_ca_python/templates/entry_point/restapi/test_app.py.jinja2` | **CREATE** |
| `src/scaffold_ca_python/templates/entry_point/restapi/test_server.py.jinja2` | **CREATE** |
| `src/scaffold_ca_python/templates/entry_point/restapi/test_exception_handler.py.jinja2` | **CREATE** |
| `src/scaffold_ca_python/templates/entry_point/restapi/test_schemas.py.jinja2` | **CREATE** |
| `src/scaffold_ca_python/commands/generate_entry_point.py` | **UPDATE** |
| `tests/commands/test_generate_entry_point.py` | **UPDATE** (new assertions) |
| `tests/templates/test_entry_point_templates.py` | **UPDATE** (new rendering tests) |
| `ms_test/src/ms_test/server.py` | **UPDATE** (thin wrapper — ms_test reference impl) |
| `ms_test/src/ms_test/application/app.py` | **CREATE** (ms_test reference impl) |
