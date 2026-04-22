# Data Model: PEP 8 / PEP 423 Naming Validation

**Phase**: 1 — Design  
**Feature**: 017-pep8-naming-validation  
**Date**: 2026-04-15

---

## Naming Convention Rules

### ValidNamePattern

The single regex that defines an accepted `--name` value:

```
^[a-z][a-z0-9]*([_-][a-z0-9]+)*$
```

| Input | Valid? | Reason |
|-------|--------|--------|
| `my-project` | ✅ | kebab-case |
| `my_project` | ✅ | snake_case |
| `order` | ✅ | single word, lowercase |
| `my-order-service` | ✅ | kebab-case, multi-word |
| `my_order_service` | ✅ | snake_case, multi-word |
| `a` | ✅ | single character, lowercase |
| `project2025` | ✅ | alphanumeric, no separator |
| `MyProject` | ❌ | PascalCase — uppercase present |
| `myProject` | ❌ | camelCase — uppercase present |
| `my--project` | ❌ | consecutive hyphens |
| `my__project` | ❌ | consecutive underscores |
| `-myproject` | ❌ | starts with separator |
| `myproject-` | ❌ | ends with separator |
| `1-2-3` | ❌ | starts with digit |
| `my@project` | ❌ | special character |
| `` (empty) | ❌ | empty string |

---

## Name Transformation Pipeline

```
User input (--name)
       │
       ▼
validate_name(name)          ← name_utils.py
  regex: ValidNamePattern
  error: "Use kebab-case or snake_case"
       │
       ▼
to_snake_case(name)          ← name_utils.py
  1. replace("-", "_")
  2. apply CamelCase boundary rules (legacy path)
  3. .lower()
  → Python-safe module name (e.g., "my_project")
       │
       ├──────────────────────────────────────┐
       ▼                                      ▼
  module file path                    ProjectContext(name=...)
  e.g., my_project/                   → python_package = _to_snake_case(name)
        my_project/__init__.py        → used in templates as {{ project.python_package }}
       │
       ▼
  ModuleContext(name=...)
  → module_name = _to_snake_case(name)   ← snake_case file stem
  → class_name  = _to_pascal_case(name)  ← PascalCase class name
```

---

## Affected Entities

### `name_utils.py` — `validate_name(name: str) -> str`

| Attribute | Before | After |
|-----------|--------|-------|
| Accepted pattern | `^[A-Za-z][A-Za-z0-9_]*$` | `^[a-z][a-z0-9]*([_-][a-z0-9]+)*$` |
| Accepts PascalCase | ✅ | ❌ |
| Accepts kebab-case | ❌ | ✅ |
| Accepts snake_case | ✅ | ✅ (subset of new pattern) |
| Error message | generic identifier hint | mentions kebab-case and snake_case explicitly |

### `name_utils.py` — `to_snake_case(name: str) -> str`

| Attribute | Before | After |
|-----------|--------|-------|
| Input `my-project` | `my-project` (unchanged — invalid Python id) | `my_project` |
| Input `my_project` | `my_project` | `my_project` |
| Input `MyOrder` | `my_order` | `my_order` (unchanged behaviour) |

Change: prepend `name = name.replace("-", "_")` before existing logic.

### `context.py` — `_NAME_RE`

| Attribute | Before | After |
|-----------|--------|-------|
| Pattern | `^[A-Za-z][A-Za-z0-9_]*$` | `^[a-z][a-z0-9]*([_-][a-z0-9]+)*$` |

### `context.py` — `_to_snake_case(name: str) -> str`

Add `name = name.replace("-", "_")` as the first step.

### `context.py` — `_to_pascal_case(name: str) -> str`

Change `re.split(r"[_\s]+", name)` → `re.split(r"[_\s-]+", name)` to split on hyphens too.

---

## State Transitions (name input lifecycle)

```
"my-project"  ──validate──▶  accepted
              ──to_snake──▶  "my_project"
              ──to_pascal─▶  "MyProject"

"MyProject"   ──validate──▶  ERROR (exit 1)
                             "Use kebab-case (e.g., 'my-project') or snake_case (e.g., 'my_project')"

"my_project"  ──validate──▶  accepted
              ──to_snake──▶  "my_project"
              ──to_pascal─▶  "MyProject"
```
