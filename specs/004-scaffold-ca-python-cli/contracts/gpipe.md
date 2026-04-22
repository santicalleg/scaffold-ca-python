# Contract: `gpipe` / `generate-pipeline`

**Command**: `scaffold gpipe` (alias: `scaffold generate-pipeline`)  
**US**: US-8 — Scaffold CI/CD pipeline

---

## Purpose

Generates a CI/CD pipeline configuration file at the project root. The `--provider` flag is mandatory; there is no default.

---

## Signature

```
scaffold gpipe --provider <PROVIDER> [--dry-run]
```

| Flag | Type | Required | Default | Description |
|---|---|---|---|---|
| `--provider` | `str` | **Yes** | — | Pipeline provider. One of: `github`, `azure` |
| `--dry-run` | `bool` | No | `False` | Preview files without writing any output |

---

## Type Behaviour

### `github`

Generates a GitHub Actions workflow:

```
.github/
└── workflows/
    └── ci.yml
```

The workflow includes: lint (ruff), type-check (mypy), test (pytest with coverage gate at 80%).

### `azure`

Generates an Azure Pipelines YAML:

```
azure-pipelines.yml
```

The pipeline includes: lint (ruff), type-check (mypy), test (pytest with coverage gate at 80%).

---

## Dry-Run

Prints the output file path and content to stdout; writes nothing.

---

## Prerequisites

Must be run inside a directory tree that contains a `pyproject.toml` with a `[tool.scaffold-ca-python]` section.

---

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | File created (or dry-run completed) successfully |
| `1` | Validation error |
| `2` | Internal/unexpected error |

---

## Errors

| Condition | Message | Exit |
|---|---|---|
| `--provider` missing | `--provider is required. Choose from: github, azure.` | `1` |
| `--provider` is not in allowed list | `Unknown provider 'X'. Allowed: github, azure.` | `1` |
| Target file already exists | `'ci.yml' already exists at '.github/workflows/ci.yml'. Use --force to overwrite.` | `1` |
| No project root | `No scaffold-ca-python project found. Run 'scaffold ca' first.` | `1` |
