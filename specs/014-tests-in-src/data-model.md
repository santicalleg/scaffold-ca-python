# Data Model: Move Tests to src/ Layout; Add Entrypoint Exclusivity Validation

**Feature**: `014-tests-in-src` | **Date**: 2026-04-13

This feature involves no persistent domain entities or storage schemas. The "data model" here describes the path-resolution contract, the exclusivity predicate, and the complete inventory of files being changed or created.

---

## Path Resolution Contract

### `resolve_tests_root(project_root: Path) -> Path`

A new free function added to `src/scaffold_ca_python/core/project_detector.py`.

| Input | Output |
|---|---|
| `project_root` with `src/tests/` present | `project_root / "src" / "tests"` |
| `project_root` with only `tests/` present (pre-feature) | `project_root / "tests"` |
| `project_root` with neither directory (fresh scaffold) | `project_root / "src" / "tests"` (new project default) |

**Consumers**: `generate_model`, `generate_use_case`, `generate_helper`, `generate_driven_adapter`, `generate_entry_point`, `delete_module` — all replace their hardcoded `project_root / "tests"` with `resolve_tests_root(project_root)`.

---

## Entrypoint Exclusivity Matrix

| Running `gep --type` → | restapi exists | mcp exists | agent exists | none |
|---|---|---|---|---|
| **restapi** | ❌ duplicate guard | ❌ existing check | ❌ existing check | ✅ |
| **mcp** | ❌ NEW (FR-005) | ❌ duplicate guard | ✅ allowed | ✅ |
| **agent** | ❌ NEW (FR-005) | ✅ allowed | ❌ duplicate guard | ✅ |
| **generic** | ✅ always | ✅ always | ✅ always | ✅ |

**Probe directory** for new mcp/agent → restapi check: `project_root / "src" / {pkg} / "infrastructure" / "entry_points" / "api"`.

---

## Template Changes

### `pyproject_toml.jinja2`

| Field | Current value | Fixed value |
|---|---|---|
| `testpaths` | `["tests"]` | `["src/tests"]` |
| ruff per-file-ignores key | `"tests/**/*.py"` | `"src/tests/**/*.py"` |
| `[tool.coverage.run] source` | `["mcp_server_code_review"]` | `["{{ python_package }}"]` |
| `addopts` | `"-x --cov=ms_test --junitxml=out_report.xml"` | `"--cov={{ python_package }} --cov-fail-under=80"` |

---

## Source Code Inventory

### Files modified in the CLI

| File | Change |
|---|---|
| `src/scaffold_ca_python/core/project_detector.py` | Add `resolve_tests_root(project_root)` free function |
| `src/scaffold_ca_python/templates/project/pyproject_toml.jinja2` | 4 field fixes (see table above) |
| `src/scaffold_ca_python/commands/generate_project.py` | `tests/__init__.py` → `src/tests/__init__.py` (1 line) |
| `src/scaffold_ca_python/commands/generate_entry_point.py` | Use `resolve_tests_root`; add mcp/agent → restapi guard |
| `src/scaffold_ca_python/commands/generate_model.py` | Use `resolve_tests_root` for `test_path` |
| `src/scaffold_ca_python/commands/generate_use_case.py` | Use `resolve_tests_root` for `test_path` |
| `src/scaffold_ca_python/commands/generate_helper.py` | Use `resolve_tests_root` for `test_dir` |
| `src/scaffold_ca_python/commands/generate_driven_adapter.py` | Use `resolve_tests_root` for `test_dir` |
| `src/scaffold_ca_python/commands/delete_module.py` | Use `resolve_tests_root` for `tests_root` |

### CLI test files modified (~30 path assertions)

| File | Path assertions updated |
|---|---|
| `tests/commands/test_generate_project.py` | 1 |
| `tests/commands/test_generate_entry_point.py` | 13 (path asserts + cleanup refs) |
| `tests/commands/test_generate_model.py` | 2 |
| `tests/commands/test_generate_use_case.py` | 2 |
| `tests/commands/test_generate_helper.py` | 2 |
| `tests/commands/test_generate_driven_adapter.py` | 4 |
| `tests/commands/test_delete_module.py` | 2 |
| `tests/commands/test_performance.py` | 4 |

### New CLI tests added

| File | New tests |
|---|---|
| `tests/commands/test_generate_entry_point.py` | `test_gep_mcp_blocked_when_restapi_exists`, `test_gep_agent_blocked_when_restapi_exists`, `test_gep_mcp_and_agent_coexist_no_error` |
| `tests/commands/test_generate_project.py` | `test_ca_creates_src_tests_init` (confirms `src/tests/__init__.py` created) |

### ms_test reference project files

All files live under `ms_test/` at the repository root.

**Source (creating or verifying)**:
- `ms_test/src/ms_test/__init__.py`
- `ms_test/src/ms_test/server.py`
- `ms_test/src/ms_test/application/__init__.py`
- `ms_test/src/ms_test/application/app.py`
- `ms_test/src/ms_test/application/config/__init__.py`
- `ms_test/src/ms_test/application/config/config.py`
- `ms_test/src/ms_test/application/config/container.py`
- `ms_test/src/ms_test/application/config/driven_adapters_container.py`
- `ms_test/src/ms_test/application/config/resource_container.py`
- `ms_test/src/ms_test/application/config/usecases_container.py`
- `ms_test/src/ms_test/domain/model/__init__.py`
- `ms_test/src/ms_test/domain/usecase/__init__.py`
- `ms_test/src/ms_test/infrastructure/driven_adapters/__init__.py`
- `ms_test/src/ms_test/infrastructure/entry_points/__init__.py`
- `ms_test/src/ms_test/infrastructure/entry_points/api/__init__.py`
- `ms_test/src/ms_test/infrastructure/entry_points/api/v1/__init__.py`
- `ms_test/src/ms_test/infrastructure/entry_points/api/v1/rest_controller.py`
- `ms_test/src/ms_test/infrastructure/entry_points/api/v1/exception_handler.py`
- `ms_test/src/ms_test/infrastructure/helpers/__init__.py`

**Tests (new, src-layout)**:
- `ms_test/src/tests/__init__.py`
- `ms_test/src/tests/application/__init__.py`
- `ms_test/src/tests/application/test_app.py`
- `ms_test/src/tests/infrastructure/__init__.py`
- `ms_test/src/tests/infrastructure/entry_points/__init__.py`
- `ms_test/src/tests/infrastructure/entry_points/api/__init__.py`
- `ms_test/src/tests/infrastructure/entry_points/api/v1/__init__.py`
- `ms_test/src/tests/infrastructure/entry_points/api/v1/test_rest_controller.py`

**Config**:
- `ms_test/pyproject.toml` — fixed testpaths, coverage source, dev deps
- `ms_test/uv.lock` — regenerated after dep changes
