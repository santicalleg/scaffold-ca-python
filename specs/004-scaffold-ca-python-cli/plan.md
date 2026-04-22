# Implementation Plan: scaffold-ca-python CLI

**Branch**: `feature/004-scaffold-ca-python-cli` | **Date**: 2026-03-26 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/004-scaffold-ca-python-cli/spec.md`

## Summary

Build `scaffold-ca-python`, a Python CLI tool that is a port of the Java/Gradle [bancolombia/scaffold-clean-architecture](https://github.com/bancolombia/scaffold-clean-architecture) plugin. The tool allows Python developers to instantly scaffold production-ready async Python applications following Clean Architecture principles via 10 commands (`ca`, `gm`, `guc`, `gda`, `gep`, `gh`, `gpipe`, `vs`, `dm`, `up`).

**Technical approach**: Typer (CLI) + Rich (output) + Jinja2 (all code generation via templates) + Pydantic v2 (context validation) + `ast` module (structural validation). Commands share a flat app structure; each exports a `register(app)` function. Aliases use two thin wrappers calling a shared implementation function. All file writes are atomic via tempdir + `os.replace()`.

## Technical Context

**Language/Version**: Python 3.13+  
**Primary Dependencies**: Typer, Rich, Jinja2, Pydantic v2, httpx (generated projects), FastAPI (generated restapi entry points)  
**Storage**: N/A (stateless CLI; minimal state in `pyproject.toml` of generated projects under `[tool.scaffold-ca-python]`)  
**Testing**: pytest + pytest-cov (80% coverage gate, NON-NEGOTIABLE per constitution)  
**Target Platform**: macOS, Linux (cross-platform paths via `pathlib`; Windows support deferred to v2 per spec Assumptions)  
**Project Type**: CLI tool (distributed as a PyPI package, installed via `pip` or `uv tool install`)  
**Performance Goals**: Sub-second response for all commands; `vs` scan of 500+ files in <2s  
**Constraints**: No external services; offline-capable; no runtime database; atomic write semantics to prevent partial generation  
**Scale/Scope**: Single-developer or team projects; handles codebases up to ~5000 `.py` files for `vs`

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|---|---|---|
| **I. Clean Architecture in Generated Projects** | ✅ PASS | `vs` command enforces dependency rules; all `generate-*` commands emit correctly layered code |
| **II. Template-Driven Code Generation** | ✅ PASS | All generated files originate from Jinja2 templates under `src/scaffold_ca_python/templates/`; no f-string assembly; `tests/templates/` directory constitutionally mandated (Amendment v2.0.0) |
| **III. Full Command Parity** | ✅ PASS | 10 commands implemented; gda types: `rest-consumer`, `secrets`, `generic`; gep types: `restapi`, `agent`, `mcp`, `generic` — formally scoped in v1 per Amendment v2.0.0 |
| **IV. Python-First Idioms** | ✅ PASS | Python 3.13+, type hints on all public APIs, ruff+mypy strict, async/await in generated projects, uv for builds |
| **V. Test-First (NON-NEGOTIABLE)** | ✅ PASS | TDD cycle enforced; pytest+pytest-cov 80% gate; every `generate-*` command emits a test scaffold file |
| **VI. Developer Experience** | ✅ PASS | Rich output on all commands, `--dry-run` on all commands, resolution hints in all error messages, aliases for all commands |
| **VII. Git Workflow** | ✅ PASS | Branch: `feature/004-scaffold-ca-python-cli` (lowercase kebab-case with `/` separator) |

**Post-design re-check**: All principles continue to pass. No additions to Complexity Tracking required.

## Project Structure

### Documentation (this feature)

```text
specs/004-scaffold-ca-python-cli/
├── plan.md              # This file (/speckit.plan command output)
├── spec.md              # Feature specification (US1–US10)
├── research.md          # Phase 0 output — 11 research findings (R-01–R-11)
├── data-model.md        # Phase 1 output — internal entities
├── quickstart.md        # Phase 1 output — developer walkthrough
├── contracts/           # Phase 1 output — one file per command
│   ├── ca.md, gm.md, guc.md, gda.md, gep.md
│   ├── vs.md, gh.md, gpipe.md, dm.md, up.md
└── tasks.md             # Phase 2 output (/speckit.tasks — NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/scaffold_ca_python/
├── cli.py                              # Typer app + register() call per command module
├── commands/
│   ├── generate_project.py             # ca / generate-project (US-1)
│   ├── generate_model.py               # gm / generate-model (US-2)
│   ├── generate_use_case.py            # guc / generate-use-case (US-3)
│   ├── generate_driven_adapter.py      # gda / generate-driven-adapter (US-4)
│   ├── generate_entry_point.py         # gep / generate-entry-point (US-5)
│   ├── validate_structure.py           # vs / validate-structure (US-6)
│   ├── generate_helper.py              # gh / generate-helper (US-7)
│   ├── generate_pipeline.py            # gpipe / generate-pipeline (US-8)
│   ├── delete_module.py                # dm / delete-module (US-9)
│   └── update_project.py               # up / update-project
├── core/
│   ├── template_renderer.py            # Jinja2 Environment + atomic rendering (R-05, R-06)
│   ├── file_writer.py                  # FileWriter: real + dry-run modes
│   ├── project_detector.py             # Root detection via pyproject.toml (R-10)
│   ├── structure_validator.py          # AST-based layer violation scanner (R-08)
│   └── name_utils.py                   # snake_case / PascalCase + regex validation (R-11)
├── models/
│   ├── context.py                      # ProjectContext, ModuleContext (Pydantic v2, R-07)
│   ├── layer.py                        # Layer enum + dependency rules
│   ├── file_operation.py               # GeneratedFile, CreateFile, DeleteFile
│   └── violation.py                    # Violation, ValidationReport
└── templates/
    ├── project/                        # ca templates (pyproject.toml, README, ruff, mypy, __init__)
    ├── model/                          # gm templates
    ├── use_case/                       # guc templates
    ├── driven_adapter/
    │   ├── rest_consumer/
    │   ├── secrets/
    │   └── generic/
    ├── entry_point/
    │   ├── restapi/                # FastAPI
    │   ├── agent/                      # A2A
    │   ├── mcp/                        # MCP server
    │   └── generic/
    ├── helper/
    └── pipeline/
        ├── github/
        └── azure/

tests/
├── commands/                           # Command tests via Typer CliRunner (workflow, dry-run, performance)
├── core/                               # Unit tests for engine components
├── models/                             # Unit tests for Pydantic models
└── templates/                          # Template rendering tests
```

**Structure Decision**: Single-project layout. CLI tool divided into `commands/` (Typer handlers), `core/` (shared engine), `models/` (Pydantic data classes), `templates/` (Jinja2 source). Generated projects are artifacts, not part of this repo.

## Complexity Tracking

> No constitution violations — no entries required.
