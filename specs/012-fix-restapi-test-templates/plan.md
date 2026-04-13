# Implementation Plan: Fix RestAPI Entry Point Test Templates

**Branch**: `012-fix-restapi-test-templates` | **Date**: 2026-04-10 | **Spec**: [spec.md](spec.md)  
**Input**: Feature specification from `specs/012-fix-restapi-test-templates/spec.md`

## Summary

The restapi entry-point test templates have three classes of bugs: (1) `test_rest_controller.py.jinja2` imports `create_app` from the wrong module (`server` instead of `application.app`) and contains a duplicate content block; (2) `schemas.py.jinja2` and `test_schemas.py.jinja2` are entirely absent, so `gep --type restapi` never generates `schemas.py` or `test_schemas.py`; (3) two CLI template tests reference a non-existent `main.py.jinja2` (removed by feature 011). The fix is: rewrite the bad template, create the three missing templates, wire `schemas.py` / `test_schemas.py` into `_build_operations`, and delete the two stale CLI tests.

## Technical Context

**Language/Version**: Python 3.13  
**Primary Dependencies**: Jinja2 (template rendering), Pydantic v2 (generated schema model), FastAPI + Starlette (generated test client), pytest + pytest-cov (testing), ruff (lint/format), mypy strict (types), uv (package management)  
**Storage**: Local filesystem — Jinja2 `.jinja2` template files  
**Testing**: pytest + `typer.testing.CliRunner`; 80% coverage gate  
**Target Platform**: macOS / Linux developer workstation  
**Project Type**: CLI code-generation tool (Python library + executable)  
**Performance Goals**: No new performance requirements  
**Constraints**: Templates must be valid Jinja2; generated Python must be ruff-clean and mypy-compliant; template context variables already fixed (`project.python_package`, `routes`)  
**Scale/Scope**: 4 template files + 1 command handler + 1 CLI test file

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I — Clean Architecture in generated projects | ✅ PASS | Templates correct layer placement |
| II — Template-Driven Code Generation | ✅ PASS | All new generated files via Jinja2 templates; `tests/templates/` tests added for new templates |
| III — Full Command Parity | ✅ PASS | `--dry-run` already works; schemas added to output list |
| IV — Python-First Idioms | ✅ PASS | Type hints in generated code; Pydantic v2; ruff + mypy |
| V — Test-First Development | ✅ PASS | RED tests written before implementation in all phases |
| VI — Developer Experience | ✅ PASS | Dry-run shows `schemas.py` in tree; no user-facing UX changes needed |

No gate violations.

## Project Structure

### Documentation (this feature)

```text
specs/012-fix-restapi-test-templates/
├── plan.md          ← this file
├── research.md      ← Phase 0 output
├── data-model.md    ← Phase 1 output
├── quickstart.md    ← Phase 1 output
└── tasks.md         ← /speckit.tasks output (NOT created by /speckit.plan)
```

### Source Code (modified files only)

```text
src/scaffold_ca_python/
├── commands/
│   └── generate_entry_point.py                    ← add schemas.py + test_schemas.py to _build_operations
└── templates/entry_point/restapi/
    ├── test_rest_controller.py.jinja2              ← rewrite (fix import + remove duplicate)
    ├── schemas.py.jinja2                           ← create new
    ├── test_schemas.py.jinja2                      ← create new
    └── router.py.jinja2                            ← create new (supplemental, not in gep output)

tests/
├── commands/
│   └── test_generate_entry_point.py               ← add RED tests for schemas.py + test_schemas.py
└── templates/
    └── test_entry_point_templates.py              ← delete 2 stale tests; add 3 new template tests
```

## Complexity Tracking

No constitution violations. Feature is fully additive + corrective with minimal scope.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]  
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single project (DEFAULT)
src/
├── models/
├── services/
├── cli/
└── lib/

tests/
├── contract/
├── integration/
└── unit/

# [REMOVE IF UNUSED] Option 2: Web application (when "frontend" + "backend" detected)
backend/
├── src/
│   ├── models/
│   ├── services/
│   └── api/
└── tests/

frontend/
├── src/
│   ├── components/
│   ├── pages/
│   └── services/
└── tests/

# [REMOVE IF UNUSED] Option 3: Mobile + API (when "iOS/Android" detected)
api/
└── [same as backend above]

ios/ or android/
└── [platform-specific structure: feature modules, UI flows, platform tests]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
