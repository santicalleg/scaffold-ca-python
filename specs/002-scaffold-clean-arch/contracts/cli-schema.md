# CLI Contract: scaffold-ca-python

**Branch**: `002-scaffold-clean-arch` | **Date**: 2026-03-25  
**Tool name**: `scaffold` (entry point: `scaffold-ca-python`)

This document defines the complete public command surface of the tool. It is the contract that tests, documentation, and users depend on.

---

## Global Flags

All commands accept the following global flags:

| Flag | Type | Default | Description |
|---|---|---|---|
| `--quiet` / `-q` | bool | False | Suppress informational output; show only errors |
| `--verbose` / `-v` | bool | False | Show debug-level output (file paths, template selections, normalizations) |
| `--version` | bool | — | Print tool version and exit |
| `--help` | bool | — | Show help and exit |

---

## Commands

### `scaffold new`

Generate a new Clean Architecture project.

```
scaffold new --name <name> [--package <package>] [--async] [--force]
```

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `--name` | str | ✅ | — | Project name (normalized to snake_case) |
| `--package` | str | ➖ | `<name>` | Python namespace; last dot-segment used as root package dir |
| `--async` | bool | ➖ | False | Generate async-mode stubs (`asyncio`-compatible) |
| `--force` | bool | ➖ | False | Overwrite if target directory already exists |

**Exit codes**: `0` success, `1` validation error (name invalid, dir exists without `--force`).

---

### `scaffold generate`

Parent command — no-op without subcommand; shows help.

#### `scaffold generate model`

```
scaffold generate model --name <name> [--force]
```

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `--name` | str | ✅ | — | Entity name (PascalCase or snake_case; normalized) |
| `--force` | bool | ➖ | False | Overwrite existing files |

**Generated files**:
- `<pkg>/domain/model/<name>.py` — entity dataclass stub
- `<pkg>/domain/model/gateways/<name>_gateway.py` — gateway interface (port) stub
- `tests/unit/model/test_<name>.py` — test stub

---

#### `scaffold generate use-case`

```
scaffold generate use-case --name <name> [--force]
```

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `--name` | str | ✅ | — | Use case name (e.g. `ProcessOrder`) |
| `--force` | bool | ➖ | False | Overwrite existing files |

**Generated files**:
- `<pkg>/domain/usecase/<name>_use_case.py`
- `tests/unit/usecase/test_<name>_use_case.py`

---

#### `scaffold generate driven-adapter`

```
scaffold generate driven-adapter --type <type> --name <name> [--force] [type-specific options]
```

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `--type` | enum | ✅ | — | Adapter type (see table below) |
| `--name` | str | ✅ (generic) | — | Adapter name; auto-derived for typed adapters |
| `--force` | bool | ➖ | False | Overwrite existing files |

**Type-specific options**:

| Type | Extra option | Type | Default | Description |
|---|---|---|---|---|
| `rest-client` | `--url` | str | — | Base URL for the HTTP client stub |
| `redis` | `--mode` | `template\|repository` | `template` | Redis access pattern |
| `kafka-sender` | `--tech` | `kafka\|rabbitmq\|both` | `kafka` | Messaging technology |
| `rabbitmq-sender` | `--tech` | same | `rabbitmq` | Messaging technology |

**Supported types**: `generic`, `repository`, `rest-client`, `mongodb`, `redis`, `dynamo`, `s3`, `sqs-sender`, `kafka-sender`, `rabbitmq-sender`, `secrets`

**Generated files** (example for `repository`):
- `<pkg>/domain/model/gateways/<name>_repository.py` — gateway interface (if absent)
- `<pkg>/infrastructure/driven_adapters/<name>/<name>_adapter.py` — adapter stub
- `tests/unit/driven_adapters/test_<name>_adapter.py`

---

#### `scaffold generate entry-point`

```
scaffold generate entry-point --type <type> --name <name> [--force] [type-specific options]
```

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `--type` | enum | ✅ | — | Entry-point type (see table below) |
| `--name` | str | ✅ | — | Entry-point name |
| `--force` | bool | ➖ | False | Overwrite existing files |

**Type-specific options**:

| Type | Extra option | Type | Default | Description |
|---|---|---|---|---|
| `async-event-handler` | `--tech` | `rabbitmq\|kafka\|both` | `rabbitmq` | Message broker technology |

**Supported types**: `generic`, `rest-api`, `graphql`, `kafka-consumer`, `sqs-listener`, `async-event-handler`, `cli`

**Generated files** (example for `rest-api`):
- `<pkg>/infrastructure/entry_points/<name>/router.py`
- `<pkg>/infrastructure/entry_points/<name>/handler.py`
- `tests/unit/entry_points/test_<name>_handler.py`

---

#### `scaffold generate helper`

```
scaffold generate helper --name <name> [--force]
```

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `--name` | str | ✅ | — | Helper name |
| `--force` | bool | ➖ | False | Overwrite existing files |

**Generated files**:
- `<pkg>/infrastructure/helpers/<name>_helper.py`
- `tests/unit/helpers/test_<name>_helper.py`

---

### `scaffold validate`

```
scaffold validate [--layer <layer>]
```

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `--layer` | str | ➖ | all layers | Restrict validation to a single layer |

**Exit codes**: `0` no violations, `1` one or more violations detected.

**Output** (human-readable):
```
✅ scaffold validate — no violations found

# or on failure:
❌ Violation: domain/model/order.py imports from infrastructure/driven_adapters/
   Rule: domain/model MUST NOT import from any other layer
```

---

### `scaffold delete`

```
scaffold delete --module <name>
```

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `--module` | str | ✅ | — | snake_case name of the component to remove |

**Exit codes**: `0` success, `1` module not found.

---

### `scaffold update`

```
scaffold update [--skip-git-check] [--dry-run]
```

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `--skip-git-check` | bool | ➖ | False | Skip the "please commit first" warning |
| `--dry-run` | bool | ➖ | False | Show what would be updated without writing files |

**Exit codes**: `0` success, `1` error.

---

### `scaffold list`

```
scaffold list [--type <driven-adapter|entry-point>]
```

| Option | Type | Required | Default | Description |
|---|---|---|---|---|
| `--type` | enum | ➖ | all | Filter by component category |

**Output** (human-readable table via Rich):
```
Driven Adapters
───────────────────────────────────────────────
 generic          Empty adapter stub
 repository       SQLAlchemy / asyncpg stub
 rest-client      HTTP client adapter stub
 ...

Entry Points
───────────────────────────────────────────────
 generic          Empty entry point stub
 rest-api         REST API router stub
 ...
```

---

### `scaffold version`  *(exists)*

```
scaffold version
```

Prints the installed package version.

---

## Exit Code Summary

| Code | Meaning |
|---|---|
| `0` | Command completed successfully |
| `1` | User error (bad input, not in project dir, file exists without `--force`, validation failure) |
| `2` | Internal/unexpected error (should not reach user under normal operation) |

---

## `.scaffold-ca.json` Schema

See [data-model.md](../data-model.md) for the full entity definition. Abbreviated here for contract reference:

```json
{
  "$schema": "scaffold-ca/v1",
  "scaffold_version": "1.0.0",
  "name": "my_project",
  "package": "my_project",
  "mode": "sync",
  "created_at": "2026-03-25T10:00:00Z",
  "components": [
    {
      "type": "USE_CASE",
      "name": "process_order",
      "class_name": "ProcessOrderUseCase",
      "layer": "domain/usecase",
      "files": [
        "my_project/domain/usecase/process_order_use_case.py",
        "tests/unit/usecase/test_process_order_use_case.py"
      ],
      "options": {},
      "is_boilerplate": false
    }
  ]
}
```
