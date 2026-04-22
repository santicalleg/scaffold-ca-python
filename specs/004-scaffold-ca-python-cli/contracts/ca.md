# Contract: `ca` / `generate-project`

**Command**: `scaffold ca` (alias: `scaffold generate-project`)  
**US**: US-1 — Scaffold entire project

---

## Purpose

Bootstraps a new Python Clean Architecture project from scratch. Creates the full directory tree, configuration files, and initial stubs for each architectural layer.

---

## Signature

```
scaffold ca --name <NAME> [--package <PACKAGE>] [--dry-run]
```

| Flag | Type | Required | Default | Description |
|---|---|---|---|---|
| `--name` | `str` | **Yes** | — | Project name. Validated: `^[A-Za-z][A-Za-z0-9_]*$` |
| `--package` | `str` | No | `"com.example"` | Dot-notation package identifier, e.g. `com.acme` |
| `--dry-run` | `bool` | No | `False` | Preview files without writing any output |

---

## Inputs → Outputs

**Given** `scaffold ca --name MyProject --package com.acme`:

```
my_project/
├── pyproject.toml
├── README.md
├── .gitignore
├── .ruff.toml
├── mypy.ini
├── src/
│   └── my_project/
│       ├── __init__.py
│       ├── application/
│       │   └── __init__.py
│       ├── domain/
│       │   ├── model/
│       │   │   └── __init__.py
│       │   └── usecase/
│       │       └── __init__.py
│       └── infrastructure/
│           ├── driven_adapters/
│           │   └── __init__.py
│           ├── entry_points/
│           │   └── __init__.py
│           └── helpers/
│               └── __init__.py
└── tests/
    └── __init__.py
```

**Dry-run**: prints a Rich tree of paths that would be created; writes nothing.

---

## State Written

Writes `[tool.scaffold-ca-python]` section to the new project's `pyproject.toml`:

```toml
[tool.scaffold-ca-python]
name = "MyProject"
package = "com.acme"
python_package = "my_project"
created_at = "<ISO8601>"
```

---

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Project created (or dry-run completed) successfully |
| `1` | Validation error (invalid name, target directory already exists) |
| `2` | Internal/unexpected error |

---

## Errors

| Condition | Message | Exit |
|---|---|---|
| `--name` fails regex | `Name 'X' is invalid. Use letters, digits, underscores; must start with a letter.` | `1` |
| Target directory already exists | `Directory 'my_project/' already exists. Aborting to prevent data loss.` | `1` |
