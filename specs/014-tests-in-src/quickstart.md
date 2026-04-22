# Quickstart: Move Tests to src/ Layout; Add Entrypoint Exclusivity Validation

**Feature**: `014-tests-in-src` | **Date**: 2026-04-13

---

## Problem Summary

Three separate issues fixed by this feature:

1. **Wrong tests location**: `scaffold ca` creates `tests/` at the project root. All `generate-*` commands write test files into `project_root/tests/...`. The reference project (`ms_test`) and the desired layout both require `src/tests/`.

2. **Partial exclusivity guard**: `gep --type restapi` correctly blocks if mcp/agent already exists. The reverse (mcp/agent blocked if restapi exists) is missing, allowing users to create invalid mixed-entrypoint projects.

3. **Broken `pyproject_toml.jinja2`**: The template has three hardcoded bugs: `source = ["mcp_server_code_review"]` (wrong package name), `--cov=ms_test` (hardcoded project name in addopts), and `testpaths = ["tests"]` (wrong path after this fix).

---

## Fix Summary (5 change sets)

### 1 — Add `resolve_tests_root` to `core/project_detector.py`

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

Import and use this in: `generate_model`, `generate_use_case`, `generate_helper`, `generate_driven_adapter`, `generate_entry_point`, `delete_module`.

### 2 — Update `generate_project.py` (1 line)

```python
# Before
_add(operations, target_dir / "tests" / "__init__.py", "")
# After
_add(operations, target_dir / "src" / "tests" / "__init__.py", "")
```

### 3 — Add reverse exclusivity guard in `generate_entry_point.py`

After the existing `if type_ == "restapi":` guard block, add:

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

### 4 — Fix `pyproject_toml.jinja2` (4 fields)

```toml
# testpaths
testpaths = ["src/tests"]

# ruff per-file-ignores
"src/tests/**/*.py" = ["ANN"]

# coverage source
[tool.coverage.run]
source = ["{{ python_package }}"]

# pytest addopts
addopts = "--cov={{ python_package }} --cov-fail-under=80"
```

### 5 — Create ms_test reference project

Create `ms_test/` at repo root with:
- Full CA source skeleton under `ms_test/src/ms_test/`
- Tests under `ms_test/src/tests/` (src-layout)
- `ms_test/pyproject.toml` with correct testpaths, coverage source, dev deps (pytest, pytest-cov, httpx)

---

## Verification

```bash
# 1. CLI test suite — all path assertions updated
uv run pytest tests/ --ignore=tests/performance --no-cov -q
# Expected: same 2 pre-existing tombstone failures, all others pass

# 2. Full coverage gate
uv run pytest tests/ --ignore=tests/performance --cov=src --cov-fail-under=80 -q

# 3. Smoke test — generated project uses src/tests/
cd /tmp && scaffold ca --name LayoutTest && cd layout_test
scaffold gep --type restapi
# Assert: src/tests/infrastructure/entry_points/api/v1/test_rest_controller.py exists
# Assert: tests/ does NOT exist at root

# 4. Exclusivity smoke test
scaffold gep --type mcp   # must exit 1 with error
echo "Exit: $?"

# 5. ms_test reference project
cd /path/to/repo/ms_test && uv run pytest -q
# Expected: exit 0, all tests pass
```

---

## File Map (affected source files)

```
src/scaffold_ca_python/
├── core/
│   └── project_detector.py          ← add resolve_tests_root()
├── templates/project/
│   └── pyproject_toml.jinja2        ← fix 4 fields
└── commands/
    ├── generate_project.py          ← src/tests/ init path
    ├── generate_entry_point.py      ← resolve_tests_root + mcp/agent guard
    ├── generate_model.py            ← resolve_tests_root
    ├── generate_use_case.py         ← resolve_tests_root
    ├── generate_helper.py           ← resolve_tests_root
    ├── generate_driven_adapter.py   ← resolve_tests_root
    └── delete_module.py             ← resolve_tests_root

tests/commands/
├── test_generate_project.py         ← path + new test
├── test_generate_entry_point.py     ← paths + 3 new exclusivity tests
├── test_generate_model.py           ← paths
├── test_generate_use_case.py        ← paths
├── test_generate_helper.py          ← paths
├── test_generate_driven_adapter.py  ← paths
├── test_delete_module.py            ← paths
└── test_performance.py              ← paths

ms_test/                             ← new reference project
├── pyproject.toml
├── src/
│   ├── ms_test/                     ← CA skeleton
│   └── tests/                       ← src-layout tests
└── uv.lock
```
