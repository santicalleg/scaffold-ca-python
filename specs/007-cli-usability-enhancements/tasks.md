# Tasks: CLI Usability Enhancements

**Input**: Design documents from `/specs/007-cli-usability-enhancements/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Tests are MANDATORY per Principle V (TDD). Write each test batch first and confirm it FAILS before implementing the corresponding production code.

**Organization**: Tasks grouped by user story — each story is independently implementable and testable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Parallelizable — touches different files, no dependency on an incomplete preceding task
- **[Story]**: US1, US2, US3
- Exact file paths included in every description

---

## Phase 1: Setup

**Purpose**: Verify the green baseline before any changes.

- [X] T001 Verify baseline test suite passes: run `uv run pytest -q` and confirm all 405 tests pass, ≥80% coverage

---

## Phase 2: Foundational (Blocking Prerequisite for US2)

**Purpose**: Enable Rich markup mode on the root app — required for US2 epilog rendering to work; harmless to US1 and US3.

**⚠️ CRITICAL**: US2 epilog Rich markup will not render without this change.

- [X] T002 Add `rich_markup_mode="rich"` to the `typer.Typer(...)` constructor call in `src/scaffold_ca_python/cli.py`

**Checkpoint**: `rich_markup_mode` is set — US2 and US3 implementation can now proceed.

---

## Phase 3: User Story 1 — Rename `generate-project` to `clean-architecture` (Priority: P1) 🎯 MVP

**Goal**: `scaffold-ca-python clean-architecture --name X` works identically to the old `generate-project`. The old command name exits 1 with a migration hint. The `ca` alias is unchanged.

**Independent Test**: `uv run pytest tests/commands/test_generate_project.py tests/commands/test_cli.py -q` — all US1 tests pass.

### Tests for User Story 1 *(write FIRST — must FAIL before implementation)*

- [X] T003 [US1] Write failing tests for `clean-architecture` command in `tests/commands/test_generate_project.py`: (a) `clean-architecture --name Demo` exits 0 and creates `demo/` directory, (b) `clean-architecture --dry-run --name Demo` exits 0 without writing files, (c) `clean-architecture --help` output contains `--name` and `--dry-run`, (d) `ca --help` output is byte-for-byte identical to `clean-architecture --help` output (SC-004)
- [X] T004 [P] [US1] Write failing tests for `ca` alias parity and `generate-project` tombstone in `tests/commands/test_generate_project.py`: (a) `ca --name Demo` exits 0, (b) `generate-project --name Demo` exits 1 and output contains `clean-architecture`
- [X] T005 [P] [US1] Create `tests/commands/test_cli.py` and write failing test for root `--help` listing: (a) `clean-architecture` appears in root help output, (b) `generate-project` does NOT appear in root help output, (c) root help exit code is 0

### Implementation for User Story 1

- [X] T006 [US1] Rename `@app.command("generate-project", ...)` to `@app.command("clean-architecture", ...)` and update `short_help` to `"Scaffold a new CA project. Alias: ca"` in `src/scaffold_ca_python/commands/generate_project.py`
- [X] T007 [US1] Add deprecated tombstone `@app.command("generate-project", hidden=True, deprecated=True)` function that prints `[red]Error:[/red] 'generate-project' has been renamed. Use 'clean-architecture' (alias: ca) instead.` and raises `typer.Exit(1)` in `src/scaffold_ca_python/commands/generate_project.py`
- [X] T008 [US1] Update `ca` alias `help=` and docstring to reference `clean-architecture` instead of `generate-project` in `src/scaffold_ca_python/commands/generate_project.py`
- [X] T009 [US1] Run `uv run pytest tests/commands/test_generate_project.py tests/commands/test_cli.py -q` — confirm all US1 tests are green
- [X] T033 Amend Principle III table in `.specify/memory/constitution.md`: update `generate-project | ca` row to `clean-architecture | ca`, increment version to v2.0.2, add PATCH amendment note

**Checkpoint**: US1 fully functional — `clean-architecture` and `ca` work, `generate-project` exits 1 with hint, root help is clean, constitution reflects the rename.

---

## Phase 4: User Story 2 — Contextual per-command help with types tables and Examples epilog (Priority: P2)

**Goal**: `gep --help`, `gda --help`, and `gpipe --help` each display a structured types/providers table and a runnable Examples section.

**Independent Test**: `uv run pytest tests/commands/test_generate_entry_point.py tests/commands/test_generate_driven_adapter.py tests/commands/test_generate_pipeline.py -q` — all US2 tests pass.

### Tests for User Story 2 *(write FIRST — must FAIL before implementation)*

- [X] T010 [P] [US2] Write failing tests for `gep --help` epilog content in `tests/commands/test_generate_entry_point.py`: (a) output contains `restapi`, `agent`, `mcp`, `generic`, (b) output contains `agent type only` for `--enable-kafka` and `--enable-mcp-client`, (c) output contains `Examples`
- [X] T011 [P] [US2] Write failing tests for `gda --help` epilog content in `tests/commands/test_generate_driven_adapter.py`: (a) output contains `rest-consumer`, `secrets`, `generic`, (b) output contains `--name required` (or equivalent) for `generic` type, (c) output contains `Examples`
- [X] T012 [P] [US2] Write failing tests for `gpipe --help` epilog content in `tests/commands/test_generate_pipeline.py`: (a) output contains `github` and `azure`, (b) output contains `required` for `--provider`, (c) output contains `Examples`

### Implementation for User Story 2

- [X] T013 [US2] Update `_KAFKA_HELP`, `_MCP_CLIENT_HELP`, and `_TYPE_HELP` constants to include "(agent type only)" and type descriptions, and add `epilog=` with types table + Notes + Examples to `@app.command("generate-entry-point", ...)` in `src/scaffold_ca_python/commands/generate_entry_point.py`
- [X] T014 [P] [US2] Add `_TYPE_HELP` module-level constant and `epilog=` param with types table + Examples to `@app.command("generate-driven-adapter", ...)` in `src/scaffold_ca_python/commands/generate_driven_adapter.py`
- [X] T015 [P] [US2] Add `_PROVIDER_HELP` module-level constant and `epilog=` param with providers table + Examples to `@app.command("generate-pipeline", ...)` in `src/scaffold_ca_python/commands/generate_pipeline.py`
- [X] T016 [US2] Run `uv run pytest tests/commands/test_generate_entry_point.py tests/commands/test_generate_driven_adapter.py tests/commands/test_generate_pipeline.py -q` — confirm all US2 tests are green

**Checkpoint**: US2 fully functional — `gep`, `gda`, `gpipe` help shows types/providers tables and examples.

---

## Phase 5: User Story 3 — Default to help when invoked with no arguments (Priority: P3)

**Goal**: `scaffold-ca-python` (no args) exits 0 with root help. Every subcommand invoked with no arguments exits 0 with its own help.

**Independent Test**: `uv run pytest tests/commands/test_cli.py tests/commands/test_generate_model.py tests/commands/test_generate_use_case.py -q` (plus all other subcommand test files updated in this phase).

### Tests for User Story 3 *(write FIRST — must FAIL before implementation)*

- [ ] T017 [US3] Add failing test for root no-args behaviour to `tests/commands/test_cli.py`: `scaffold-ca-python` (no args) exits 0, output contains `Usage`
- [ ] T018 [P] [US3] Add failing no-args exit-0 tests to `tests/commands/test_generate_model.py` and `tests/commands/test_generate_use_case.py`: invoking `gm` / `guc` with no arguments exits 0 and output contains `--name`
- [ ] T019 [P] [US3] Add failing no-args exit-0 tests to `tests/commands/test_generate_entry_point.py`, `tests/commands/test_generate_driven_adapter.py`, and `tests/commands/test_generate_pipeline.py`: invoking `gep` / `gda` / `gpipe` with no arguments exits 0
- [ ] T020 [P] [US3] Add failing no-args exit-0 tests to `tests/commands/test_generate_helper.py`, `tests/commands/test_delete_module.py`, `tests/commands/test_validate_structure.py`, and `tests/commands/test_update_project.py`: invoking `gh` / `dm` / `vs` / `up` with no arguments exits 0

### Implementation for User Story 3

- [ ] T021 [US3] Replace `no_args_is_help=True` on root `typer.Typer(...)` with `@app.callback(invoke_without_command=True)` callback that prints `ctx.get_help()` and raises `typer.Exit(0)` when no subcommand is given in `src/scaffold_ca_python/cli.py`
- [ ] T022 [P] [US3] Add `ctx: typer.Context` first parameter and change `--name` from required (`typer.Option(...)`) to optional (`typer.Option(None, ...)`) with early-exit guard in the `register()` function of `src/scaffold_ca_python/commands/generate_model.py`
- [ ] T023 [P] [US3] Add `ctx: typer.Context` first parameter and change `--name` to optional with early-exit guard in the `register()` function of `src/scaffold_ca_python/commands/generate_use_case.py`
- [ ] T024 [P] [US3] Add `ctx: typer.Context` first parameter and change `--type` to optional with early-exit guard in the `register()` function of `src/scaffold_ca_python/commands/generate_entry_point.py`
- [ ] T025 [P] [US3] Add `ctx: typer.Context` first parameter and change `--type` to optional with early-exit guard in the `register()` function of `src/scaffold_ca_python/commands/generate_driven_adapter.py`
- [ ] T026 [P] [US3] Add `ctx: typer.Context` first parameter and change `--provider` to optional with early-exit guard in the `register()` function of `src/scaffold_ca_python/commands/generate_pipeline.py`
- [ ] T027 [P] [US3] Add `ctx: typer.Context` first parameter and change `--name` to optional with early-exit guard in the `register()` function of `src/scaffold_ca_python/commands/generate_helper.py`
- [ ] T028 [P] [US3] Add `ctx: typer.Context` first parameter and change `--name` to optional with early-exit guard in the `register()` function of `src/scaffold_ca_python/commands/delete_module.py`; also add `ctx` guard to `src/scaffold_ca_python/commands/validate_structure.py` (no required options — guard outputs help when invoked bare); `update_project.py` requires no change (no required options, already exits cleanly)
- [ ] T029 [US3] Run `uv run pytest tests/commands/ -q` — confirm all US3 no-args tests are green alongside all pre-existing tests

**Checkpoint**: US3 fully functional — root and all subcommands exit 0 with help on no-args invocation.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Linting, typing, coverage gate, and constitution amendment.

- [ ] T030 [P] Run `uv run ruff check src/ tests/ --output-format=concise` — fix any E501/ANN/I001 issues introduced by `ctx: typer.Context` params and `str | None` type annotations
- [ ] T031 [P] Run `uv run mypy src/` — fix any strict-mode issues from `Optional[str]` changes and `ctx` parameter types
- [ ] T032 Run full suite `uv run pytest -q` — confirm ≥405 tests pass (SC-005) and ≥80% coverage gate passes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — blocks US2 Rich markup rendering
- **US1 (Phase 3)**: Depends on Phase 1 only — does NOT depend on Foundational (Phase 2)
- **US2 (Phase 4)**: Depends on Foundational (Phase 2) — requires `rich_markup_mode="rich"`
- **US3 (Phase 5)**: Depends on Phase 1 only; MUST run after US2 for `gep`, `gda`, `gpipe` (those files are touched by both)
- **Polish (Phase 6)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: Independent — only touches `generate_project.py` and `cli.py` (command registration)
- **US2 (P2)**: Depends on Foundational (T002); independent of US1
- **US3 (P3)**: Independent of US1; for `gep`/`gda`/`gpipe` files, MUST run AFTER US2 (those files are already modified by US2)

### Within US3 Implementation

- T021 (cli.py callback) is independent of T022–T028 (different file)
- T022–T028 are all parallel to each other (each touches a different command file)
- All T017–T020 tests can be written in parallel (different test files)

### Parallel Opportunities

```bash
# Phase 3 tests (write in parallel — different test methods/files):
T003, T004, T005

# Phase 4 tests (fully parallel — different test files):
T010, T011, T012

# Phase 4 implementation (parallel after tests written — different files):
T014, T015  # (T013 must come before T014/T015 only if running sequentially)

# Phase 5 tests (parallel — different test files):
T017, T018, T019, T020

# Phase 5 implementation (fully parallel — all different files):
T021, T022, T023, T024, T025, T026, T027, T028

# Phase 6 checks (parallel):
T030, T031
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Verify baseline
2. Skip Phase 2 (not needed for US1)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: `clean-architecture` works, `generate-project` is tombstoned
5. Demo/merge US1 as a standalone breaking change

### Incremental Delivery

1. Phase 1 + Phase 2 → baseline confirmed, Rich mode enabled
2. Phase 3 (US1) → `clean-architecture` live, MVP delivered
3. Phase 4 (US2) → `gep`/`gda`/`gpipe` help enriched
4. Phase 5 (US3) → all commands exit 0 on no-args
5. Phase 6 (Polish) → lint + types + coverage gate

### Summary

| Metric | Value |
|---|---|
| Total tasks | 33 |
| US1 tasks | 7 (T003–T009) |
| US2 tasks | 7 (T010–T016) |
| US3 tasks | 13 (T017–T029) |
| Polish tasks | 3 (T030–T032) |
| Parallel-eligible tasks | 18 (marked [P]) |
| New files | `tests/commands/test_cli.py` |
| Modified source files | `cli.py` + 9 command modules |
| Modified test files | 8 existing + 1 new |
| MVP scope | Phase 3 (US1) alone |
