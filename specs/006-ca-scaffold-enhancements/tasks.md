# Tasks: Clean Architecture Scaffold Enhancements

**Feature Branch**: `feature/006-ca-scaffold-enhancements`
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)
**Total tasks**: 42 | **Parallelizable**: 30

> **Spec US-4 (Auto-inject Dependencies) traceability**: Dependency injection into `pyproject.toml`
> is tested per-command inside `[US4]` test tasks. SC-005 (idempotency) is verified in T042.

---

## Phase 1: Setup — Add `tomli-w` dependency

- [X] T001 Add `tomli-w>=1.0` to `[dependencies]` in `pyproject.toml`

**Checkpoint**: `uv sync` succeeds. `import tomli_w` works inside the venv.

---

## Phase 2: Foundational — Core engine changes (BLOCKS all user stories)

- [X] T002 [P] skip the file-existence guard (the `path must not exist check`) and call `os.replace` directly when `overwrite=True`; parent-dir creation MUST still occur.
- [X] T003 [P] Write unit tests for the `overwrite` flag in `FileWriter` — `overwrite=True` replaces an existing file; `overwrite=False` (default) raises or errors on existing target — in tests/core/test_file_writer.py
- [X] T004 Create `src/scaffold_ca_python/core/pyproject_writer.py` with two public functions: `inject_dependencies(project_root: Path, packages: list[str]) -> list[str]` (writes; returns actually-added packages) and `dry_run_inject(project_root: Path, packages: list[str]) -> list[str]` (returns packages that would be added, no write); uses `tomllib` + `tomli_w`; idempotent (skips packages already present by name prefix)
- [X] T005 [P] Write unit tests for `pyproject_writer` in tests/core/test_pyproject_writer.py: adds new package, skips duplicate, handles `[project.dependencies]` absent, returns empty list when all present, `dry_run_inject` never writes, malformed TOML raises clear error
- [X] T006 Remove `package: str` field from `ProjectContext` in src/scaffold_ca_python/models/context.py; update all 9 `_load_project_context` helper functions in src/scaffold_ca_python/commands/ (generate_model.py, generate_use_case.py, generate_driven_adapter.py, generate_entry_point.py, generate_helper.py, generate_pipeline.py, delete_module.py, validate_structure.py, update_project.py) to no longer read or pass `package`

**Checkpoint**: `uv run mypy src/` passes. All existing tests that construct `ProjectContext` with `package=` are updated and pass.

---

## Phase 3: User Story 1 — Simplified Project Bootstrapping (Priority: P1)

**Story goal**: `scaffold ca --name X` produces a production-ready skeleton with `.python-version`, `Dockerfile`, `.dockerignore`, ruff config inline in `pyproject.toml`, and no `--package` flag.

**Independent Test**: Project root contains exactly the files listed in spec US-1 scenario 1. `pyproject.toml` has `[tool.ruff]` + `[tool.ruff.lint]`. No `.ruff.toml` exists. `scaffold ca --name X --package y` exits 1.

### Tests for US1 *(write first)*

- [X] T007 [P] [US1] Update tests/commands/test_generate_project.py: remove all `package=` arguments from `ProjectContext` constructions and CLI invocations; add assertions that `.dockerignore`, `.python-version`, `Dockerfile` are created; assert `.ruff.toml` is NOT created; assert `pyproject.toml` contains `[tool.ruff.lint]`; assert `--package` flag exits 1

### Templates for US1

- [X] T008 [P] [US1] [US2] Update src/scaffold_ca_python/templates/project/pyproject_toml.jinja2: remove `package = "{{ package }}"` line from `[tool.scaffold-ca-python]`; expand `[tool.ruff]` to include `[tool.ruff.lint]` with `select`, `ignore`, and `[tool.ruff.lint.per-file-ignores]` sections; add `"dependency-injector>=4.41"` and `"pydantic-settings>=2.0"` to `[project.dependencies]` *(T015, T023, and T030 depend on this task completing first)*
- [X] T009 [P] [US1] Create src/scaffold_ca_python/templates/project/dockerfile.jinja2 — minimal multi-stage `python:3.13-slim` stub: `FROM python:3.13-slim AS base`, install uv, copy source, install deps, `CMD ["python", "-m", "{{ python_package }}"]`
- [X] T010 [P] [US1] Create src/scaffold_ca_python/templates/project/dockerignore.jinja2 — standard patterns: `.venv`, `__pycache__`, `*.pyc`, `*.pyo`, `.pytest_cache`, `.mypy_cache`, `dist/`, `.git`, `*.egg-info`
- [X] T011 [P] [US1] Create src/scaffold_ca_python/templates/project/python_version.jinja2 — renders `3.13\n` (single line, no Jinja2 variables needed)
- [X] T012 [P] [US1] Delete src/scaffold_ca_python/templates/project/ruff_toml.jinja2 (ruff config is now fully inline in pyproject_toml.jinja2)

### Implementation for US1

- [X] T013 [US1] Update `_generate_project_impl` in src/scaffold_ca_python/commands/generate_project.py: remove `package` parameter; remove `.ruff.toml` `_add` call; add `_add` calls for `Dockerfile`, `.dockerignore`, `.python-version`; update `ProjectContext(name=name)` (no `package`); update `register()` to remove `--package` from both `generate-project` and `ca` command wrappers
- [X] T014 [US1] (a) Update tests/templates/test_project_templates.py: assert `[tool.ruff.lint]` present and `package` key absent in rendered `pyproject_toml.jinja2` output; assert `python_version.jinja2` renders `3.13`. (b) Create tests/templates/test_docker_templates.py (new file): render `dockerfile.jinja2` and assert `FROM python:3.13-slim` and `python_package` variable present; render `dockerignore.jinja2` and assert `.venv` and `__pycache__` present

**Checkpoint**: `scaffold ca --name OrderService` produces the full tree including Docker files. No `.ruff.toml` created. `scaffold ca --name OrderService --package x` exits 1. All US1 tests pass.

---

## Phase 4: User Story 2 — DI Scaffolding (Priority: P2)

**Story goal**: `scaffold ca` produces `application/config/` with 5 DI files wired with `dependency-injector`; `dependency-injector` and `pydantic-settings` listed in generated `pyproject.toml`.

**Independent Test**: `src/order_service/application/config/` contains all 5 files. Each passes `python -m py_compile`. `pyproject.toml` lists both deps.

### Tests for US2 *(write first)*

- [ ] T015 [P] [US2] Update tests/commands/test_generate_project.py: add assertions for the 5 DI config files being created (`application/config/__init__.py`, `config.py`, `driven_adapters_container.py`, `usecases_container.py`, `container.py`); assert generated `pyproject.toml` contains `dependency-injector` and `pydantic-settings` in `[project.dependencies]`

### Templates for US2

- [ ] T016 [P] [US2] Create src/scaffold_ca_python/templates/project/application/config/__init__.py.jinja2 — empty module docstring stub: `"""DI configuration package."""\n`
- [ ] T017 [P] [US2] Create src/scaffold_ca_python/templates/project/application/config/config.py.jinja2 — renders `Settings(BaseSettings)` with `ENV: str`, `LOG_LEVEL: str`, `SettingsConfigDict(env_file=".env")`, and `settings = Settings()` singleton
- [ ] T018 [P] [US2] Create src/scaffold_ca_python/templates/project/application/config/driven_adapters_container.py.jinja2 — renders `DAContainer(containers.DeclarativeContainer)` with placeholder `providers.Singleton` stub; imports use `{{ python_package }}` namespace
- [ ] T019 [P] [US2] Create src/scaffold_ca_python/templates/project/application/config/usecases_container.py.jinja2 — renders `UseCaseContainer(containers.DeclarativeContainer)` with `da_container = providers.DependenciesContainer()` and placeholder use-case `providers.Singleton`; imports use `{{ python_package }}` namespace
- [ ] T020 [P] [US2] Create src/scaffold_ca_python/templates/project/application/config/container.py.jinja2 — renders `Container(containers.DeclarativeContainer)` wiring `DAContainer` and `UseCaseContainer` via `providers.Container`; imports use `{{ python_package }}` namespace

### Implementation for US2

- [ ] T021 [US2] Update `_generate_project_impl` in src/scaffold_ca_python/commands/generate_project.py: add `_add` calls for all 5 DI config files rendering from the new templates under `application/config/`
- [ ] T022 [P] [US2] Create tests/templates/test_di_config_templates.py: render each of the 5 DI templates with a representative `ProjectContext`; assert `DAContainer` in `driven_adapters_container.py` output; assert `UseCaseContainer` and `DependenciesContainer` in `usecases_container.py` output; assert `Container` and two `providers.Container` wires in `container.py` output; assert `Settings` and `BaseSettings` in `config.py` output

**Checkpoint**: `scaffold ca --name OrderService` produces all 5 DI files. Each passes `python -m py_compile`. Tests pass.

---

## Phase 5: User Story 3 — `main.py` Lifecycle (Priority: P3)

**Story goal**: `scaffold ca` creates `src/<pkg>/main.py` with Hello World. `scaffold gep --type <type>` overwrites it with the correct entrypoint bootstrap. `[project.scripts]` in `pyproject.toml` points to it.

**Independent Test**: After `scaffold ca`, `src/order_service/main.py` contains `def main() -> None` printing "Hello, World!". After `scaffold gep --type restapi`, `main.py` contains `uvicorn.run(...)`.

### Tests for US3 *(write first)*

- [ ] T023 [P] [US3] Update tests/commands/test_generate_project.py: add assertion that `src/<pkg>/main.py` is created; assert it defines `def main`; assert `pyproject.toml` `[project.scripts]` entry exists with format `<python_package> = "<python_package>.main:main"`
- [ ] T024 [P] [US3] Update tests/commands/test_generate_entry_point.py: for each of the 4 types, assert `main.py` is overwritten after `scaffold gep`; assert the overwritten content is type-appropriate (e.g., `uvicorn` for restapi, agent runner for agent); assert a warning message is printed to stdout

### Templates for US3

- [ ] T025 [P] [US3] Create src/scaffold_ca_python/templates/project/main.py.jinja2 — default entrypoint: `def main() -> None: print("Hello, World!")` plus `if __name__ == "__main__": main()`
- [ ] T026 [P] [US3] Create src/scaffold_ca_python/templates/entry_point/restapi/entrypoint_main.py.jinja2 — `uvicorn.run("{{ python_package }}.infrastructure.entry_points.restapi.main:app", host="0.0.0.0", port=8000, reload=False)` wrapped in `def main() -> None`
- [ ] T027 [P] [US3] Create src/scaffold_ca_python/templates/entry_point/agent/entrypoint_main.py.jinja2 — runs the agent entry-point's async `run()` via `asyncio.run()`, wrapped in `def main() -> None`
- [ ] T028 [P] [US3] Create src/scaffold_ca_python/templates/entry_point/mcp/entrypoint_main.py.jinja2 — starts the MCP server, wrapped in `def main() -> None`
- [ ] T029 [P] [US3] Create src/scaffold_ca_python/templates/entry_point/generic/entrypoint_main.py.jinja2 — calls generic handler `run()` via `asyncio.run()`, wrapped in `def main() -> None`

### Implementation for US3

- [ ] T030 [US3] Update `_generate_project_impl` in src/scaffold_ca_python/commands/generate_project.py: add `_add` call rendering `project/main.py.jinja2` to `src/<pkg>/main.py`; ensure `pyproject_toml.jinja2` already has the `[project.scripts]` entry (verify in T008)
- [ ] T031 [US3] Update `_generate_entry_point_impl` in src/scaffold_ca_python/commands/generate_entry_point.py: after successful file generation, print `[yellow]⚠[/yellow] main.py will be replaced with <type> entrypoint.`; render `entry_point/<type>/entrypoint_main.py.jinja2`; write to `src/<pkg>/main.py` using `CreateFile` with `overwrite=True` on the `GeneratedFile`
- [ ] T032 [P] [US3] Create tests/templates/test_entrypoint_main_templates.py (new file): render each of the 4 `entry_point/<type>/entrypoint_main.py.jinja2` templates with a representative `ProjectContext`; assert `def main` present in each; assert type-appropriate import (`uvicorn` for restapi, `asyncio` for agent/mcp/generic)

**Checkpoint**: `scaffold ca --name X` creates `main.py`. `scaffold gep --type restapi` overwrites it with uvicorn runner. Warning printed. All US3 tests pass.

---

## Phase 6: User Story 4 — Auto-inject Dependencies (Priority: P4)

**Story goal**: `gep` and `gda` commands append required packages to `[project.dependencies]` in the project's `pyproject.toml` post-generation. `--dry-run` prints what would be added. Idempotent.

**Independent Test**: After `scaffold gep --type restapi`, `pyproject.toml` contains `fastapi` and `uvicorn[standard]`. Running again does not duplicate them. `--dry-run` prints but does not write.

### Tests for US4 *(write first)*

- [ ] T033 [P] [US4] Update tests/commands/test_generate_entry_point.py: for each type with non-empty `_DEP_MAP`, assert `pyproject.toml` gains the expected packages; assert running the same command twice does not duplicate packages; assert `--dry-run` does NOT modify `pyproject.toml` but prints the packages; assert `main.py` is NOT modified after `gep --type restapi --dry-run` (FR-016); assert package injection is skipped (no error) when `pyproject.toml` is absent (outside CA project — existing exit-1 path covers this)
- [ ] T034 [P] [US4] Update tests/commands/test_generate_driven_adapter.py: for `rest-consumer` assert `httpx` added; for `secrets` assert `boto3` added; for `generic` assert no packages added; assert idempotency; assert `--dry-run` does not write

### Implementation for US4

- [ ] T035 [US4] Add `_DEP_MAP: dict[str, list[str]]` to src/scaffold_ca_python/commands/generate_entry_point.py: `{"restapi": ["fastapi>=0.100", "uvicorn[standard]>=0.20"], "agent": ["a2a-sdk>=0.1"], "mcp": ["mcp>=1.0"], "generic": []}`; call `inject_dependencies` (real) or `dry_run_inject` + print (dry-run) after successful file generation; print `[green]✓[/green] Added X, Y to [project.dependencies].` when packages are added
- [ ] T036 [US4] Add `_DEP_MAP: dict[str, list[str]]` to src/scaffold_ca_python/commands/generate_driven_adapter.py: `{"rest-consumer": ["httpx>=0.27"], "secrets": ["boto3>=1.34"], "generic": []}`; call `inject_dependencies` / `dry_run_inject` after successful file generation; print confirmation when packages are added

**Checkpoint**: All US4 acceptance scenarios pass. Idempotency confirmed. `--dry-run` never writes. Tests pass.

---

## Final Phase: Polish & Regression

- [ ] T037 [P] Run `uv run ruff check src/ tests/` and fix any new lint errors introduced by changes (unused imports after `package` removal, etc.)
- [ ] T038 [P] Run `uv run mypy src/` and fix any new type errors (especially around `ProjectContext` without `package`, `GeneratedFile.overwrite`, and `pyproject_writer.py` signatures)
- [ ] T039 Update tests/commands/test_workflow.py (E2E workflow test): remove any `package=` references; assert the workflow still exits 0 end-to-end; assert `main.py` is present after `ca` step; assert `mypy.ini` is present after `ca` step (FR-017 continuity)
- [ ] T040 Update tests/commands/test_dry_run_checksum.py: verify `ca` dry-run checksum still passes after the new files are in scope
- [ ] T041 [P] Run `uv run pytest -q --benchmark-disable` and confirm all existing tests pass (no regression on T001–T092); fix any broken tests caused by `package` removal
- [ ] T042 [P] Write idempotency integration test in tests/commands/test_generate_entry_point.py: scaffold a project, run `gep --type restapi` twice, assert `pyproject.toml` contains exactly one `fastapi` entry (SC-005 / FR-015)

**Checkpoint**: `uv run pytest -q --benchmark-disable` passes with ≥80% coverage. `ruff` and `mypy` exit 0. No regression on previously passing tests.

---

## Dependencies & Execution Order

```
Phase 1 (Setup)        → No dependencies; start immediately
Phase 2 (Foundational) → Requires Phase 1 complete; BLOCKS all user stories
Phase 3 (US-1)         → Requires Phase 2 complete
Phase 4 (US-2)         → Requires Phase 2 + Phase 3 complete (needs updated pyproject_toml.jinja2 from T008)
Phase 5 (US-3)         → Requires Phase 2 + Phase 3 complete (needs updated generate_project.py from T013)
Phase 6 (US-4)         → Requires Phase 2 + Phase 3 complete (needs pyproject_writer from T004)
Final Phase (Polish)   → Requires Phases 3–6 complete
```

### User Story Dependencies

| Story | Depends On | Reason |
|---|---|---|
| US-1 (ca simplification) | Phase 2 | Needs `ProjectContext` without `package` (T006) |
| US-2 (DI scaffolding) | Phase 2, US-1 | `generate_project.py` must already be clean of `--package` before adding more ops |
| US-3 (main.py lifecycle) | Phase 2, US-1 | `generate_project.py` base updated in US-1; `FileWriter.overwrite` from T002 |
| US-4 (auto-inject deps) | Phase 2 | Needs `pyproject_writer.py` (T004); independent of US-2/US-3 |

### Within Each User Story

1. **Tests** — write and confirm failing *(mandatory first step)*
2. **Templates** — create/update Jinja2 source files *(parallel with test authoring)*
3. **Implementation** — update command handlers *(after tests and templates)*

---

## Parallel Execution Examples

### Phase 2 — Foundational (all [P] tasks parallelizable)

```text
Stream A: T002 → T003  (FileWriter overwrite flag + tests)
Stream B: T004 → T005  (pyproject_writer + tests)
Stream C: T006         (ProjectContext cleanup — sequential due to 9-file impact)
```

### Phase 3–6 — User Stories (independent streams after Phase 2)

```text
Stream A (US-1): T007 [P] → T008–T012 [P] → T013 → T014 [P]
Stream B (US-2): T015 [P] → T016–T020 [P] → T021 → T022 [P]
Stream C (US-3): T023 [P] + T024 [P] → T025–T029 [P] → T030 → T031 → T032 [P]
Stream D (US-4): T033 [P] + T034 [P] → T035 → T036
```

Streams A–D can all proceed in parallel after Phase 2 completes, with the intra-US-1 constraint
that T015, T023 depend on T013 being done first (same file: `generate_project.py`).

---

## Implementation Strategy

### MVP Scope (Phase 1 + Phase 2 + Phase 3)

Phase 3 alone (`scaffold ca` simplification + Docker files + ruff consolidation) is the highest-value
increment — it ships immediately after Phase 2 and removes the `--package` friction. The DI scaffolding
(Phase 4), `main.py` lifecycle (Phase 5), and auto-inject (Phase 6) can follow in order.

### Incremental Delivery

1. **Sprint 1 (MVP)**: Phases 1–3 → Ship simplified `scaffold ca` with Docker files
2. **Sprint 2**: Phase 4 → Ship DI scaffolding
3. **Sprint 3**: Phase 5 → Ship `main.py` lifecycle
4. **Sprint 4**: Phase 6 → Ship auto-inject dependencies
5. **Sprint 5**: Final Phase → Polish, coverage gate, no regression

---

## Summary

| Metric | Count |
|---|---|
| **Total tasks** | **42** |
| **Phase 1 (Setup)** | 1 task |
| **Phase 2 (Foundational)** | 5 tasks |
| **Phase 3 (US-1 ca simplification)** | 8 tasks |
| **Phase 4 (US-2 DI scaffolding)** | 8 tasks |
| **Phase 5 (US-3 main.py lifecycle)** | 10 tasks |
| **Phase 6 (US-4 auto-inject deps)** | 4 tasks |
| **Final Phase (Polish)** | 6 tasks |
| **Parallelizable tasks ([P])** | 28 tasks |

### Independent Test Criteria per Story

| Story | Independent Test |
|---|---|
| US-1 | `scaffold ca --name X` → root has Docker files, no `.ruff.toml`, `--package` rejected |
| US-2 | 5 DI files present; each `py_compile` clean; `pyproject.toml` has DI deps |
| US-3 | `main.py` created by `ca`; overwritten by `gep`; warning printed |
| US-4 | `gep`/`gda` append packages; idempotent; `--dry-run` never writes |

### Format Validation

All tasks follow the required checklist format: `- [ ] T### [P]? [US#]? Description with file path`. ✅
