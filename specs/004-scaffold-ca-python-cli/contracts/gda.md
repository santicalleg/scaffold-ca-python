# Contract: `gda` / `generate-driven-adapter`

**Command**: `scaffold gda` (alias: `scaffold generate-driven-adapter`)  
**US**: US-4 — Scaffold driven adapter

---

## Purpose

Generates a driven adapter implementation inside `infrastructure/driven_adapters/` and its test stub. Adapter type determines the template and dependencies added.

---

## Signature

```
scaffold gda --type <TYPE> [--name <NAME>] [--dry-run]
```

| Flag | Type | Required | Default | Description |
|---|---|---|---|---|
| `--type` | `str` | **Yes** | — | Adapter type. One of: `rest-consumer`, `secrets`, `generic` |
| `--name` | `str` | Conditional | — | Required when `--type generic`. Optional for named variants of other types. Validated: `^[A-Za-z][A-Za-z0-9_]*$` |
| `--dry-run` | `bool` | No | `False` | Preview files without writing any output |

---

## Type Behaviour

### `rest-consumer`

Generates an async HTTP client adapter using `httpx`:

```
src/my_project/infrastructure/driven_adapters/rest_consumer/
    __init__.py
    rest_consumer.py           ← async httpx-based adapter
tests/infrastructure/driven_adapters/rest_consumer/
    test_rest_consumer.py
```

### `secrets`

Generates an async secrets-store adapter (provider-agnostic interface):

```
src/my_project/infrastructure/driven_adapters/secrets/
    __init__.py
    secrets_adapter.py
tests/infrastructure/driven_adapters/secrets/
    test_secrets_adapter.py
```

### `generic`

`--name` is **required**. Generates an empty async adapter with the given name:

```
src/my_project/infrastructure/driven_adapters/<name>/
    __init__.py
    <name>_adapter.py
tests/infrastructure/driven_adapters/<name>/
    test_<name>_adapter.py
```

---

## Dry-Run

Prints all file paths and their content to stdout; writes nothing.

---

## Prerequisites

Must be run inside a directory tree that contains a `pyproject.toml` with a `[tool.scaffold-ca-python]` section.

---

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Files created (or dry-run completed) successfully |
| `1` | Validation error |
| `2` | Internal/unexpected error |

---

## Errors

| Condition | Message | Exit |
|---|---|---|
| `--type` is not one of the allowed values | `Unknown type 'X'. Allowed: rest-consumer, secrets, generic.` | `1` |
| `--type generic` without `--name` | `--name is required when --type is generic.` | `1` |
| `--name` fails regex | `Name 'X' is invalid. Use letters, digits, underscores; must start with a letter.` | `1` |
| Target directory already exists | `Directory 'src/.../rest_consumer/' already exists.` | `1` |
| No project root | `No scaffold-ca-python project found. Run 'scaffold ca' first.` | `1` |
