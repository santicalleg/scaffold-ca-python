# Quickstart: scaffold-ca-python

A walkthrough of a developer's first session with `scaffold-ca-python`, from project creation to a first validated Clean Architecture structure.

---

## Prerequisites

```bash
pip install scaffold-ca-python   # or: uv tool install scaffold-ca-python
scaffold --version
```

---

## 1. Bootstrap a new project

```bash
scaffold ca --name OrderService --package com.acme
cd order_service
```

This creates the full Clean Architecture skeleton:

```
order_service/
├── pyproject.toml             ← includes [tool.scaffold-ca-python] metadata
├── README.md
├── .ruff.toml
├── mypy.ini
├── src/order_service/
│   ├── application/
│   ├── domain/model/
│   ├── domain/usecase/
│   └── infrastructure/
│       ├── driven_adapters/
│       ├── entry_points/
│       └── helpers/
└── tests/
```

---

## 2. Add a domain model

```bash
scaffold gm --name Order
```

Creates:

- `src/order_service/domain/model/order.py` — Pydantic v2 `BaseModel`
- `tests/domain/model/test_order.py` — pytest stub

---

## 3. Add a use case

```bash
scaffold guc --name CreateOrder
```

Creates:

- `src/order_service/domain/usecase/create_order.py` — async use case
- `tests/domain/usecase/test_create_order.py` — pytest stub

---

## 4. Add a driven adapter

```bash
scaffold gda --type rest-consumer
```

Creates an async `httpx`-based adapter in `infrastructure/driven_adapters/rest_consumer/`.

---

## 5. Add a REST entry point (FastAPI)

```bash
scaffold gep --type restapi
```

Creates a FastAPI async application in `infrastructure/entry_points/restapi/`.

**Contract-first variant** (if you have an OpenAPI spec):

```bash
scaffold gep --type restapi --swagger openapi.yaml
```

---

## 6. Add a CI/CD pipeline

```bash
scaffold gpipe --provider github
```

Creates `.github/workflows/ci.yml` with lint, type-check, and test stages.

---

## 7. Validate the Clean Architecture structure

```bash
scaffold vs
```

Clean output:
```
✓ Validated 18 files — no violations found.
```

If a violation is introduced (e.g. `domain/model` imports from `infrastructure`), `vs` will report it:

```
✗ 1 violation(s) found:

  src/order_service/domain/model/order.py:5
    from order_service.infrastructure.driven_adapters.rest_consumer import ...
    domain/model must not import from infrastructure/driven-adapters
    Hint: Define a port interface in domain/model and inject the adapter.
```

Exit code is `1` — useful for CI gates.

---

## 8. Preview any command before writing

Every command supports `--dry-run`:

```bash
scaffold gm --name Payment --dry-run
scaffold gda --type secrets --dry-run
scaffold dm --name Order        # dm is dry-run by default
scaffold dm --name Order --confirm   # actual deletion
```

---

## 9. Update project dependencies

```bash
scaffold up
```

Runs `uv lock --upgrade && uv sync` in the project root.

---

## Full command reference

| Command | Alias | Purpose |
|---|---|---|
| `generate-project` | `ca` | Bootstrap project |
| `generate-model` | `gm` | Add domain model |
| `generate-use-case` | `guc` | Add use case |
| `generate-driven-adapter` | `gda` | Add driven adapter |
| `generate-entry-point` | `gep` | Add entry point |
| `generate-helper` | `gh` | Add helper utility |
| `generate-pipeline` | `gpipe` | Add CI/CD pipeline |
| `validate-structure` | `vs` | Check dependency rules |
| `delete-module` | `dm` | Remove a module |
| `update-project` | `up` | Update dependencies |
