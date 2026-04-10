# Research: App Factory Split (Feature 009)

**Status**: Complete — no NEEDS CLARIFICATION markers in spec
**Date**: 2026-04-10

---

## Decision 1: Where does `app.py` live?

- **Decision**: `application/app.py` — placed directly under `src/<pkg>/application/`
- **Rationale**: Clean Architecture constitution (Principle I) places the composition root in `application/`. The factory (`create_app`) and lifecycle (`lifespan`) are composition concerns — they wire the container, register routers, and attach exception handlers. `application/` is the correct layer.
- **Alternatives considered**: `infrastructure/entry_points/api/v1/app.py` (rejected — factory is not a transport adapter); `server.py` unchanged (rejected — exactly the problem this feature solves).
- **Evidence from codebase**: `ms_test/src/ms_test/application/` already contains `config/container.py` and `config/config.py` — composition-root configuration lives here. Adding `app.py` is consistent.

---

## Decision 2: What does the new `server.py` template look like?

- **Decision**: Two-line thin wrapper — `from {{ project.python_package }}.application.app import start_server` + `start_server()` guard, plus `if __name__ == "__main__": start_server()`. The `start_server()` function stays in `application/app.py`.
- **Rationale**: `server.py` is the process entry point registered in `[project.scripts]`. It must not contain business or wiring logic. All wiring stays in `application/app.py`.
- **Alternatives considered**: `uvicorn.run()` directly in `server.py` (rejected — duplicates Settings logic); moving `start_server` to a separate `application/server.py` (rejected — unnecessary indirection; `app.py` already owns the factory context).
- **Evidence**: User-provided example: `from application import app; app.start_server()`. The factory callable reference in uvicorn must also be updated from `<pkg>.server:create_app` → `<pkg>.application.app:create_app`.

---

## Decision 3: How is `main.py` suppressed without breaking existing callers?

- **Decision**: Remove the `main.py` overwrite block from `_generate_entry_point_impl` (the `"Overwrite main.py"` section at the bottom of that function). The `entrypoint_main.py.jinja2` template and `main.py.jinja2` template can remain on disk as legacy artefacts but will no longer be invoked by `gep --type restapi`.
- **Rationale**: The current code explicitly overwrites `main.py` after creating the API files. Removing that block is the minimal, reversible change.  `server.py` already acts as the `[project.scripts]` entry point for feature 008; `main.py` is redundant.
- **Alternatives considered**: Deleting `entrypoint_main.py.jinja2` (rejected — risky, other types use it; keep as tombstone); writing a `--no-main` flag (rejected — over-engineering, this should simply not happen for restapi).
- **Clarification**: The `entrypoint_main.py.jinja2` template currently points to a stale uvicorn path (`infrastructure/entry_points/restapi/main:app`). It is NOT used in the new restapi flow and should remain untouched (other types may reference it).

---

## Decision 4: Test template strategy — one template per source file

- **Decision**: Add four new test templates to `src/scaffold_ca_python/templates/entry_point/restapi/`:
  - `test_app.py.jinja2` — tests for `application/app.py` (factory + lifespan)
  - `test_server.py.jinja2` — tests for the thin `server.py`
  - `test_exception_handler.py.jinja2` — tests for `exception_handler.py`
  - `test_schemas.py.jinja2` — tests for `schemas.py`
  - `test_rest_controller.py.jinja2` already exists (feature 008) — no change needed
- **Rationale**: Constitution Principle II mandates dedicated tests per template group. Principle V (TDD) requires generated test files so that consumers start with a passing suite.
- **Alternatives considered**: Single `test_app_stack.py` aggregating all assertions (rejected — each file's test should be independently runnable and clearly named).
- **Test placement in generator**: `test_app.py` lands at `tests/application/test_app.py`; the others land in `tests/infrastructure/entry_points/api/v1/`.

---

## Decision 5: `_build_operations` changes in `generate_entry_point.py`

- **Decision**: Extend the `restapi` branch of `_build_operations` to:
  1. Emit `application/app.py` via a new `CreateFile` operation pointing to `project_root / "src" / pkg / "application" / "app.py"`.
  2. Emit `tests/application/test_app.py` via a new test `CreateFile`.
  3. Emit four new test files in `test_dir`: `test_server.py`, `test_exception_handler.py`, `test_schemas.py` (test_rest_controller already emitted).
  4. Update the `server.py` `CreateFile` to use the new thin-wrapper template.
  5. Remove the trailing `main.py` overwrite block from `_generate_entry_point_impl`.
- **Rationale**: All changes are additive or replacement inside the existing pattern; no new command infrastructure is needed.

---

## Decision 6: `uvicorn.run` factory path update in `application/app.py`

- **Decision**: In the new `app.py.jinja2`, the `start_server()` function calls:
  ```python
  uvicorn.run("{{ project.python_package }}.application.app:create_app", factory=True, ...)
  ```
  The old path `<pkg>.server:create_app` no longer works once `create_app` moves to `application/app.py`.
- **Rationale**: Factory mode requires the dotted path to the factory callable, not the app instance.
- **Evidence**: `ms_test/src/ms_test/server.py` line 67: `uvicorn.run("ms_test.server:create_app", factory=True, ...)` — this path breaks after the split.

---

## No Open Unknowns

All decisions are resolved. No external research was required — the technology stack
(Python 3.13, uv, ruff, mypy strict, pytest, Jinja2, FastAPI, uvicorn,
dependency-injector, pydantic-settings) is already in use and fully understood.
