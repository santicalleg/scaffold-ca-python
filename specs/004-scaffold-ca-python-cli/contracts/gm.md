# Contract: `gm` / `generate-model`

**Command**: `scaffold gm` (alias: `scaffold generate-model`)  
**US**: US-2 — Scaffold domain model

---

## Purpose

Generates a Pydantic v2 domain model class inside `domain/model/` and its corresponding test stub.

---

## Signature

```
scaffold gm --name <NAME> [--dry-run]
```

| Flag | Type | Required | Default | Description |
|---|---|---|---|---|
| `--name` | `str` | **Yes** | — | Model name. Validated: `^[A-Za-z][A-Za-z0-9_]*$` |
| `--dry-run` | `bool` | No | `False` | Preview files without writing any output |

---

## Inputs → Outputs

**Given** `scaffold gm --name Order` (inside a project named `my_project`):

```
src/my_project/domain/model/order.py       ← Pydantic v2 BaseModel subclass
tests/domain/model/test_order.py           ← pytest stub
```

**Generated `order.py`** (representative structure):

```python
from pydantic import BaseModel


class Order(BaseModel):
    pass
```

**Dry-run**: prints the two file paths and their content to stdout; writes nothing.

---

## Prerequisites

Must be run inside a directory tree that contains a `pyproject.toml` with a `[tool.scaffold-ca-python]` section.  
Error if no project root is found.

---

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Files created (or dry-run completed) successfully |
| `1` | Validation error (invalid name, files already exist, no project root found) |
| `2` | Internal/unexpected error |

---

## Errors

| Condition | Message | Exit |
|---|---|---|
| `--name` fails regex | `Name 'X' is invalid. Use letters, digits, underscores; must start with a letter.` | `1` |
| Target files already exist | `File 'src/.../order.py' already exists. Use --force to overwrite.` | `1` |
| No project root | `No scaffold-ca-python project found. Run 'scaffold ca' first.` | `1` |
