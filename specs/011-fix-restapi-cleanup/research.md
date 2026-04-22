# Research: Fix RestAPI Entry Point Cleanup

**Feature**: 011-fix-restapi-cleanup | **Date**: 2026-04-10

## Q1 — How should `[project.scripts]` be updated in `pyproject.toml`?

**Decision**: Add two new functions to `pyproject_writer.py` following the existing `inject_dependencies` / `dry_run_inject` pattern: `update_project_scripts(project_root, pkg)` and `dry_run_scripts_update(project_root, pkg)`.

**Rationale**: The file already uses `tomllib` (read) + `tomli_w` (write) for TOML mutations. Reusing the same pattern keeps the module cohesive, makes it testable in isolation, and avoids string-manipulation of raw TOML text (which would risk breaking formatting).

**Implementation**:
```python
def update_project_scripts(project_root: Path, pkg: str) -> bool:
    """Set [project.scripts] entry for pkg to pkg.server:start_server. Returns True if changed."""
    pyproject = project_root / "pyproject.toml"
    with pyproject.open("rb") as fh:
        data = tomllib.load(fh)
    scripts: dict[str, str] = data.setdefault("project", {}).setdefault("scripts", {})
    new_value = f"{pkg}.server:start_server"
    if scripts.get(pkg) == new_value:
        return False
    scripts[pkg] = new_value
    with pyproject.open("wb") as fh:
        tomli_w.dump(data, fh)
    return True

def dry_run_scripts_update(project_root: Path, pkg: str) -> bool:
    """Return True if update_project_scripts would change the file."""
    pyproject = project_root / "pyproject.toml"
    with pyproject.open("rb") as fh:
        data = tomllib.load(fh)
    scripts = data.get("project", {}).get("scripts", {})
    return scripts.get(pkg) != f"{pkg}.server:start_server"
```

**Alternatives considered**:
- Raw text regex replace: Rejected — fragile, corrupts TOML formatting, hard to keep idempotent.
- Patching `pyproject_toml.jinja2` to emit `server:start_server`: Rejected — FR-003 explicitly forbids this; project creation should not assume a restapi entry point.

---

## Q2 — Where does `main.py` deletion and scripts update go in the command flow?

**Decision**: Both operations execute **after** the `writer.execute(operations, dry_run=False)` call and **after** `inject_dependencies`, at the bottom of `_generate_entry_point_impl`, guarded by `if type_ == "restapi":`.

**Rationale**: This mirrors the existing `if type_ != "restapi":` block that overwrites `main.py` for other types. Placing it at the end ensures the main files are already written before cleanup runs.

**Dry-run placement**: In the existing dry-run `return` block, add a preview note:
```python
if type_ == "restapi":
    if (project_root / "src" / pkg / "main.py").exists():
        console.print("[dim]Would delete: src/{pkg}/main.py[/dim]")
    if dry_run_scripts_update(project_root, pkg):
        console.print(f"[dim]Would update [project.scripts]: {pkg} = \"{pkg}.server:start_server\"[/dim]")
```

---

## Q3 — Should `schemas.py` be missing from `_build_operations` restapi list?

**Decision**: Out of scope for this feature. The current file content (as of 2026-04-10) omits `schemas.py` from the restapi operations list. This may be an unintended regression from feature 009's reformatting, but it is not in scope here. A separate fix feature should address it.

---

## Q4 — Are there any existing tests that conflict with the new behaviour?

**Decision**: `test_restapi_no_main_py` (line 91 in `test_generate_entry_point.py`) pre-deletes `main.py` and then asserts gep doesn't re-create it. After this feature, `gep --type restapi` will also actively delete `main.py` — this test remains correct (main.py absent both before and after). No existing tests need to be removed or modified.

**Note**: `test_dry_run_does_not_create_main_py` pre-deletes `main.py` and verifies the dry-run doesn't create it. After this feature, dry-run still should not create or delete main.py (dry-run never writes files) — test remains valid.

---

## Q5 — Should the scripts update be idempotent if `[project.scripts]` section is missing?

**Decision**: Yes. `update_project_scripts` uses `setdefault` to create `[project.scripts]` if absent (same pattern as `inject_dependencies` with `setdefault` for `dependencies`). This covers FR edge case: "What if `pyproject.toml` does not contain a `[project.scripts]` section?"
