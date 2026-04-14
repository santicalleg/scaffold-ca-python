# Implementation Plan: Move Tests to src/ Layout; Add Entrypoint Exclusivity Validation

**Branch**: `014-tests-in-src` | **Date**: 2026-04-13 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/014-tests-in-src/spec.md`

## Summary

Three bugs fixed by this feature: (1) all `scaffold ca` and `generate-*` commands write test files to `project_root/tests/` but the reference layout (`ms_test`) requires `src/tests/` — a new `resolve_tests_root()` utility centralises the probe; (2) `gep --type mcp/agent` does not check for an existing restapi entry point before proceeding, allowing mixed-entrypoint projects — a reverse exclusivity guard is added; (3) `pyproject_toml.jinja2` contains hardcoded stale values (`mcp_server_code_review`, `ms_test`, `tests`) that break every generated project — all four fields are fixed with template variables. The `ms_test` reference project is also created at the repository root to serve as a living end-to-end example.

## Technical Context

**Language/Version**: Python 3.13  
**Primary Dependencies**: Typer (CLI), Rich (output formatting), Jinja2 (template rendering), Pydantic v2, pytest 9.0, pytest-cov, ruff, mypy strict, uv (package manager)  
**Storage**: Local filesystem — Path operations only  
**Testing**: pytest + `typer.testing.CliRunner`; 80% coverage gate (constitution Principle V)  
**Target Platform**: macOS / Linux developer workstation  
**Project Type**: CLI code-generation tool (Python library + executable)  
**Performance Goals**: No new performance requirements  
**Constraints**: No external I/O; all path logic uses `pathlib.Path`; backward compatibility required for pre-feature projects (resolution probe); template output must be ruff-clean and mypy-compliant  
**Scale/Scope**: 9 source files modified; ~30 CLI test path assertions updated; 4 new tests; ms_test reference project created (~30 files)

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I — Clean Architecture in generated projects | ✅ PASS | Template changes keep generated layout valid; `src/tests/` is outside the package, no layer dependency violations |
| II — Template-Driven Code Generation | ✅ PASS | `pyproject_toml.jinja2` fixed; no new ad-hoc string assembly introduced; `tests/templates/` unaffected (no new Jinja2 templates) |
| III — Full Command Parity | ✅ PASS | All 7 `generate-*` commands updated consistently; `--dry-run` for `scaffold ca` will show `src/tests/__init__.py` |
| IV — Python-First Idioms | ✅ PASS | `resolve_tests_root` typed; ruff + mypy clean |
| V — Test-First Development | ✅ PASS | RED tests written before implementation in all phases; 80% coverage gate maintained |
| VI — Developer Experience | ✅ PASS | Exclusivity error messages include Rich formatting and resolution hints; dry-run behaviour preserved |
| VII — Branch naming | ✅ PASS | `014-tests-in-src` follows `NNN-kebab-name` convention |

No gate violations.

## Project Structure

### Documentation (this feature)

```text
specs/014-tests-in-src/
├── plan.md          ← this file
├── research.md      ← Phase 0 output
├── data-model.md    ← Phase 1 output
├── quickstart.md    ← Phase 1 output
└── tasks.md         ← /speckit.tasks output (NOT created by /speckit.plan)
```

### Source Code (modified / created)

```text
src/scaffold_ca_python/
├── core/
│   └── project_detector.py          ← add resolve_tests_root()
├── templates/project/
│   └── pyproject_toml.jinja2        ← fix testpaths, ruff ignores, coverage source, addopts
└── commands/
    ├── generate_project.py          ← src/tests/__init__.py path
    ├── generate_entry_point.py      ← resolve_tests_root + mcp/agent → restapi guard
    ├── generate_model.py            ← resolve_tests_root for test_path
    ├── generate_use_case.py         ← resolve_tests_root for test_path
    ├── generate_helper.py           ← resolve_tests_root for test_dir
    ├── generate_driven_adapter.py   ← resolve_tests_root for test_dir
    └── delete_module.py             ← resolve_tests_root for tests_root

tests/commands/
├── test_generate_project.py         ← update 1 path; add test_ca_creates_src_tests_init
├── test_generate_entry_point.py     ← update 13 paths; add 3 exclusivity tests
├── test_generate_model.py           ← update 2 paths
├── test_generate_use_case.py        ← update 2 paths
├── test_generate_helper.py          ← update 2 paths
├── test_generate_driven_adapter.py  ← update 4 paths
├── test_delete_module.py            ← update 2 paths
└── test_performance.py              ← update 4 paths

ms_test/                             ← NEW reference project (FR-008, FR-009)
├── pyproject.toml
├── uv.lock
└── src/
    ├── ms_test/                     ← full CA skeleton
    │   ├── __init__.py
    │   ├── server.py
    │   ├── application/
    │   │   ├── app.py
    │   │   └── config/
    │   ├── domain/
    │   │   ├── model/__init__.py
    │   │   └── usecase/__init__.py
    │   └── infrastructure/
    │       ├── driven_adapters/__init__.py
    │       ├── entry_points/api/v1/
    │       │   ├── rest_controller.py
    │       │   └── exception_handler.py
    │       └── helpers/__init__.py
    └── tests/                       ← src-layout tests
        ├── __init__.py
        ├── application/test_app.py
        └── infrastructure/entry_points/api/v1/test_rest_controller.py
```

## Complexity Tracking

No constitution violations. Feature is corrective (fixing broken behaviour) + additive (new utility + new reference project). Medium complexity due to the number of files with path updates (~30 assertions), but each change is a mechanical string substitution.

## Phase 0: Research Summary

All research decisions are resolved. See [research.md](research.md).

| Decision | Outcome |
|----------|---------|
| Q1 — Where does `resolve_tests_root` live? | `core/project_detector.py` (existing import chain) |
| Q2 — Probe logic | `src/tests/` if exists; `tests/` if exists; else `src/tests/` (new project) |
| Q3 — Reverse exclusivity guard | Inline in `generate_entry_point.py` mirroring existing pattern |
| Q4 — Template fixes | 4 fields: testpaths, ruff ignores, coverage source, addopts |
| Q5 — CLI test file scope | ~30 path assertions across 8 test files |
| Q6 — `delete_module` probe | Uses `resolve_tests_root` for backward compatibility |
| Q7 — ms_test state | Does not exist on disk; must be created as part of this feature |

## Phase 1: Design Summary

See [data-model.md](data-model.md) and [quickstart.md](quickstart.md).

### `resolve_tests_root` signature

```python
def resolve_tests_root(project_root: Path) -> Path:
    """Return the tests root for a project, probing for src-layout vs root-layout."""
    src_tests = project_root / "src" / "tests"
    if src_tests.exists():
        return src_tests
    root_tests = project_root / "tests"
    if root_tests.exists():
        return root_tests
    return src_tests
```

### Reverse exclusivity guard (generate_entry_point.py)

Inserted after the existing `if type_ == "restapi":` guard, before `if type_ == "restapi": subdir = "api/v1"`:

```python
if type_ in ("mcp", "agent"):
    restapi_dir = (
        project_root / "src" / project_ctx.python_package
        / "infrastructure" / "entry_points" / "api"
    )
    if restapi_dir.exists():
        console.print(
            f"[red]Error:[/red] Incompatible entry point '[bold]restapi[/bold]' "
            f"already exists at: {restapi_dir.relative_to(project_root)}\n"
            "[dim]Hint:[/dim] A project may have only one entry-point type. "
            f"Remove '{restapi_dir.relative_to(project_root)}' before adding {type_}."
        )
        raise typer.Exit(code=1) from None
```

### pyproject_toml.jinja2 diff (key fields only)

```diff
-"tests/**/*.py" = ["ANN"]
+"src/tests/**/*.py" = ["ANN"]

-source = ["mcp_server_code_review"]
+source = ["{{ python_package }}"]

-addopts = "-x --cov=ms_test --junitxml=out_report.xml"
+addopts = "--cov={{ python_package }} --cov-fail-under=80"

-testpaths = ["tests"]
+testpaths = ["src/tests"]
```
