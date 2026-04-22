# Data Model: PyPI Publishing & README Documentation

**Feature**: `020-pypi-publish-readme`
**Derived from**: research.md + spec FR-001 through FR-008

---

## 1. `pyproject.toml` — `[project]` table additions

All fields below are **additions** to the existing `[project]` table. No existing fields change.

### `license` (string, SPDX identifier)

```toml
license = "MIT"
```

- Type: SPDX license expression string (PEP 639)
- Constraint: Must match the `LICENSE` file content (already MIT)
- PyPI validates this against the Trove classifier `License :: OSI Approved :: MIT License`

### `keywords` (list of strings)

```toml
keywords = ["clean architecture", "scaffold", "code generation", "cli", "python", "mcp", "fastapi"]
```

- Type: list\[str\]
- Constraint: ≤15 keywords recommended by PyPI; each keyword ≤50 chars
- Purpose: Powers PyPI search index

### `classifiers` (list of Trove strings)

```toml
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "Topic :: Software Development :: Code Generators",
    "Topic :: Software Development :: Libraries :: Application Frameworks",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.13",
    "Operating System :: OS Independent",
    "Environment :: Console",
    "Typing :: Typed",
]
```

- Type: list\[str\] (Trove classifiers; validated by PyPI against the official taxonomy)
- Constraint: All classifiers must exist in the PyPI classifier list

### `authors` (updated — add `name` field)

```toml
authors = [
    { name = "Santiago Callegari", email = "santiagocalleg@gmail.com" }
]
```

- Type: list\[inline table\] with `name` and `email` keys
- Change: add `name` key alongside the existing `email` key

---

## 2. `pyproject.toml` — `[project.urls]` table (new section)

```toml
[project.urls]
Homepage = "https://github.com/santiagocalleg/scaffold-ca-python"
Repository = "https://github.com/santiagocalleg/scaffold-ca-python"
Issues = "https://github.com/santiagocalleg/scaffold-ca-python/issues"
```

- Type: TOML table; keys are display labels on the PyPI sidebar; values are absolute URLs
- Constraint: URLs must be reachable; PyPI does not validate them but crawlers will

> **Note**: Replace with the actual GitHub repository URL if it differs.

---

## 3. `README.md` — section schema

Each section below defines its required presence, heading level, and content contract.

| # | Section | Heading | Required | Content |
|---|---------|---------|----------|---------|
| 1 | Project title + badges | `# scaffold-ca-python` | ✅ | Name + PyPI version badge + Python version badge + License badge |
| 2 | Description | `## What is this?` | ✅ | 2–4 sentence plain-language description; Clean Architecture rationale |
| 3 | Installation | `## Installation` | ✅ | `pip install` command + `uv add` command; requires Python 3.13+ note |
| 4 | Quick Start | `## Quick Start` | ✅ | Step-by-step: install → `scaffold ca` → `scaffold gm` → run project |
| 5 | Commands & Examples | `## Commands & Examples` | ✅ | Sub-section per command; usage + example for each of the 10 commands |
| 6 | Technologies | `## Technologies` | ✅ | Table: tool/library, version, role |
| 7 | Current Features | `## Current Features` | ✅ | Bullet list per implemented command/feature |
| 8 | Contributing | `## Contributing` | ✅ | Fork → clone → `uv sync` → tests → PR steps |
| 9 | License | `## License` | ✅ | One-liner + link to LICENSE file |

### Commands & Examples sub-section schema

Each command gets:
- A `###` heading: `### scaffold ca` (with alias note)
- A brief one-line description
- A fenced `bash` code block with the most common invocation
- `--dry-run` example where applicable

Commands covered (10 total):

| Command | Alias | Example invocation |
|---------|-------|--------------------|
| `clean-architecture` | `ca` | `scaffold ca --name my-project` |
| `generate-model` | `gm` | `scaffold gm --name Order` |
| `generate-use-case` | `guc` | `scaffold guc --name CreateOrder` |
| `generate-driven-adapter` | `gda` | `scaffold gda --type rest-consumer` |
| `generate-entry-point` | `gep` | `scaffold gep --type restapi` / `--type mcp` |
| `generate-helper` | `gh` | `scaffold gh --name LoggingHelper` |
| `generate-pipeline` | `gpipe` | `scaffold gpipe --provider github` |
| `validate-structure` | `vs` | `scaffold vs` |
| `delete-module` | `dm` | `scaffold dm --name Order` |
| `update-project` | `up` | `scaffold up` |

### Technologies table schema

| Tool / Library | Version | Role |
|----------------|---------|------|
| Python | ≥3.13 | Runtime |
| uv | latest | Dependency management, build, publish |
| Typer | ≥0.16.0 | CLI framework |
| Rich | ≥14.1.0 | Terminal output formatting |
| Jinja2 | ≥3.1 | Template engine for code generation |
| Pydantic v2 | ≥2.0 | Runtime validation of template context |
| hatchling | latest | Build backend |
| uv-dynamic-versioning | latest | PEP 440 version from git tags |
| ruff | latest | Linter + formatter |
| mypy | latest (strict) | Static type checker |
| pytest + pytest-cov | latest | Testing + coverage (≥80% gate) |
