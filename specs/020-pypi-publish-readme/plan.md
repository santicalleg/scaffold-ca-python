# Implementation Plan: PyPI Publishing & README Documentation

**Branch**: `020-pypi-publish-readme` | **Date**: 2026-04-20 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/020-pypi-publish-readme/spec.md`

## Summary

Add all required PyPI metadata fields to `pyproject.toml` (`license`, `keywords`, `classifiers`, `[project.urls]`, named `authors`) and rewrite `README.md` with a complete documentation structure covering description, installation, usage examples for all CLI commands, technologies, features, contributing guide, and license. No code changes to the CLI itself — this feature is purely configuration + documentation. Build tooling: `uv build` (hatchling backend) + `uv publish`.

## Technical Context

**Language/Version**: Python 3.13+
**Primary Dependencies**: hatchling (build backend), uv-dynamic-versioning (git-tag versioning, PEP 440), uv (build + publish)
**Storage**: N/A — pyproject.toml (TOML) and README.md (Markdown) edits only
**Testing**: pytest + pytest-cov (≥80% gate); `uv build` smoke-test to confirm artifact production; no new test files needed (no logic added)
**Target Platform**: PyPI distribution; installable on Python 3.13+ / Linux, macOS, Windows
**Project Type**: CLI tool (published to PyPI as `scaffold-ca-python`)
**Performance Goals**: N/A
**Constraints**: README Markdown must render correctly on both GitHub and PyPI (no relative image links; standard Markdown only); `uv-dynamic-versioning` config must remain untouched
**Scale/Scope**: 2 files modified (`pyproject.toml`, `README.md`); 0 new source files; 1 new artifact directory (`dist/`)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I — Clean Architecture in Generated Projects** | ✅ N/A | No changes to generated project structure or templates. |
| **II — Template-Driven Code Generation** | ✅ N/A | No new templates or generated files. |
| **III — Full Command Parity** | ✅ N/A | No new CLI commands or command changes. |
| **IV — Python-First Idioms** | ✅ PASS | `uv` is the mandated build/publish tool per Principle IV. SPDX license field and classifiers follow PEP 566 conventions. |
| **V — Test-First Development** | ✅ PASS | No implementation logic added; no new tests required. Existing 80% coverage gate is unaffected. A `uv build` smoke-test in the task list validates artifact production. |
| **VI — Developer Experience** | ✅ PASS | README enables a developer to onboard in ≤5 minutes (SC-004). |
| **VII — Branch Naming** | ✅ PASS | Branch `020-pypi-publish-readme` follows the flat `NNN-kebab-name` convention. |

## Project Structure

### Documentation (this feature)

```text
specs/020-pypi-publish-readme/
├── plan.md              ← this file
├── research.md          ← Phase 0 output
├── data-model.md        ← Phase 1 output (pyproject.toml field schema)
├── contracts/
│   └── readme-outline.md  ← Phase 1 output (README section contract)
├── quickstart.md        ← Phase 1 output (build + publish workflow)
└── tasks.md             ← Phase 2 output (/speckit.tasks)
```

### Source Code Changes

```text
pyproject.toml               ← MODIFIED: add license, keywords, classifiers, [project.urls], author name
README.md                    ← MODIFIED: full rewrite with all required sections
```

No changes to `src/`, `tests/`, or any template files.

## Complexity Tracking

No constitution violations. No complexity justification needed.
