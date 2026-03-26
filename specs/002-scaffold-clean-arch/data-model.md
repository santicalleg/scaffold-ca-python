# Data Model: Python Clean Architecture Scaffold

**Branch**: `002-scaffold-clean-arch` | **Date**: 2026-03-25

---

## Overview

All persistent state lives in a single `.scaffold-ca.json` marker file at the project root. No database or remote storage is used. The in-memory domain model is a set of Python dataclasses in `core/project.py`.

---

## Entities

### ProjectMarker

The root entity. Persisted as `.scaffold-ca.json`.

| Field | Type | Required | Description |
|---|---|---|---|
| `scaffold_version` | `str` | ✅ | Version of the scaffold tool that created the project (semver) |
| `name` | `str` | ✅ | Project name (snake_case) |
| `package` | `str` | ✅ | Top-level Python package name (snake_case, derived from `--package` last segment) |
| `mode` | `"sync" \| "async"` | ✅ | Project execution mode; inherited by all generated components |
| `created_at` | `str` (ISO 8601) | ✅ | Creation timestamp |
| `components` | `list[ComponentRecord]` | ✅ | Registry of all generated components |

**Validation rules**:
- `name` and `package`: must match `^[a-z][a-z0-9_]*$`; must not be a Python reserved keyword.
- `scaffold_version`: semver string; used by `scaffold update` to detect stale boilerplate.

---

### ComponentRecord

Represents a single generated artifact registered in the project.

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | `ComponentType` | ✅ | Enum identifying the kind of component |
| `name` | `str` | ✅ | Normalized snake_case name |
| `class_name` | `str` | ✅ | PascalCase class name |
| `layer` | `LayerPath` | ✅ | Owning layer (e.g., `"domain/usecase"`) |
| `files` | `list[str]` | ✅ | Project-relative paths of all files generated for this component |
| `options` | `dict[str, str]` | ➖ | Type-specific options used at generation time (e.g., `{"url": "https://api.example.com"}`) |
| `is_boilerplate` | `bool` | ✅ | If `True`, `scaffold update` may refresh this file. If `False`, user-authored content — never overwritten. |

---

### ComponentType (enum)

```
# Domain
MODEL
USE_CASE

# Infrastructure — Driven Adapters
DA_GENERIC
DA_REPOSITORY
DA_REST_CLIENT
DA_MONGODB
DA_REDIS
DA_DYNAMO
DA_S3
DA_SQS_SENDER
DA_KAFKA_SENDER
DA_RABBITMQ_SENDER
DA_SECRETS

# Infrastructure — Entry Points
EP_GENERIC
EP_REST_API
EP_GRAPHQL
EP_KAFKA_CONSUMER
EP_SQS_LISTENER
EP_ASYNC_EVENT_HANDLER
EP_CLI

# Infrastructure — Helpers
HELPER

# Application
APP_BOILERPLATE
```

---

### LayerPath (value object)

A string-typed enum representing the seven project layers and their filesystem paths relative to the project root.

| LayerPath value | Directory | Dependency rank |
|---|---|---|
| `"domain/model"` | `<pkg>/domain/model/` | 0 (innermost — no deps allowed) |
| `"domain/usecase"` | `<pkg>/domain/usecase/` | 1 (depends only on model) |
| `"infrastructure/driven_adapters"` | `<pkg>/infrastructure/driven_adapters/` | 2 |
| `"infrastructure/entry_points"` | `<pkg>/infrastructure/entry_points/` | 2 |
| `"infrastructure/helpers"` | `<pkg>/infrastructure/helpers/` | 2 |
| `"app"` | `<pkg>/app/` | 3 (composition root — may depend on any layer) |
| `"deployment"` | `deployment/` | ∞ (non-Python; not analysed by `scaffold validate`) |

---

### Template (in-process value object)

Not persisted to disk. Used by `core/renderer.py`.

| Field | Type | Description |
|---|---|---|
| `component_type` | `ComponentType` | Identifies which template directory to load |
| `files` | `list[TemplateFile]` | Ordered list of files to render |
| `required_options` | `list[str]` | Flags that must be present for this type (e.g., `--url` for `rest-client`) |
| `optional_options` | `dict[str, Any]` | Optional flags and their default values |

---

### TemplateFile (in-process value object)

| Field | Type | Description |
|---|---|---|
| `template_path` | `str` | Path inside `templates/<component_type>/` |
| `output_path_template` | `str` | Jinja2 expression for the output path (e.g., `"{{ layer }}/{{ name }}.py"`) |
| `is_boilerplate` | `bool` | Whether this file is updatable by `scaffold update` |

---

## State Transitions

### Project Lifecycle

```
[not initialized]
      │  scaffold new --name <x>
      ▼
[initialized]  ← .scaffold-ca.json created, boilerplate files written
      │  scaffold generate ...
      ▼
[components added]  ← new ComponentRecord appended to .scaffold-ca.json
      │  scaffold delete --module <x>
      ▼
[component removed]  ← ComponentRecord removed, files deleted
      │  scaffold update
      ▼
[boilerplate refreshed]  ← boilerplate files updated, user files untouched
```

### validate Command — No State Mutation

`scaffold validate` is a read-only operation. It reads `.scaffold-ca.json` and all `.py` files; it never writes any file.

---

## Name Normalization Rules

| Input | snake_case output | PascalCase output |
|---|---|---|
| `ProcessOrder` | `process_order` | `ProcessOrder` |
| `processOrder` | `process_order` | `ProcessOrder` |
| `process-order` | `process_order` | `ProcessOrder` |
| `process_order` | `process_order` (unchanged) | `ProcessOrder` |
| `PROCESS_ORDER` | `process_order` | `ProcessOrder` |
| `import` (reserved) | ❌ rejected | — |
| `order__item` (double underscore) | ❌ rejected | — |

---

## Dependency Rule Matrix (for `scaffold validate`)

| Source layer | May import from |
|---|---|
| `domain/model` | nothing (no cross-layer imports) |
| `domain/usecase` | `domain/model` only |
| `infrastructure/driven_adapters` | `domain/model`, `domain/usecase`, `infrastructure/helpers` |
| `infrastructure/entry_points` | `domain/model`, `domain/usecase`, `infrastructure/helpers` |
| `infrastructure/helpers` | `domain/model`, `domain/usecase` |
| `app` | any layer |
| `deployment` | not analysed |
