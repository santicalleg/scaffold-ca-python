<!--
## Sync Impact Report

**Version change**: (new) → 1.0.0
**Type**: Initial ratification — all sections are new.

### Added sections
- Core Principles (I–VII)
- Technology Stack
- Governance

### Modified / removed principles
N/A (initial ratification)

### Template alignment
| Template | Status | Notes |
|---|---|---|
| `.specify/templates/plan-template.md` | ✅ Compatible | Constitution Check gate is a feature-level placeholder; no structural update required |
| `.specify/templates/spec-template.md` | ✅ Compatible | Existing structure supports CA and TDD requirements |
| `.specify/templates/tasks-template.md` | ✅ Updated | Removed "tests are OPTIONAL" language to match Principle V (Test-First NON-NEGOTIABLE) |
| `.specify/templates/agent-file-template.md` | ✅ No action needed | No outdated agent-specific references found |

### Deferred items
None — all placeholders resolved.
-->

# scaffold-ca-python Constitution

## Core Principles

### I. Clean Architecture in Generated Projects

Generated projects MUST follow a strict three-layer structure:

- **domain**: `model/` (pure data classes, no I/O) and `usecase/` (orchestration logic,
  depends only on the domain model and abstract ports).
- **infrastructure**: `entry-points/` (inbound adapters — web, messaging, CLI),
  `driven-adapters/` (outbound adapters — DB, HTTP, queues), `helpers/`
  (cross-cutting utilities with no business logic).
- **application**: composition root, dependency wiring, and runtime configuration.

**Dependency Rule (non-negotiable)**: outer layers MUST depend on inner layers; inner
layers MUST NOT import from outer layers. `domain` MUST NOT import from
`infrastructure` or `application`. `infrastructure` MAY import from `domain` only.

The `validate-structure` (`vs`) command MUST detect and report all dependency-rule
violations, flagging every `import` statement that crosses a layer boundary inward.

> **Scope note**: these constraints apply exclusively to projects *generated* by the
> CLI, not to the CLI tool's own source code.

**Rationale**: Enforcing the dependency rule at the tooling level prevents architectural
decay across all generated codebases and mirrors the guarantees provided by
[bancolombia/scaffold-clean-architecture](https://github.com/bancolombia/scaffold-clean-architecture).

---

### II. Template-Driven Code Generation

All source files emitted by any `generate-*` command MUST originate from Jinja2
templates located under `src/scaffold_ca_python/templates/`. Ad-hoc string
concatenation or f-string assembly for generated code is FORBIDDEN.

- Templates MUST be versioned alongside the CLI source.
- Templates MUST have dedicated unit tests that render them with representative inputs
  and assert structural correctness of the output.
- Template context objects MUST be validated via Pydantic models before rendering.

**Rationale**: A single rendering path eliminates inconsistencies between generated
artifacts and makes template changes auditable through standard code review.

---

### III. Full Command Parity with scaffold-clean-architecture

The CLI MUST implement the following commands (with required short aliases), adapted
for Python idioms:

| Command | Alias | Purpose |
|---|---|---|
| `generate-project` | `ca` | Scaffold full CA project (asyncio or sync, pyproject.toml, optional Pydantic models, optional logging setup) |
| `generate-model` | `gm` | Domain model class in `domain/model/` |
| `generate-use-case` | `guc` | Use-case class in `domain/usecase/` |
| `generate-driven-adapter` | `gda` | Driven adapter; types: `sqlalchemy`, `mongodb`, `redis`, `rest-consumer`, `sqs`, `s3`, `kafka`, `secrets`, `generic` |
| `generate-entry-point` | `gep` | Entry point; types: `restapi` (FastAPI), `graphql`, `kafka`, `sqs`, `async-event-handler`, `mcp`, `agent` (A2A), `generic` |
| `generate-helper` | `gh` | Utility helper module in `infrastructure/helpers/` |
| `generate-pipeline` | `gpipe` | CI/CD pipeline files (GitHub Actions) |
| `generate-acceptance-test` | `gat` | Acceptance test scaffold (pytest-bdd) |
| `generate-performance-test` | `gpt` | Performance test scaffold (locust) |
| `validate-structure` | `vs` | Validate CA layer boundaries and dependency rule |
| `delete-module` | `dm` | Safely delete a generated module |
| `update-project` | `up` | Update project dependencies to latest compatible versions |

Every command MUST support a `--dry-run` flag that previews all file changes without
writing to disk.

**Rationale**: Feature parity with the canonical Java/Gradle plugin ensures Python
teams can adopt the same architectural discipline with equivalent tooling.

---

### IV. Python-First Idioms

- Type hints MUST be present on all public interfaces in the CLI codebase.
- `ruff` MUST be the sole linter/formatter; PEP 8 compliance is enforced by CI.
- `mypy` MUST be enabled in strict mode for the CLI codebase.
- Async/await MUST be the default I/O pattern inside generated project skeletons.
- Python 3.13+ is the minimum supported runtime.
- `uv` MUST be used for dependency management, builds, and publishing.

**Rationale**: Enforcing modern Python idioms in both the tool and generated output
keeps the ecosystem coherent and eliminates common sources of technical debt.

---

### V. Test-First Development (NON-NEGOTIABLE)

Tests MUST be written before implementation code. The Red-Green-Refactor cycle is
strictly enforced:

1. Write a failing test that describes the desired behaviour.
2. Obtain explicit or implied acceptance that the test reflects intent.
3. Implement the minimum code to make the test pass.
4. Refactor under green.

- `pytest` is the test framework for the CLI codebase.
- `pytest-cov` MUST enforce a minimum 80% line-coverage gate; CI MUST fail below
  this threshold.
- Every `generate-*` command MUST produce a corresponding test scaffold file inside
  the generated project so that TDD is the default workflow for consumers.

**Rationale**: Testing discipline is non-negotiable because it is the primary quality
gate for a code-generation tool — generated code that ships broken tests undermines
the entire value proposition.

---

### VI. Developer Experience

- Every command MUST emit Rich-formatted output with progress indicators.
- Short aliases MUST be registered for every command (see Principle III table).
- Every command MUST support `--dry-run` to preview changes without writing to disk.
- All error messages MUST include a resolution hint that tells the user what to do
  next (e.g., "Run `scaffold-ca-python vs` to identify layer violations").
- `--help` output for every command MUST include at least one concrete usage example.

**Rationale**: The CLI is a productivity tool; poor UX discourages adoption and
negates the architectural benefits the tool is designed to enforce.

---

### VII. Git Workflow and Branch Naming

All feature branches MUST follow the convention:

```
feature/<branch-name>
```

- The separator MUST be a forward slash (`/`).
- `<branch-name>` MUST use lowercase kebab-case (e.g., `feature/generate-use-case`,
  `feature/jinja-template-engine`, `feature/fastapi-entry-point`).
- No other branch prefixes (`fix/`, `chore/`, `hotfix/`, etc.) are permitted without
  an explicit amendment to this constitution.

**Rationale**: A single enforced branch pattern keeps CI selectors, code-review
automation, and project board filters simple and predictable.

---

## Technology Stack

The following stack applies to the CLI tool itself:

| Concern | Tool |
|---|---|
| CLI framework | Typer |
| Terminal output | Rich |
| Code generation | Jinja2 |
| Package management / build / publish | uv |
| Linting / formatting | ruff |
| Static typing | mypy (strict) |
| Runtime validation (CLI internals) | Pydantic |
| Testing | pytest + pytest-cov |

Generated projects may optionally include any of the driven-adapter or entry-point
dependencies listed in Principle III, installed via `uv` at generation time.

## Governance

- This constitution supersedes all other practices, style guides, and verbal agreements.
- Any amendment MUST be proposed as a pull request against `.specify/memory/constitution.md`,
  include a rationale, and receive at least one explicit approval before merging.
- Version increments follow semantic versioning:
  - **MAJOR**: backward-incompatible governance changes, principle removals, or
    redefinitions that break existing workflows.
  - **MINOR**: new principles, new mandatory sections, or materially expanded guidance.
  - **PATCH**: clarifications, wording improvements, or typo fixes with no semantic change.
- All pull requests MUST include a Constitution Check section in their plan document
  verifying compliance with every applicable principle.
- Compliance reviews MUST occur at the start of each new feature branch and before
  merging to `main`.

**Version**: 1.0.0 | **Ratified**: 2026-03-25 | **Last Amended**: 2026-03-25
