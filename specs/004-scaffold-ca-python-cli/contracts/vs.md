# Contract: `vs` / `validate-structure`

**Command**: `scaffold vs` (alias: `scaffold validate-structure`)  
**US**: US-6 — Validate structure

---

## Purpose

Scans every `.py` file under `src/` in the current project and reports any import that violates Clean Architecture dependency rules (outer layers must not be imported by inner layers).

---

## Signature

```
scaffold vs [--dry-run]
```

| Flag | Type | Required | Default | Description |
|---|---|---|---|---|
| `--dry-run` | `bool` | No | `False` | Run the scan and print results but exit with code `0` regardless of violations |

> `vs` has no required flags. Detection is fully automatic from the project structure.

---

## Dependency Rules Enforced

```
ALLOWED DIRECTION (inward only):
  application  →  domain/*
  entry_points →  domain/*
  driven_adapters → domain/*
  helpers      →  domain/*
  domain/usecase → domain/model

FORBIDDEN (any import going outward):
  domain/model    → ANYTHING outside domain/model
  domain/usecase  → infrastructure/**
  domain/*        → application
```

---

## Output

### Clean run (no violations)

```
✓ Validated 42 files — no violations found.
```

### Violations found

```
✗ 2 violation(s) found:

  src/my_project/domain/model/order.py:12
    from my_project.infrastructure.driven_adapters.rest_consumer import ...
    domain/model must not import from infrastructure/driven-adapters
    Hint: Define a port interface in domain/model and inject the adapter.

  src/my_project/domain/usecase/create_order.py:4
    from my_project.application import config
    domain/usecase must not import from application
    Hint: Pass configuration as a constructor argument instead.
```

---

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | No violations (or `--dry-run` set) |
| `1` | One or more violations found |
| `2` | Internal/unexpected error (e.g. parse failure on malformed Python) |

---

## Errors

| Condition | Message | Exit |
|---|---|---|
| No project root | `No scaffold-ca-python project found. Run 'scaffold ca' first.` | `1` |
| `src/` directory not found | `Could not locate src/ under project root.` | `1` |
| Malformed `.py` file (SyntaxError) | `Warning: could not parse 'X' — skipping` (non-fatal, printed but scan continues) | — |
