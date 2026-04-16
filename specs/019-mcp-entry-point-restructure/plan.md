# Implementation Plan: MCP Entry Point Restructure

**Branch**: `019-mcp-entry-point-restructure` | **Date**: 2026-04-16 | **Spec**: [spec.md](../018-mcp-entry-point-restructure/spec.md)  
**Input**: Feature specification from `/specs/018-mcp-entry-point-restructure/spec.md`

## Summary

Restructure the `gep --type mcp` command to generate MCP server primitives as individual focused modules (`tools.py`, optional `resources.py`, optional `prompts.py`) instead of the current monolithic `server.py`. Simultaneously add two new generated files: `application/app.py` (Starlette/FastMCP composition root) and `src/<pkg>/server.py` (uvicorn entrypoint replacing `main.py`). Two new CLI flags `--with-resources` and `--with-prompts` control the optional primitive files. All changes are template-driven (Jinja2) per Principle II.

## Technical Context

**Language/Version**: Python 3.13+  
**Primary Dependencies**: Typer (CLI), Rich (output), Jinja2 (templates), Pydantic v2 (context models), `mcp>=1.0` (generated project dep), `starlette` (generated project dep), `uvicorn` (generated project dep), `dependency-injector` (generated project dep)  
**Storage**: N/A — file system writes only  
**Testing**: pytest + pytest-cov (≥80% coverage gate), ruff (linter), mypy strict  
**Target Platform**: CLI tool running on Python 3.13+; generated code targets Linux/macOS  
**Project Type**: CLI code-generation tool  
**Performance Goals**: N/A  
**Constraints**: ruff line-length=120; mypy strict; no new regressions in existing tests  
**Scale/Scope**: ~6 new/modified Jinja2 templates, 1 modified factory, 1 modified CLI command, ~10 new/modified tests

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I — Clean Architecture in Generated Projects** | ✅ PASS | `tools.py`/`resources.py`/`prompts.py` live in `infrastructure/entry_points/mcp_server/` (inbound adapters). `app.py` lives in `application/` (composition root). `server.py` lives at the package root as entrypoint. All dependency rules are preserved. |
| **II — Template-Driven Code Generation** | ✅ PASS | All new generated files originate from Jinja2 templates under `src/scaffold_ca_python/templates/`. New tests in `tests/templates/` assert key class/function names and import statements. |
| **III — Full Command Parity** | ✅ PASS | `gep --type mcp` is an existing mandated command. Adding `--with-resources`/`--with-prompts` flags extends it; no new commands are introduced. |
| **IV — Python-First Idioms** | ✅ PASS | All templates use async/await; type hints on all stubs; ruff-compliant output. |
| **V — Test-First Development** | ✅ PASS | Tests for each new template and factory behaviour written before implementation code. |
| **VI — Developer Experience** | ✅ PASS | Dry-run previews all changes; Rich-formatted output; error messages include hints. |
| **VII — Branch Naming** | ✅ PASS | Branch `019-mcp-entry-point-restructure` follows the flat numbered-branch convention. |

## Project Structure

### Documentation (this feature)

```text
specs/019-mcp-entry-point-restructure/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output
├── contracts/
│   └── gep-mcp.md       ← Phase 1 output
└── tasks.md             ← Phase 2 output (/speckit.tasks)
```

### Source Code Changes

```text
src/scaffold_ca_python/
├── templates/
│   └── entry_point/
│       └── mcp/
│           ├── __init__.py.jinja2          (unchanged)
│           ├── tools.py.jinja2             (NEW — replaces server.py.jinja2)
│           ├── resources.py.jinja2         (NEW — optional primitive)
│           ├── prompts.py.jinja2           (NEW — optional primitive)
│           ├── app.py.jinja2               (NEW — composition root)
│           ├── server.py.jinja2            (NEW — uvicorn entrypoint, replaces entrypoint_main.py.jinja2)
│           ├── test_tools.py.jinja2        (NEW — replaces test_server.py.jinja2)
│           ├── test_resources.py.jinja2    (NEW — optional test stub)
│           ├── test_prompts.py.jinja2      (NEW — optional test stub)
│           ├── server.py.jinja2            (DELETED — was monolithic MCP impl)
│           └── entrypoint_main.py.jinja2   (DELETED — superseded by new server.py)
├── factory/
│   └── entry_points/
│       └── ep_mcp.py                       (MODIFIED — new build logic)
└── commands/
    └── generate_entry_point.py             (MODIFIED — add --with-resources, --with-prompts flags)

tests/
├── templates/
│   └── test_entry_point_templates.py       (MODIFIED — update MCP section, add new assertions)
├── factory/
│   └── entry_points/
│       └── test_ep_mcp.py                  (MODIFIED — update existing tests, add flag tests)
└── commands/
    └── test_generate_entry_point.py        (MODIFIED — add MCP flag integration tests)
```

## Complexity Tracking

No constitution violations.

---

## Phase 0: Research

*All NEEDS CLARIFICATION items resolved here.*

**Research areas**:
1. How does the `EntryPointRestApi` factory handle conditional file generation? (pattern to follow for `--with-resources`/`--with-prompts`)
2. How does `generate_entry_point.py` pass flags to the factory via `builder.add_param`? (pattern for new flags)
3. How does `ep_restapi.py` update `pyproject.toml` scripts? (pattern for FR-010)
4. What does `mcp.server.FastMCP` and `mcp.server.transport_security` API look like for the `app.py` template?

See [`research.md`](research.md) for findings.

---

## Phase 1: Design & Contracts

### Data Model

See [`data-model.md`](data-model.md) for entity definitions.

**Key entities**:
- `EntryPointMcp.build()` gains access to two new boolean builder params: `with_resources: bool` and `with_prompts: bool`
- New template context: same `ModuleContext.model_dump()` as today — no new context fields needed; conditional logic lives in the factory, not the templates
- `app.py.jinja2` template needs `with_resources: bool` and `with_prompts: bool` in its render context to conditionally include import lines and `bind_*` calls

### Interface Contracts

See [`contracts/gep-mcp.md`](contracts/gep-mcp.md) for the full CLI contract.

**CLI changes to `gep`**:
```
scaffold gep --type mcp [--with-resources] [--with-prompts] [--dry-run]
```

| Flag | Type | Default | Constraint |
|------|------|---------|------------|
| `--type mcp` | str | — | existing |
| `--with-resources` | bool | False | mcp only |
| `--with-prompts` | bool | False | mcp only |
| `--dry-run` | bool | False | all types |

**Guard**: If `--with-resources` or `--with-prompts` are passed with any type other than `mcp`, exit 1 with:
```
Error: --with-resources and --with-prompts are only valid with --type mcp.
```

### Agent Context Update

Run after Phase 1 artifacts are complete:
```bash
bash .specify/scripts/bash/update-agent-context.sh copilot
```
