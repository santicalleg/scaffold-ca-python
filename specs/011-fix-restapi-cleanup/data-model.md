# Data Model: Fix RestAPI Entry Point Cleanup

**Feature**: 011-fix-restapi-cleanup | **Date**: 2026-04-10

## Overview

No new domain entities or Pydantic models are introduced. This feature operates on two existing data structures:

---

## Existing Entity: `pyproject.toml` TOML structure

The relevant slice of the TOML document (typed as Python dict after `tomllib.load`):

```python
{
    "project": {
        "name": str,                   # package name
        "scripts": {                   # dict[str, str] — may be absent before update
            "<pkg>": str               # entry point target, e.g. "my_app.server:start_server"
        },
        "dependencies": list[str],     # managed by inject_dependencies (existing)
    }
}
```

### Fields Changed by This Feature

| Field | Before `gep --type restapi` | After `gep --type restapi` |
|-------|----------------------------|---------------------------|
| `project.scripts.<pkg>` | `"<pkg>.main:main"` | `"<pkg>.server:start_server"` |

### Invariants

- The `pyproject.toml` file always exists at `project_root/pyproject.toml` when `gep` runs (enforced by `find_project_root()`).
- The `[project.scripts]` section **may** already be present (from `pyproject_toml.jinja2`).
- If `[project.scripts]` is absent, `update_project_scripts` creates it via `setdefault`.
- `update_project_scripts` is idempotent: calling it twice produces one entry, not two.

---

## Existing File: `src/<pkg>/main.py`

| State | Condition |
|-------|-----------|
| Exists | Freshly scaffolded project that has not had `gep --type restapi` run |
| Absent | After `gep --type restapi` completes, or if manually deleted by developer |

### Delete Semantics

- Deletion uses `Path.unlink(missing_ok=True)` — silent no-op if already absent.
- Dry-run: file is **not** deleted; a preview message is emitted to stdout.

---

## New Functions in `pyproject_writer.py`

| Function | Signature | Returns | Side Effect |
|----------|-----------|---------|-------------|
| `update_project_scripts` | `(project_root: Path, pkg: str) -> bool` | `True` if file was changed | Writes updated `pyproject.toml` |
| `dry_run_scripts_update` | `(project_root: Path, pkg: str) -> bool` | `True` if change would occur | None — read-only |
