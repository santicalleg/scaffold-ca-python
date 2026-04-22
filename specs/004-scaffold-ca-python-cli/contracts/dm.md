# Contract: `dm` / `delete-module`

**Command**: `scaffold dm` (alias: `scaffold delete-module`)  
**US**: US-9 — Delete module

---

## Purpose

Safely removes a previously generated module (and its test mirror) from the project. Performs a dry-run by default to prevent accidental deletion; actual deletion requires explicit `--confirm`.

---

## Signature

```
scaffold dm --name <NAME> [--confirm] [--dry-run]
```

| Flag | Type | Required | Default | Description |
|---|---|---|---|---|
| `--name` | `str` | **Yes** | — | Name of the module to delete. Validated: `^[A-Za-z][A-Za-z0-9_]*$` |
| `--confirm` | `bool` | No | `False` | Actually perform the deletion. Without this flag, behaves as dry-run regardless. |
| `--dry-run` | `bool` | No | `False` | Explicitly preview what would be deleted; no-op if `--confirm` is not set (same behaviour as default). |

> **Safety default**: without `--confirm`, `dm` always operates in preview mode and prints what would be deleted without touching the filesystem.

---

## Behaviour

### Without `--confirm` (default / dry-run)

```
The following files would be deleted:

  src/my_project/domain/model/order.py
  tests/domain/model/test_order.py

Run with --confirm to proceed.
```

### With `--confirm`

```
Deleted:
  ✓ src/my_project/domain/model/order.py
  ✓ tests/domain/model/test_order.py
```

### Module discovery

The command searches for a module matching `--name` across all layers:

1. `domain/model/<name>.py`
2. `domain/usecase/<name>.py`
3. `infrastructure/driven_adapters/<name>/`
4. `infrastructure/entry_points/<name>/`
5. `infrastructure/helpers/<name>/`

If multiple matches are found, the user is prompted to confirm which one to delete (interactive disambiguation).

---

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Deletion completed (or dry-run/preview completed) successfully |
| `1` | Validation error (invalid name, module not found, no project root) |
| `2` | Internal/unexpected error |

---

## Errors

| Condition | Message | Exit |
|---|---|---|
| `--name` fails regex | `Name 'X' is invalid. Use letters, digits, underscores; must start with a letter.` | `1` |
| No matching module found | `No module named 'order' found in project.` | `1` |
| No project root | `No scaffold-ca-python project found. Run 'scaffold ca' first.` | `1` |
