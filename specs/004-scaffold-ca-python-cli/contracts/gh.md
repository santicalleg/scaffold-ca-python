# Contract: `gh` / `generate-helper`

**Command**: `scaffold gh` (alias: `scaffold generate-helper`)  
**US**: US-7 — Scaffold helper

---

## Purpose

Generates a helper utility class inside `infrastructure/helpers/` and its corresponding test stub. Helpers are shared cross-cutting utilities (logging, metrics, serialisation, etc.) with no business logic.

---

## Signature

```
scaffold gh --name <NAME> [--dry-run]
```

| Flag | Type | Required | Default | Description |
|---|---|---|---|---|
| `--name` | `str` | **Yes** | — | Helper name. Validated: `^[A-Za-z][A-Za-z0-9_]*$` |
| `--dry-run` | `bool` | No | `False` | Preview files without writing any output |

---

## Inputs → Outputs

**Given** `scaffold gh --name DateUtils` (inside a project named `my_project`):

```
src/my_project/infrastructure/helpers/date_utils/
    __init__.py
    date_utils.py              ← empty helper class stub
tests/infrastructure/helpers/date_utils/
    test_date_utils.py
```

**Generated `date_utils.py`** (representative structure):

```python
class DateUtils:
    pass
```

**Dry-run**: prints the file paths and their content to stdout; writes nothing.

---

## Prerequisites

Must be run inside a directory tree that contains a `pyproject.toml` with a `[tool.scaffold-ca-python]` section.

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
| Target directory already exists | `Directory 'src/.../date_utils/' already exists.` | `1` |
| No project root | `No scaffold-ca-python project found. Run 'scaffold ca' first.` | `1` |
