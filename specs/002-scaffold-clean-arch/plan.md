# Implementation Plan: Python Clean Architecture Scaffold

**Branch**: `002-scaffold-clean-arch` | **Date**: 2026-03-25 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `/specs/002-scaffold-clean-arch/spec.md`

## Summary

Build a Python CLI tool (`scaffold-ca-python`) that generates and manages opinionated Python project structures following Clean Architecture principles — a direct translation of the bancolombia/scaffold-clean-architecture Gradle plugin into idiomatic Python. The tool exposes commands for project creation (`new`), component generation (`generate model|use-case|driven-adapter|entry-point|helper`), structural validation (`validate`), module deletion (`delete`), project update (`update`), and component discovery (`list`). All generated artifacts are rendered from Jinja2 templates. Project metadata is persisted in `.scaffold-ca.json` at the project root. The CLI is built on the existing Typer + Rich foundation already present in `src/scaffold_ca_python/cli.py`.

## Technical Context

**Language/Version**: Python 3.13+  
**Primary Dependencies**: typer ≥ 0.16 (CLI framework, already installed), rich ≥ 14.1 (terminal output, already installed), Jinja2 (template rendering — to be added), stdlib `ast` (import analysis for `validate`), stdlib `json` (marker file I/O)  
**Storage**: `.scaffold-ca.json` — plain JSON file at project root; no database  
**Testing**: pytest (to be added as dev dependency); generated projects also use pytest as their default test runner  
**Target Platform**: macOS / Linux / Windows CLI (cross-platform); distributed via PyPI  
**Project Type**: CLI code-generation tool (library + CLI)  
**Performance Goals**: Any `generate` or `validate` command completes in < 5 s; `scaffold new` completes in < 30 s  
**Constraints**: No network access required at runtime; no system-level dependencies; must work inside a standard `venv`  
**Scale/Scope**: Single-project per invocation; 21 FRs; 18 component types (11 driven-adapter + 7 entry-point)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Constitution is a blank template (not yet ratified for this project) — no gates to evaluate. Proceeding without violations.

## Project Structure

### Documentation (this feature)

```text
specs/002-scaffold-clean-arch/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── cli-schema.md
└── tasks.md             # Phase 2 output (created by /speckit.tasks)
```

### Source Code (repository root)

```text
src/scaffold_ca_python/
├── cli.py                          # Entry point — top-level Typer app (exists)
├── __init__.py                     # (exists, empty)
│
├── commands/                       # One module per top-level command
│   ├── new.py                      # scaffold new
│   ├── generate/
│   │   ├── __init__.py
│   │   ├── model.py                # scaffold generate model
│   │   ├── use_case.py             # scaffold generate use-case
│   │   ├── driven_adapter.py       # scaffold generate driven-adapter
│   │   ├── entry_point.py          # scaffold generate entry-point
│   │   └── helper.py               # scaffold generate helper
│   ├── validate.py                 # scaffold validate
│   ├── delete.py                   # scaffold delete
│   ├── update.py                   # scaffold update
│   └── list_components.py          # scaffold list
│
├── core/
│   ├── __init__.py
│   ├── project.py                  # ProjectMarker: read/write .scaffold-ca.json
│   ├── naming.py                   # Name normalization (snake_case / PascalCase)
│   ├── renderer.py                 # Jinja2 template rendering engine
│   └── validator.py                # AST-level import analysis for `scaffold validate`
│
└── templates/                      # Jinja2 file templates, one dir per component type
    ├── project/                    # scaffold new — full project tree
    ├── model/
    ├── use_case/
    ├── driven_adapter/
    │   ├── generic/
    │   ├── repository/
    │   ├── rest_client/
    │   ├── mongodb/
    │   ├── redis/
    │   ├── dynamo/
    │   ├── s3/
    │   ├── sqs_sender/
    │   ├── kafka_sender/
    │   ├── rabbitmq_sender/
    │   └── secrets/
    └── entry_point/
        ├── generic/
        ├── rest_api/
        ├── graphql/
        ├── kafka_consumer/
        ├── sqs_listener/
        ├── async_event_handler/
        └── cli/

tests/
├── unit/
│   ├── test_naming.py
│   ├── test_renderer.py
│   ├── test_project.py
│   └── test_validator.py
└── integration/
    ├── test_new.py
    ├── test_generate.py
    ├── test_validate.py
    ├── test_delete.py
    ├── test_update.py
    └── test_list.py
```

**Structure Decision**: Single-project CLI tool using the existing `src/scaffold_ca_python/` layout. Commands are organized as submodules under `commands/`. Core logic is isolated in `core/` for independent testability. Templates live under `templates/` as plain text Jinja2 files shipped with the package (included via `tool.hatch.build` configuration).

## Complexity Tracking

No constitution violations to justify.
