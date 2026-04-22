# Tasks: Fix RestAPI Entry Point Cleanup

**Feature**: `011-fix-restapi-cleanup`  
**Spec**: [spec.md](spec.md) | **Plan**: [plan.md](plan.md)  
**Total tasks**: 27

**User Stories**:
- **US1 (P1)**: `gep --type restapi` deletes `src/<pkg>/main.py`
- **US2 (P1)**: `gep --type restapi` updates `[project.scripts]` to `<pkg>.server:start_server`

---

## Phase 1: Setup

**Purpose**: Verify baseline before any changes.

- [X] T001 Verify baseline — run `uv run pytest tests/ -q --no-cov`, confirm 461 passing / 8 pre-existing failures (2 tombstones + 6 restapi-schemas); record counts

**Checkpoint**: Baseline confirmed — implementation can begin

---

## Phase 2: Foundational — Extend `pyproject_writer.py`

**Purpose**: Add `update_project_scripts` and `dry_run_scripts_update` to `pyproject_writer.py`. These are blocking prerequisites for US2 implementation. US1 (file deletion) is independent and can proceed in parallel with this phase.

**Independent Test**: `uv run pytest tests/core/test_pyproject_writer.py -q` — all new unit tests GREEN before touching the command handler.

### Tests for Foundational Phase *(write first — must fail before T008–T009)*

- [X] T002 [P] Add `test_update_project_scripts_changes_entry` — make pyproject with `main:main`, call `update_project_scripts`, assert returns `True` and entry reads `<pkg>.server:start_server` · `tests/core/test_pyproject_writer.py`
- [X] T003 [P] Add `test_update_project_scripts_is_idempotent` — pyproject already has `server:start_server`, call twice, assert returns `False` on second call and entry unchanged · `tests/core/test_pyproject_writer.py`
- [X] T004 [P] Add `test_update_project_scripts_creates_section_when_absent` — pyproject with no `[project.scripts]` key, call function, assert section created and entry present · `tests/core/test_pyproject_writer.py`
- [X] T005 [P] Add `test_dry_run_scripts_update_returns_true_when_change_needed` — pyproject with `main:main`, assert returns `True`; file must not be modified · `tests/core/test_pyproject_writer.py`
- [X] T006 [P] Add `test_dry_run_scripts_update_returns_false_when_already_correct` — pyproject with `server:start_server`, assert returns `False` · `tests/core/test_pyproject_writer.py`
- [X] T007 [P] Add `test_dry_run_scripts_update_never_writes_to_disk` — call on pyproject with `main:main`, read raw bytes before and after, assert file bytes unchanged · `tests/core/test_pyproject_writer.py`

### Implementation for Foundational Phase

- [X] T008 Implement `update_project_scripts(project_root: Path, pkg: str) -> bool` — use `tomllib.load` + `data.setdefault("project", {}).setdefault("scripts", {})`, set entry, write with `tomli_w.dump` only if changed; return `True` iff file was written · `src/scaffold_ca_python/core/pyproject_writer.py`
- [X] T009 [P] Implement `dry_run_scripts_update(project_root: Path, pkg: str) -> bool` — read-only; return `True` iff current entry differs from `<pkg>.server:start_server` · `src/scaffold_ca_python/core/pyproject_writer.py`

**Checkpoint**: T002–T007 GREEN · `update_project_scripts` and `dry_run_scripts_update` fully unit-tested

---

## Phase 3: User Story 1 — Delete `main.py` (Priority: P1)

**Goal**: `gep --type restapi` removes `src/<pkg>/main.py` after scaffolding; silent no-op if already absent; dry-run reports the would-delete without touching the file.

**Independent Test**: Run `scaffold ca --name MyApp && gep --type restapi`; assert `src/my_app/main.py` does not exist.

### Tests for User Story 1 *(write first — must fail before T013–T014)*

- [X] T010 [US1] Add `test_restapi_deletes_main_py` — do NOT pre-delete `main.py`; run `gep --type restapi`; assert `src/my_app/main.py` absent after · `tests/commands/test_generate_entry_point.py`
- [X] T011 [P] [US1] Add `test_restapi_gep_ok_when_main_py_already_absent` — `unlink(missing_ok=True)` first; run `gep --type restapi`; assert `exit_code == 0` · `tests/commands/test_generate_entry_point.py`
- [X] T010b [P] [US1] Add `test_restapi_second_run_exits_with_duplicate_error` — run `gep --type restapi` twice on same project; assert second invocation `exit_code != 0`; assert `src/my_app/main.py` still absent · `tests/commands/test_generate_entry_point.py`
- [X] T012 [P] [US1] Add `test_restapi_dry_run_reports_would_delete_main_py` — run `gep --type restapi --dry-run`; assert `"main.py"` in output; assert `src/my_app/main.py` still exists (not deleted by dry-run) · `tests/commands/test_generate_entry_point.py`

### Implementation for User Story 1

- [X] T013 [US1] Add delete step to `_generate_entry_point_impl`: under the `if type_ == "restapi":` cleanup block (after `inject_dependencies`), add `main_py = project_root / "src" / pkg / "main.py"`, `main_py.unlink(missing_ok=True)`, and `console.print(f"[green]✓[/green] Deleted src/{pkg}/main.py")` · `src/scaffold_ca_python/commands/generate_entry_point.py`
- [X] T014 [P] [US1] Add dry-run preview for main.py deletion inside the `if dry_run:` block (before `return`): `if type_ == "restapi" and (project_root / "src" / pkg / "main.py").exists(): console.print(...)` · `src/scaffold_ca_python/commands/generate_entry_point.py`

**Checkpoint**: T010–T012 GREEN · `main.py` deleted after `gep --type restapi`; dry-run preview correct

---

## Phase 4: User Story 2 — Update `[project.scripts]` (Priority: P1)

**Goal**: `gep --type restapi` rewrites `[project.scripts]` so the installed CLI command calls `start_server()`; idempotent; dry-run previews without writing; other types unaffected.

**Independent Test**: Run `gep --type restapi`; read `pyproject.toml`; assert `[project.scripts]` entry reads `my_app = "my_app.server:start_server"`.

### Tests for User Story 2 *(write first — must fail before T019–T020)*

- [X] T015 [US2] Add `test_restapi_updates_project_scripts` — run `gep --type restapi`; read `pyproject.toml` via `tomllib`; assert `data["project"]["scripts"]["my_app"] == "my_app.server:start_server"` · `tests/commands/test_generate_entry_point.py`
- [X] T016 [P] [US2] Add `test_restapi_dry_run_reports_scripts_update` — run `gep --type restapi --dry-run`; assert `"server:start_server"` in output; re-read `pyproject.toml` and assert `data["project"]["scripts"]["my_app"] == "my_app.main:main"` (file unchanged) · `tests/commands/test_generate_entry_point.py`
- [X] T017 [P] [US2] Add `test_agent_does_not_change_project_scripts` — run `gep --type agent`; read `pyproject.toml`; assert scripts entry still `"my_app.main:main"` (not updated) · `tests/commands/test_generate_entry_point.py`
- [X] T018 [P] [US2] Add `test_mcp_does_not_change_project_scripts` — run `gep --type mcp`; read `pyproject.toml`; assert scripts entry unchanged · `tests/commands/test_generate_entry_point.py`
- [X] T018b [P] [US2] Add `test_generic_does_not_change_project_scripts` — run `gep --type generic`; read `pyproject.toml`; assert `data["project"]["scripts"]["my_app"] == "my_app.main:main"` · `tests/commands/test_generate_entry_point.py`

### Implementation for User Story 2

- [X] T019 [US2] Import `update_project_scripts`, `dry_run_scripts_update`; call in restapi block · `src/scaffold_ca_python/commands/generate_entry_point.py`
- [X] T020 [P] [US2] Add dry-run preview calling `dry_run_scripts_update` inside `if dry_run:` block

**Checkpoint**: T015–T018 GREEN · scripts updated for restapi; other types unaffected; dry-run correct

---

## Phase 5: Polish & Quality Gates

**Purpose**: Confirm linting, type-checking, and coverage gates all pass.

- [X] T021 [P] Run `uv run ruff check src/ tests/` — zero lint errors
- [X] T022 [P] Run `uv run ruff format src/ tests/` — zero format violations (apply fixes if needed)
- [X] T023 [P] Run `uv run mypy src/` — zero new type errors (2 pre-existing `generate_project.py` tombstones are acceptable)
- [X] T024 Run `uv run pytest tests/ --cov=src --cov-fail-under=80 -q` — ≥ 80% coverage; ≥ 476 tests passing (461 baseline + 15 new tests: T002–T007, T010–T010b–T011–T012, T015–T018–T018b)
- [ ] T025 Smoke test — (a) `scaffold ca --name TestApi`; assert fresh `pyproject.toml` scripts entry reads `test_api = "test_api.main:main"` (FR-003: template unchanged); (b) run `scaffold gep --type restapi`; assert `src/test_api/main.py` absent; assert `pyproject.toml` scripts entry is `test_api.server:start_server`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1** (Baseline): No dependencies — start immediately
- **Phase 2** (Foundational): No dependencies — can start after Phase 1
- **Phase 3** (US1): Independent of Phase 2 — can run in parallel with Phase 2
- **Phase 4** (US2): Depends on Phase 2 complete (`update_project_scripts` must exist)
- **Phase 5** (Polish): Depends on all story phases complete

### Parallel Opportunities

```
Phase 2 (T002–T009)  ──────────────────────────────► Phase 4 (T015–T020)
Phase 3 (T010–T014)  ─────────────────────────────────────────────────────► Phase 5 (T021–T025)
```

Within Phase 2:
```
T002, T003, T004, T005, T006, T007 [P] (unit tests) → T008 (implement update) → T009 [P] (implement dry_run)
```

Within Phase 3:
```
T010 (command test) → T013 (implement delete)
T011, T012 [P] (edge case tests) → T014 [P] (dry-run preview)
```

Within Phase 4:
```
T015 (command test) → T019 (implement update call)
T016, T017, T018 [P] (edge case tests) → T020 [P] (dry-run preview)
```

### Implementation Strategy

**MVP (Phase 1 + Phase 3 only)**: Delete `main.py` — already delivers SC-001 and eliminates the stale-entry-point confusion.  
**Full delivery (all phases)**: Both bugs fixed, scripts pointing to `server:start_server`, all quality gates green.
