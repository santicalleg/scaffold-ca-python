# Tasks: Deduplicate Command + Alias Function Bodies

**Input**: Design documents from `/specs/016-dedup-command-aliases/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on each other)
- **[US1]**: Belongs to User Story 1 — one shared handler per `register()`
- **[US2]**: Belongs to User Story 2 — establish and verify the alias convention

---

## Phase 1: Setup

**Purpose**: Record a clean baseline before any source change.

- [X] T001 Run `uv run pytest --ignore=tests/performance --no-cov -q` and record total pass count as the regression baseline

**Checkpoint**: Baseline recorded — refactoring can begin.

---

## Phase 2: User Story 1 — One Function Body Per Module (Priority: P1) 🎯 MVP

**Goal**: Each of the 6 affected `register()` functions contains exactly one inner function definition, registered under both the long-form name and the short alias via stacked `@app.command(...)` decorators.

**Pattern** (from `research.md`):
```python
# Replace this:
@app.command("generate-model", help="...", epilog="...")
def generate_model(ctx, name, dry_run): ...

@app.command("gm", hidden=True, help="Alias for generate-model.")
def gm(ctx, name, dry_run): ...   # ← identical body, DELETE this

# With this:
@app.command("generate-model", help="...", epilog="...")
@app.command("gm", hidden=True)           # ← stack alias here
def generate_model(ctx, name, dry_run): ...   # ← single body
```

**Independent Test**: `grep -c "def " <(grep -A100 "def register" <file.py> | head -50)` returns `1` for each module; existing test suite passes with no regressions.

### Simple modules (identical 141-line structure)

- [X] T002 [P] [US1] Refactor `generate_model.py`: add `@app.command("gm", hidden=True)` between the existing long-form decorator and `def generate_model(...)`, then delete the entire `@app.command("gm", ...) / def gm(...)` block in `src/scaffold_ca_python/commands/generate_model.py`; add a one-line comment above the stacked decorators inside `register()` — e.g. `# Both names route to the same handler; add further aliases by stacking @app.command before the def.` — to make the convention discoverable (US2)
- [X] T003 [P] [US1] Refactor `generate_use_case.py`: add `@app.command("guc", hidden=True)` between the existing long-form decorator and `def generate_use_case(...)`, then delete the entire `@app.command("guc", ...) / def guc(...)` block in `src/scaffold_ca_python/commands/generate_use_case.py`
- [X] T004 [P] [US1] Refactor `generate_helper.py`: add `@app.command("gh", hidden=True)` between the existing long-form decorator and `def generate_helper(...)`, then delete the entire `@app.command("gh", ...) / def gh(...)` block in `src/scaffold_ca_python/commands/generate_helper.py`

### Complex modules (additional module-level helpers — same inner-function duplicate pattern)

- [X] T005 [P] [US1] Refactor `generate_driven_adapter.py`: add `@app.command("gda", hidden=True)` between the existing long-form decorator and `def generate_driven_adapter(...)`, then delete the entire `@app.command("gda", ...) / def gda(...)` block in `src/scaffold_ca_python/commands/generate_driven_adapter.py`
- [X] T006 [P] [US1] Refactor `generate_entry_point.py`: add `@app.command("gep", hidden=True)` between the existing long-form decorator and `def generate_entry_point(...)`, then delete the entire `@app.command("gep", ...) / def gep(...)` block in `src/scaffold_ca_python/commands/generate_entry_point.py`
- [X] T007 [P] [US1] Refactor `delete_module.py`: add `@app.command("dm", hidden=True)` between the existing long-form decorator and `def delete_module(...)`, then delete the entire `@app.command("dm", ...) / def dm(...)` block in `src/scaffold_ca_python/commands/delete_module.py`

### Regression verification

- [X] T008 [US1] Run `grep -r '"gm"\|"guc"\|"gh"\|"gep"\|"gda"\|"dm"' tests/` and confirm alias forms appear in at least one test per alias (SC-003 coverage check); then run `uv run pytest --ignore=tests/performance --no-cov -q` and confirm pass count matches T001 baseline — zero regressions

**Checkpoint**: All 6 modules have a single inner function. Both long-form name and alias route identically.

---

## Phase 3: User Story 2 — Convention Consistency (Priority: P2)

**Goal**: The stacked `@app.command` pattern is demonstrably uniform across all 6 modules so a new contributor can follow it by imitation.

**Independent Test**: `grep -n "def " src/scaffold_ca_python/commands/generate_model.py` (and 5 others) each show exactly one `def` inside the `register()` body; the short-alias decorator always immediately precedes the long-form handler's `def`.

- [X] T009 [US2] Verify convention consistency: run `grep -n "@app.command\|def " src/scaffold_ca_python/commands/generate_model.py src/scaffold_ca_python/commands/generate_use_case.py src/scaffold_ca_python/commands/generate_helper.py src/scaffold_ca_python/commands/generate_entry_point.py src/scaffold_ca_python/commands/generate_driven_adapter.py src/scaffold_ca_python/commands/delete_module.py` and confirm each module shows the pattern inside `register()`: long-form `@app.command("generate-...")` first (outermost), alias `@app.command("<short>", hidden=True)` second (innermost, directly above `def`), then a single `def` — decorator order is significant and must be visually confirmed

**Checkpoint**: Convention is visually consistent. A contributor extending any module has a clear model to follow.

---

## Phase 4: Polish & Quality Gates

**Purpose**: Confirm all linting, type-checking, and coverage gates pass after the refactor.

- [X] T010 [P] Run `uv run ruff check src/` — confirm zero lint errors introduced by the refactor
- [X] T011 [P] Run `uv run mypy src/` — confirm zero type errors (strict mode)
- [X] T012 Run `uv run pytest --ignore=tests/performance -q` — confirm ≥80% line-coverage gate and full test suite green; then run `wc -l src/scaffold_ca_python/commands/generate_model.py src/scaffold_ca_python/commands/generate_use_case.py src/scaffold_ca_python/commands/generate_helper.py src/scaffold_ca_python/commands/generate_entry_point.py src/scaffold_ca_python/commands/generate_driven_adapter.py src/scaffold_ca_python/commands/delete_module.py` and confirm total is below the 1132-line baseline (SC-004)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **User Story 1 (Phase 2)**: Depends on Phase 1 baseline; T002–T007 can all run in parallel; T008 depends on T002–T007 all completing
- **User Story 2 (Phase 3)**: Depends on Phase 2 completion (T008 green)
- **Polish (Phase 4)**: Depends on Phase 3; T010/T011 can run in parallel; T012 depends on T010+T011

### Within User Story 1

```
T001 (baseline)
  └─ T002–T007 (parallel: 6 independent file edits)
       └─ T008 (regression gate — depends on all 6)
```

### Parallel Opportunities

All of T002–T007 target different files with no shared state. They can be executed simultaneously by 6 agents/developers or sequentially in any order.

```bash
# All 6 refactors can launch together:
Task: "Refactor generate_model.py"
Task: "Refactor generate_use_case.py"
Task: "Refactor generate_helper.py"
Task: "Refactor generate_driven_adapter.py"
Task: "Refactor generate_entry_point.py"
Task: "Refactor delete_module.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup baseline
2. Complete Phase 2: Refactor all 6 modules + verify regression
3. **STOP and VALIDATE**: `grep` confirms single inner `def` per module; tests green
4. Move to Phase 3 + 4 for convention sign-off and quality gates

### Incremental Delivery (if preferred)

1. Refactor simple modules (T002–T004) → run T008 → validate 3 of 6 clean
2. Refactor complex modules (T005–T007) → run T008 → validate remaining 3
3. Convention check + quality gates

---

## Notes

- Do **not** modify any file under `tests/` — FR-005 prohibits test file changes
- Keep the long-form `@app.command("generate-model", help="...", epilog="...")` as the OUTER decorator; the alias `@app.command("gm", hidden=True)` goes INNER (directly above `def`)
- No new files are created; no template files are touched
- `SC-004` (total lines decrease) is a consequence of the refactor, not a task
