# Research: Move Tests to src/ Layout; Add Entrypoint Exclusivity Validation

**Feature**: `014-tests-in-src` | **Date**: 2026-04-13

---

## Q1 — Where should `resolve_tests_root` live in the CLI codebase?

**Decision**: Add `resolve_tests_root(project_root: Path) -> Path` as a free function in `src/scaffold_ca_python/core/project_detector.py`.
**Rationale**: `project_detector.py` already owns project-layout resolution (`find_project_root`, `_get_python_package`). Placing the layout probe there keeps all path-discovery logic in one module, avoids a new file, and matches the existing import pattern used by every command (`from scaffold_ca_python.core.project_detector import find_project_root`). All 7 affected commands already import from this module.
**Alternatives considered**: A separate `core/layout.py` module — rejected; would be a one-function file with no growth path. Inline per-command — rejected; duplicates the probe logic 7 times.

---

## Q2 — What is the exact probe logic for backward compatibility?

**Decision**:
```python
def resolve_tests_root(project_root: Path) -> Path:
    src_tests = project_root / "src" / "tests"
    if src_tests.exists():
        return src_tests
    root_tests = project_root / "tests"
    if root_tests.exists():
        return root_tests
    return src_tests  # new project default
```
**Rationale**: The probe must not assume a specific layout. For new projects (neither exists yet), returning `src_tests` is the correct default so all `generate-*` commands create `src/tests/...` even before `src/tests/__init__.py` is created (the `FileWriter` creates parent directories). For older projects with `tests/` at root, the fallback preserves their layout.
**Alternatives considered**: Always returning `src/tests/` — would silently write test files in the wrong place for older projects without warning.

---

## Q3 — How should the mcp/agent → restapi reverse exclusivity guard be implemented?

**Decision**: In `_generate_entry_point_impl` in `generate_entry_point.py`, after the existing restapi guard block (lines 104–117), add a parallel guard for `mcp` and `agent` types that checks for `infrastructure/entry_points/api`:
```python
if type_ in ("mcp", "agent"):
    restapi_dir = project_root / "src" / project_ctx.python_package / "infrastructure" / "entry_points" / "api"
    if restapi_dir.exists():
        console.print(
            f"[red]Error:[/red] Incompatible entry point '[bold]restapi[/bold]' "
            f"already exists at: {restapi_dir.relative_to(project_root)}\n"
            "[dim]Hint:[/dim] A project may have only one entry-point type. "
            f"Remove '{restapi_dir.relative_to(project_root)}' before adding {type_}."
        )
        raise typer.Exit(code=1) from None
```
**Rationale**: Mirrors the existing pattern exactly (same Rich formatting, same hint structure, same `Exit(code=1)`). The restapi directory is `infrastructure/entry_points/api/` — checking its existence is the minimal probe needed. `generic` type is not included in the `type_ in ("mcp", "agent")` check, satisfying FR-007.
**Alternatives considered**: A centralised `_check_exclusivity(type_, project_root, project_ctx)` helper — too abstract for a two-branch symmetry; direct inline is cleaner and matches the existing pattern.

---

## Q4 — What fixes are needed in `pyproject_toml.jinja2`?

**Decision**: Three fixes in one pass:
1. `testpaths = ["tests"]` → `testpaths = ["src/tests"]`
2. `"tests/**/*.py"` (ruff per-file-ignores) → `"src/tests/**/*.py"`
3. `source = ["mcp_server_code_review"]` (coverage run) → `source = ["{{ python_package }}"]`
4. `addopts = "-x --cov=ms_test --junitxml=out_report.xml"` → `addopts = "--cov={{ python_package }} --cov-fail-under=80"` (remove hardcoded project name and junit artifact; keep 80% gate consistent with constitution Principle V)

**Rationale**: Items 1 and 2 directly implement FR-002. Items 3 and 4 are bugs in the current template: `mcp_server_code_review` is a hardcoded lefover project name (not even the template variable), and the hardcoded `--cov=ms_test` would emit the wrong package name for any project other than ms_test. Both must use `{{ python_package }}`.
**Alternatives considered**: Keeping `addopts` unchanged — rejected because a generated project with hardcoded wrong cov source breaks `uv run pytest` out of the box.

---

## Q5 — Which CLI test files need path updates and how many assertions?

**Decision**: Update all path assertions in 7 CLI command test files. Exact counts:

| File | Assertions to update |
|------|---------------------|
| `test_generate_project.py` | 1 (`tests/__init__.py` → `src/tests/__init__.py`) |
| `test_generate_entry_point.py` | 8 path assertions + 2 cleanup `shutil.rmtree` + 3 `unlink` calls = 13 |
| `test_generate_model.py` | 2 |
| `test_generate_use_case.py` | 2 |
| `test_generate_helper.py` | 2 |
| `test_generate_driven_adapter.py` | 4 |
| `test_delete_module.py` | 2 |
| `test_performance.py` | 4 |

**Total**: ~30 path string updates.
**Rationale**: All assertions directly test the path where generated files land. Once the source commands change their `test_dir`/`test_path`, all assertions must match.

---

## Q6 — Should `delete_module.py` use the probe or always `src/tests/`?

**Decision**: Use `resolve_tests_root(project_root)`. `dm` deletes test files from wherever they live. If a user runs `dm` on a pre-feature project where tests are at root, the probe resolves to `tests/` and deletes correctly.
**Rationale**: Backward compatibility is more important than simplicity here — silently not deleting test files would be a worse user experience than using the probe.

---

## Q7 — What does the ms_test reference project need?

**Decision**: Create `ms_test/` as a fully structured reference project at the scaffold-ca-python repo root, matching the desired post-feature layout. Required files:
- `ms_test/src/ms_test/` — full CA skeleton (application, domain, infrastructure, server.py) — source files as described in the user's attachment
- `ms_test/src/tests/__init__.py` — tests root (src-layout)
- `ms_test/src/tests/infrastructure/entry_points/api/v1/test_rest_controller.py` — health endpoint tests using `starlette.testclient.TestClient`
- `ms_test/src/tests/application/test_app.py` — asserts `create_app()` returns FastAPI
- `ms_test/pyproject.toml` — fixed: `testpaths = ["src/tests"]`, `source = ["ms_test"]`, `httpx` in dev deps
- Existing source files (app.py, rest_controller.py, exception_handler.py, server.py, config/) preserved

**Rationale**: ms_test does not exist on disk currently (deleted or never committed to this branch). It must be created as part of this feature to satisfy FR-008 and FR-009. Its test stubs are the minimal set needed to validate SC-005 (`uv run pytest -q` exits 0).
