# Contract: `guc` / `generate-use-case`

**Command**: `scaffold guc` (alias: `scaffold generate-use-case`)  
**US**: US-3 — Scaffold use case

---

## Purpose

Generates an async use case class inside `domain/usecase/` and its corresponding test stub.

---

## Signature

```
scaffold guc --name <NAME> [--dry-run]
```

| Flag | Type | Required | Default | Description |
|---|---|---|---|---|
| `--name` | `str` | **Yes** | — | Use case name. Validated: `^[A-Za-z][A-Za-z0-9_]*$` |
| `--dry-run` | `bool` | No | `False` | Preview files without writing any output |

---

## Inputs → Outputs

**Given** `scaffold guc --name CreateOrder` (inside a project named `my_project`):

```
src/my_project/domain/usecase/create_order.py   ← async use case class
tests/domain/usecase/test_create_order.py        ← pytest stub
```

**Generated `create_order.py`** (representative structure):

```python
class CreateOrderUseCase:
    async def execute(self) -> None:
        raise NotImplementedError
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
| Target files already exist | `File 'src/.../create_order.py' already exists. Use --force to overwrite.` | `1` |
| No project root | `No scaffold-ca-python project found. Run 'scaffold ca' first.` | `1` |
