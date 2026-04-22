# Research: PEP 8 / PEP 423 Naming Validation

**Phase**: 0 — Research  
**Feature**: 017-pep8-naming-validation  
**Date**: 2026-04-15

---

## Decision 1: Valid `--name` pattern (kebab-case + snake_case)

**Decision**: Accept names matching `^[a-z][a-z0-9]*([_-][a-z0-9]+)*$`  
**Rationale**:
- PEP 423 (packaging best practice) recommends lowercase letters with hyphens for distribution names (e.g., `my-project`).
- PEP 8 mandates lowercase letters with underscores for Python module/package names (e.g., `my_project`).
- Both are valid for user input; internally hyphens are normalised to underscores before use as Python identifiers.
- Names must start with a letter (Python identifier rule) and must not have consecutive separators, leading/trailing separators, or any uppercase character.

**Alternatives considered**:
- Allow PascalCase/CamelCase at input and auto-convert silently → rejected because it hides intent and leads to surprising output (`MyOrder` silently becomes `my_order`).
- Accept any non-empty ASCII string → rejected; too permissive, breaks Python import paths.

---

## Decision 2: Where to enforce the new validation rule

**Decision**: Enforce in `src/scaffold_ca_python/core/name_utils.py` (`validate_name`) **and** in `src/scaffold_ca_python/models/context.py` (`_NAME_RE` + validators).  
**Rationale**:
- `name_utils.validate_name` is called directly by every command module (`generate_project.py`, `generate_use_case.py`, `generate_helper.py`, `generate_driven_adapter.py`, `delete_module.py`).
- `context.py` `ProjectContext` and `ModuleContext` have their own inline `_NAME_RE` and validators — these are the last defence before a name reaches Jinja2 templates. Both must be updated for defence-in-depth.
- Keeping both in sync is acceptable because they serve different layers (CLI validation vs. model validation).

**Alternatives considered**:
- Update only `context.py` and remove the command-level `validate_name` call → rejected; commands would silently pass invalid names through until Pydantic raises a Pydantic `ValueError` with a less user-friendly message.
- Extract validation into a shared Pydantic type → valid long-term refactor but out of scope for this feature; defer.

---

## Decision 3: `to_snake_case` must normalise hyphens

**Decision**: Update `to_snake_case` in **both** `name_utils.py` and `context.py` to replace hyphens with underscores **before** other transformations.  
**Rationale**:
- User input of `my-project` (kebab-case) must produce the Python package name `my_project`.
- Current implementation only strips CamelCase boundaries; `my-project` would remain `my-project` (invalid Python identifier).
- Adding `name.replace("-", "_")` as the first step makes conversion idempotent and safe.

**Alternatives considered**:
- Handle the replacement in each command instead of in the utility → rejected; DRY violation and easy to miss in future commands.

---

## Decision 4: `to_pascal_case` must split on hyphens

**Decision**: Update `_to_pascal_case` in `context.py` to split on `[_\s-]+` (add `-`).  
**Rationale**:
- If `my-project` reaches `_to_pascal_case` before normalisation (e.g., via `ProjectContext.name`), splitting on hyphens produces correct PascalCase: `MyProject`.
- The `to_pascal_case` in `name_utils.py` only splits on underscores. After the hyphen-normalisation step in `to_snake_case`, this is fine; but for defence-in-depth the context-level helper should also handle hyphens.

---

## Decision 5: Update `test_validate_name_rejects_hyphens` test

**Decision**: The existing test `test_validate_name_rejects_hyphens` asserts that `validate_name("my-project")` raises `ScaffoldError`. After this feature, hyphenated names are valid. The test must be renamed and inverted.  
**Rationale**: The feature explicitly makes `kebab-case` a first-class accepted format. The old test encodes the opposite behaviour and must be updated.

**Impact**: Other existing tests for `validate_name` that check PascalCase acceptance (e.g., `test_validate_name_accepts_pascal_case`) must also be updated — PascalCase is now **rejected**.

---

## Decision 6: Error message wording

**Decision**: Error message: `"Invalid name {name!r}. Use kebab-case (e.g., 'my-project') or snake_case (e.g., 'my_project')."`  
**Rationale**:
- FR-002 requires the message to explicitly mention both formats.
- Providing concrete examples reduces ambiguity.
- Matching the exact wording in tests makes assertions stable.

---

## Decision 7: No new files needed — modify existing utilities

**Decision**: This feature modifies only:
1. `src/scaffold_ca_python/core/name_utils.py` — regex + `to_snake_case` + error message
2. `src/scaffold_ca_python/models/context.py` — `_NAME_RE` + `_to_snake_case` + `_to_pascal_case`
3. `tests/core/test_name_utils.py` — updated + new test cases

**Rationale**: The command modules (`generate_*.py`, `delete_module.py`) already call `validate_name` and `to_snake_case` correctly — no changes needed there once the utilities are fixed. Template files already use `class_name` (computed PascalCase) and `module_name` (computed snake_case) — no template changes needed.
