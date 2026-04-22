# Implementation Plan: PEP 8 / PEP 423 Naming Validation

**Branch**: `017-pep8-naming-validation` | **Date**: 2026-04-15 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/017-pep8-naming-validation/spec.md`

## Summary

Tighten the `--name` validation rule across all scaffold commands to accept only `kebab-case` and `snake_case` input (rejecting PascalCase/CamelCase), normalise `kebab-case` to `snake_case` internally, and guarantee that generated module file names are always `snake_case` and generated class names are always `PascalCase`. Changes are confined to `name_utils.py`, `context.py`, and their tests — no command modules or templates require modification.

## Technical Context

**Language/Version**: Python 3.13+  
**Primary Dependencies**: typer ≥ 0.16, pydantic ≥ 2.0, rich ≥ 14.1, jinja2 ≥ 3.1  
**Storage**: N/A (file generation only)  
**Testing**: pytest + pytest-cov (≥ 80% coverage gate), mypy strict, ruff  
**Target Platform**: macOS / Linux CLI (uv-managed)  
**Project Type**: CLI tool / library  
**Performance Goals**: No change — validation is pure regex, negligible cost  
**Constraints**: No new dependencies; no breaking changes to `to_snake_case` / `to_pascal_case` for existing valid snake_case inputs  
**Scale/Scope**: 2 source files, 1 test file, ~15 test cases added/modified

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Clean Architecture (generated projects) | ✅ PASS | No generated project structure changes |
| II. Template-Driven Code Generation | ✅ PASS | No template changes; templates already use `class_name` / `module_name` computed fields |
| III. Full Command Parity | ✅ PASS | All required commands unchanged; only their `--name` validation tightened |
| IV. Python-First Idioms (ruff, mypy strict, type hints) | ✅ PASS | All changes in existing files; must pass ruff + mypy strict |
| V. Test-First Development | ✅ PASS | Tests written before implementation (TDD enforced per constitution) |
| VI. (Other principles) | ✅ PASS | No violations identified |

**Post-design re-check**: No new violations introduced by data-model.md or contracts/.

## Project Structure

### Documentation (this feature)

```text
specs/017-pep8-naming-validation/
├── plan.md              ← this file
├── research.md          ← Phase 0 output (complete)
├── data-model.md        ← Phase 1 output (complete)
├── contracts/
│   └── name-validation.md   ← Phase 1 output (complete)
└── tasks.md             ← Phase 2 output (created by /speckit.tasks)
```

### Source Code (modified files only)

```text
src/scaffold_ca_python/
├── core/
│   └── name_utils.py        ← MODIFY: validate_name regex + error msg; to_snake_case handles hyphens
└── models/
    └── context.py            ← MODIFY: _NAME_RE + _to_snake_case + _to_pascal_case

tests/
├── core/
│   └── test_name_utils.py          ← MODIFY: update inverted test; add kebab-case + rejection tests
└── commands/
    ├── test_generate_project.py    ← MODIFY: replace PascalCase --name values (T006a)
    ├── test_generate_use_case.py   ← MODIFY: replace PascalCase --name values (T006b)
    ├── test_generate_model.py      ← MODIFY: replace PascalCase + add rejection/PascalCase tests (T005, T006b, T014)
    ├── test_generate_helper.py     ← MODIFY: replace PascalCase --name values (T006b)
    ├── test_generate_driven_adapter.py  ← MODIFY: replace PascalCase --name values (T006c)
    ├── test_generate_entry_point.py     ← MODIFY: replace PascalCase --name values (T006c)
    ├── test_delete_module.py            ← MODIFY: replace PascalCase --name values (T006c)
    ├── test_dry_run_checksum.py         ← MODIFY: replace PascalCase --name values (T006d)
    ├── test_workflow.py                 ← MODIFY: replace PascalCase --name values (T006d)
    └── test_validate_structure.py       ← MODIFY: replace PascalCase --name values (T006d)
```

**110 existing test invocations** across 13 command test files pass PascalCase `--name` values and must be migrated (T006a–T006d) before the regex in `name_utils.py` / `context.py` is tightened.

## Complexity Tracking

No constitution violations. No complexity justification required.

---

## Implementation Phases

> **Note**: Task IDs in this section (T001–T006) are design-phase labels only. For authoritative, executable IDs refer to [tasks.md](tasks.md) (T001–T018).

### Phase 1 — Tests first (TDD: Red)

**T001 — Update `test_name_utils.py`**: modify the existing `test_validate_name_rejects_hyphens` test to assert acceptance, and add the following new test cases:

| Test name | Input | Expected |
|-----------|-------|----------|
| `test_validate_name_accepts_kebab_case` | `"my-project"` | returns `"my-project"` |
| `test_validate_name_accepts_single_word` | `"order"` | returns `"order"` |
| `test_validate_name_accepts_multi_word_kebab` | `"my-order-service"` | returns `"my-order-service"` |
| `test_validate_name_rejects_pascal_case` | `"MyProject"` | raises `ScaffoldError` mentioning `kebab-case` |
| `test_validate_name_rejects_camel_case` | `"myProject"` | raises `ScaffoldError` mentioning `kebab-case` |
| `test_validate_name_rejects_mixed_case_with_hyphen` | `"My-Project"` | raises `ScaffoldError` |
| `test_validate_name_rejects_consecutive_hyphens` | `"my--project"` | raises `ScaffoldError` |
| `test_validate_name_rejects_leading_hyphen` | `"-myproject"` | raises `ScaffoldError` |
| `test_validate_name_rejects_trailing_underscore` | `"myproject_"` | raises `ScaffoldError` |
| `test_to_snake_case_from_kebab` | `"my-project"` | `"my_project"` |
| `test_to_snake_case_multi_word_kebab` | `"my-order-service"` | `"my_order_service"` |
| (existing `test_validate_name_accepts_pascal_case`) | `"MyProject"` | **invert** → raises `ScaffoldError` |

Also add integration-level assertions to `tests/commands/test_generate_project.py` (and at least one other command test) that `scaffold ca --name MyProject` exits 1 with a message containing `kebab-case`.

### Phase 2 — Implementation (TDD: Green)

**T002 — `src/scaffold_ca_python/core/name_utils.py`**:

1. Replace `_NAME_RE`:
   ```python
   _NAME_RE = re.compile(r"^[a-z][a-z0-9]*([_-][a-z0-9]+)*$")
   ```
2. Update `validate_name` error message:
   ```python
   raise ScaffoldError(
       f"Invalid name {name!r}. "
       "Use kebab-case (e.g., 'my-project') or snake_case (e.g., 'my_project')."
   )
   ```
3. Prepend hyphen normalisation in `to_snake_case`:
   ```python
   def to_snake_case(name: str) -> str:
       name = name.replace("-", "_")
       s = _CAMEL_BOUNDARY_RE.sub("_", name)
       return s.lower()
   ```

**T003 — `src/scaffold_ca_python/models/context.py`**:

1. Replace `_NAME_RE`:
   ```python
   _NAME_RE = re.compile(r"^[a-z][a-z0-9]*([_-][a-z0-9]+)*$")
   ```
2. Update both `_validate_name` validators to use the new error message wording.
3. Update `_to_snake_case` to prepend `name = name.replace("-", "_")`.
4. Update `_to_pascal_case` to split on hyphens: `re.split(r"[_\s-]+", name)`.

### Phase 3 — Quality gates (TDD: Refactor + Green gates)

**T004 — ruff**: `uv run ruff check src/ tests/` — must report no new violations.

**T005 — mypy**: `uv run mypy src/` — must report no new errors (strict mode).

**T006 — pytest**: `uv run pytest --ignore=tests/performance` — must reach ≥ 80% coverage; all previously passing tests must still pass; all new tests must pass.

---

## Acceptance Verification

| Check | Command | Expected |
|-------|---------|----------|
| Kebab-case accepted | `scaffold ca --name my-project --dry-run` | exit 0, no error |
| Snake-case accepted | `scaffold ca --name my_project --dry-run` | exit 0, no error |
| PascalCase rejected | `scaffold ca --name MyProject` | exit 1, message contains `kebab-case` |
| Generated file is snake_case | inspect dry-run output for `my-project` | all `.py` names are `[a-z_]+.py` |
| Generated class is PascalCase | inspect dry-run output for `my-project` | `class MyProject` appears |