---
description: "Task list for Python Clean Architecture Scaffold"
---

# Tasks: Python Clean Architecture Scaffold

**Input**: Design documents from `/specs/002-scaffold-clean-arch/`
**Branch**: `002-scaffold-clean-arch`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/cli-schema.md ✅, quickstart.md ✅

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies on in-progress work)
- **[Story]**: Which user story this task belongs to (US1–US10 from spec.md)
- All file paths are relative to repository root

---

## Phase 1: Setup

**Purpose**: Project initialization — add missing dependencies, configure package data, create package skeleton

- [ ] T001 Add `jinja2>=3.1` to `[project].dependencies` and `pytest>=8`, `pytest-tmp-dir` to `[project.optional-dependencies].dev`; add `[tool.hatch.build.targets.wheel]` `include` pattern `src/scaffold_ca_python/templates/**` to ship templates as package data in `pyproject.toml`
- [ ] T002 Create package skeleton directories and empty `__init__.py` files: `src/scaffold_ca_python/commands/__init__.py`, `src/scaffold_ca_python/commands/generate/__init__.py`, `src/scaffold_ca_python/core/__init__.py`, and top-level `tests/unit/__init__.py`, `tests/integration/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core engine modules that every command depends on. No command work can begin until T003–T006 are complete.

**⚠️ CRITICAL**: All user story phases depend on T003, T004, T005, and T006 being complete.

- [ ] T003 [P] Implement name normalization in `src/scaffold_ca_python/core/naming.py`: functions `to_snake_case(name: str) -> str`, `to_pascal_case(name: str) -> str`, `validate_name(name: str) -> tuple[str, bool]` (returns normalised name + whether normalisation was applied), and `is_reserved_keyword(name: str) -> bool` using `keyword.iskeyword`; raise `ValueError` with actionable message for reserved keywords or names that cannot be safely normalised
- [ ] T004 [P] Implement `ProjectMarker` dataclass and persistence layer in `src/scaffold_ca_python/core/project.py`: `MARKER_FILE = ".scaffold-ca.json"`, `find_project_root(start: Path) -> Path` (walks up to find marker file; raises `NoProjectError` if not found), `ProjectMarker.load(root: Path)` / `ProjectMarker.save(root: Path)`, `ProjectMarker.register_component(record: ComponentRecord)`, `ProjectMarker.deregister_component(name: str)`; JSON schema matches `contracts/cli-schema.md`; fields: `name`, `base_package`, `mode` (`sync`/`async`), `tool_version`, `components: list[ComponentRecord]`
- [ ] T005 [P] Implement Jinja2 template renderer in `src/scaffold_ca_python/core/renderer.py`: `TemplateRenderer` class using `importlib.resources` to load templates from `scaffold_ca_python.templates`; method `render_to_file(template_path: str, dest: Path, context: dict, force: bool = False)` — raises `FileExistsError` if destination exists and `force` is False, writes parent directories as needed, renders with Jinja2 `Environment(keep_trailing_newline=True)`
- [ ] T006 Update `src/scaffold_ca_python/cli.py` to: (1) add `generate_app = typer.Typer(name="generate", help="Generate a new component")` and `app.add_typer(generate_app)`; (2) add a global `--quiet / --verbose` state via a `typer.callback` that sets a module-level `OutputMode` enum consumed by all commands; (3) remove the placeholder `hello` command; (4) keep the existing `version` command unchanged

**Checkpoint**: Core engine ready — all user story phases can now begin

---

## Phase 3: User Story 1 - Generate a New Project (Priority: P1) 🎯 MVP

**Goal**: `scaffold new --name <name> [--package <pkg>] [--async] [--force]` creates a fully structured, immediately runnable Clean Architecture project

**Independent Test**: Run `scaffold new --name my_app` in a temp directory; verify all 7 layer directories exist with `__init__.py` stubs, `.scaffold-ca.json` is written, `pyproject.toml` is valid, and `pytest` passes inside the generated project

- [ ] T007 [P] [US1] Create all Jinja2 project-skeleton templates under `src/scaffold_ca_python/templates/project/`: `domain/model/__init__.py.j2` (stub), `domain/model/gateways/__init__.py.j2`, `domain/usecase/__init__.py.j2`, `infrastructure/driven_adapters/__init__.py.j2`, `infrastructure/entry_points/__init__.py.j2`, `infrastructure/helpers/__init__.py.j2`, `app/__init__.py.j2`, `app/main.py.j2` (manual DI wiring stub wiring no-op adapters), `deployment/Dockerfile.j2`, `deployment/github_actions.yml.j2`, `pyproject.toml.j2` (generated project's own pyproject, Python 3.13+, pytest dep), `README.md.j2` (layer guide), `tests/__init__.py.j2`, `tests/test_smoke.py.j2` (a test that always passes to satisfy FR-004), `tests/test_architecture.py.j2` (ArchitectureTest per FR-005 — programmatically enforces layer-dependency rules using AST on every test run)
- [ ] T008 [US1] Implement `scaffold new` command in `src/scaffold_ca_python/commands/new.py`: accept `--name` (required), `--package` (optional, default = name), `--async` flag, `--force` flag; extract last dot-segment of `--package` as top-level Python package dir (FR-001); validate and normalise name via `naming.py`; check target directory does not exist (abort unless `--force`); render all `templates/project/` templates via `renderer.py`; write `.scaffold-ca.json` via `project.py`; emit Rich informational output respecting `OutputMode`; register command with `cli.py` app

**Checkpoint**: `scaffold new` fully functional — MVP scope complete

---

## Phase 4: User Story 2 - Generate a Domain Model (Priority: P2)

**Goal**: `scaffold generate model --name <Name>` creates entity stub + gateway interface in `domain/model/`

**Independent Test**: Inside a scaffolded project, `scaffold generate model --name Order` creates `domain/model/order.py` and `domain/model/gateways/order_gateway.py` with correct class names

- [ ] T009 [P] [US2] Create Jinja2 model templates in `src/scaffold_ca_python/templates/model/`: `entity.py.j2` (dataclass entity stub in `domain/model/<snake_name>.py`) and `gateway.py.j2` (abstract gateway interface stub in `domain/model/gateways/<snake_name>_gateway.py`)
- [ ] T010 [US2] Implement `scaffold generate model` command in `src/scaffold_ca_python/commands/generate/model.py`: `--name` (required), `--force`; call `find_project_root()` guard (FR-017); normalise name; render entity + gateway templates; register `ComponentRecord(type="model", ...)` in `.scaffold-ca.json`; emit normalisation notice if applied; register sub-command with `generate_app` in `cli.py`

**Checkpoint**: `scaffold generate model` fully functional

---

## Phase 5: User Story 3 - Generate a Use Case (Priority: P2)

**Goal**: `scaffold generate use-case --name <Name>` creates use case stub in `domain/usecase/`

**Independent Test**: `scaffold generate use-case --name ProcessOrder` creates `domain/usecase/process_order_use_case.py` with no lint errors

- [ ] T011 [P] [US3] Create Jinja2 use-case templates in `src/scaffold_ca_python/templates/use_case/`: `use_case.py.j2` (use case class stub in `domain/usecase/<snake_name>_use_case.py` — imports only from `domain.model`) and `test_use_case.py.j2` (minimal passing pytest stub in generated project's `tests/usecase/test_<snake_name>_use_case.py`)
- [ ] T012 [US3] Implement `scaffold generate use-case` command in `src/scaffold_ca_python/commands/generate/use_case.py`: `--name` (required), `--force`; project-root guard; normalise name; render use-case class + test stub templates; register `ComponentRecord(type="use-case", ...)` in `.scaffold-ca.json`; register sub-command with `generate_app`

**Checkpoint**: `scaffold generate use-case` fully functional

---

## Phase 6: User Story 4 - Generate a Driven Adapter (Priority: P2)

**Goal**: `scaffold generate driven-adapter --type <type> --name <Name>` creates adapter stub in `infrastructure/driven_adapters/` and gateway interface in `domain/model/gateways/` (if absent)

**Independent Test**: `scaffold generate driven-adapter --type repository --name OrderRepo` creates both the domain gateway and the adapter stub; unsupported type exits non-zero with full type catalog

- [ ] T013 [P] [US4] Create Jinja2 driven-adapter templates for all 11 types under `src/scaffold_ca_python/templates/driven_adapter/` — one subdirectory per type (`generic/`, `repository/`, `rest_client/`, `mongodb/`, `redis/`, `dynamo/`, `s3/`, `sqs_sender/`, `kafka_sender/`, `rabbitmq_sender/`, `secrets/`); each subdir contains `adapter.py.j2` (adapter class stub in `infrastructure/driven_adapters/<type>/<snake_name>.py` implementing the gateway protocol) and `gateway.py.j2` (gateway interface stub, skipped if already exists); `rest_client` adapter includes `url` context variable; `redis` adapter includes `mode` context variable
- [ ] T014 [US4] Implement `scaffold generate driven-adapter` command in `src/scaffold_ca_python/commands/generate/driven_adapter.py`: `--type` (required, validated against `ADAPTER_TYPES` set), `--name` (required), `--url` (optional, required when `--type rest-client`), `--mode` (optional, `template|repository`, only for `--type redis`), `--force`; project-root guard; normalise name; render adapter + gateway templates (skip gateway render if gateway file already exists and no `--force`); register component; list all valid types on invalid `--type`; register sub-command with `generate_app`

**Checkpoint**: All 11 driven-adapter types generatable

---

## Phase 7: User Story 5 - Generate an Entry Point (Priority: P2)

**Goal**: `scaffold generate entry-point --type <type> --name <Name>` creates entry point stub in `infrastructure/entry_points/`

**Independent Test**: `scaffold generate entry-point --type rest-api --name OrderApi` creates the entry point stub in `infrastructure/entry_points/rest_api/order_api.py`

- [ ] T015 [P] [US5] Create Jinja2 entry-point templates for all 7 types under `src/scaffold_ca_python/templates/entry_point/` — one subdirectory per type (`generic/`, `rest_api/`, `graphql/`, `kafka_consumer/`, `sqs_listener/`, `async_event_handler/`, `cli/`); each subdir contains `entry_point.py.j2` (entry point class/router stub in `infrastructure/entry_points/<type>/<snake_name>.py`); `async_event_handler` template includes `tech` context variable (`rabbitmq` or `kafka`)
- [ ] T016 [US5] Implement `scaffold generate entry-point` command in `src/scaffold_ca_python/commands/generate/entry_point.py`: `--type` (required, validated against `ENTRY_POINT_TYPES` set), `--name` (required), `--tech` (optional, `rabbitmq|kafka`, only for `--type async-event-handler`), `--force`; project-root guard; normalise name; render entry-point template; register component; list valid types on invalid `--type`; register sub-command with `generate_app`

**Checkpoint**: All 7 entry-point types generatable

---

## Phase 8: User Story 7 - Validate Project Structure (Priority: P2)

**Goal**: `scaffold validate` walks the project, parses imports with AST, and reports all cross-layer dependency violations

**Independent Test**: Introduce `from infrastructure.driven_adapters.repo import Repo` inside `domain/model/order.py`; run `scaffold validate`; verify exit code 1 and the offending file + rule are reported

- [ ] T017 [P] Implement AST import analyser and layer dependency matrix in `src/scaffold_ca_python/core/validator.py`: `LAYER_RULES: dict[str, list[str]]` mapping each layer path prefix to the set of layer prefixes it is allowed to import from (based on FR-011 matrix: `domain/model` allows nothing, `domain/usecase` allows `domain/model`, `infrastructure` allows `domain/`, `app` allows all); `find_layer(file: Path, project_root: Path) -> str | None`; `extract_imports(file: Path) -> list[str]`; `validate_project(project_root: Path) -> list[Violation]` — walks all `.py` files, skips `tests/`, returns list of `Violation(file, import_stmt, rule_broken)` dataclass instances
- [ ] T018 [US7] Implement `scaffold validate` command in `src/scaffold_ca_python/commands/validate.py`: project-root guard; call `validate_project()`; print pass (exit 0) or violation report with file path + offending import + rule broken (exit 1); respect `OutputMode`; register command with `cli.py` app

**Checkpoint**: `scaffold validate` detects 100% of cross-layer violations (SC-005)

---

## Phase 9: User Story 6 - Generate a Helper (Priority: P3)

**Goal**: `scaffold generate helper --name <Name>` creates a helper utility stub in `infrastructure/helpers/`

**Independent Test**: `scaffold generate helper --name JwtHelper` creates `infrastructure/helpers/jwt_helper.py` with correct class name

- [ ] T019 [P] [US6] Create Jinja2 helper template in `src/scaffold_ca_python/templates/helper/`: `helper.py.j2` (helper class stub in `infrastructure/helpers/<snake_name>.py`)
- [ ] T020 [US6] Implement `scaffold generate helper` command in `src/scaffold_ca_python/commands/generate/helper.py`: `--name` (required), `--force`; project-root guard; normalise name; render helper template; register `ComponentRecord(type="helper", ...)`; register sub-command with `generate_app`

**Checkpoint**: `scaffold generate helper` fully functional

---

## Phase 10: User Story 8 - Delete a Module (Priority: P3)

**Goal**: `scaffold delete --module <name>` removes a previously generated component's files and deregisters it from `.scaffold-ca.json`

**Independent Test**: Generate a driven adapter, then `scaffold delete --module order_repo`; verify files removed and component absent from `.scaffold-ca.json`

- [ ] T021 [US8] Implement `scaffold delete` command in `src/scaffold_ca_python/commands/delete.py`: `--module` (required); project-root guard; load `ProjectMarker`; look up component by name (case-insensitive snake_case match); if not found, print error and exit non-zero without touching filesystem; remove all `generated_files` listed in the component record (files + parent directory if empty); call `ProjectMarker.deregister_component()`; report each deleted path; register command with `cli.py` app

**Checkpoint**: `scaffold delete` fully functional

---

## Phase 11: User Story 9 - Update Project (Priority: P3)

**Goal**: `scaffold update` refreshes boilerplate structural files while preserving user-authored code; creates `.bak` backups on conflict

**Independent Test**: Modify `deployment/Dockerfile` manually, run `scaffold update`; verify the `.bak` backup is created, the file is overwritten with the current template output, and the backup is reported in the output

- [ ] T022 [US9] Implement `scaffold update` command in `src/scaffold_ca_python/commands/update.py`: `--skip-git-check` flag; project-root guard; unless `--skip-git-check`, run `git status --porcelain` and warn (not abort) if there are unstaged changes; define `BOILERPLATE_FILES` list (structural files safe to re-render: `deployment/Dockerfile`, `deployment/github_actions.yml`, `app/main.py`, `pyproject.toml` top-level project config sections); for each boilerplate file, compute SHA-256 of on-disk file vs freshly rendered template output; if they differ, write `<file>.bak` before overwriting; re-render from current template; report each updated file (and each `.bak` created); register command with `cli.py` app

**Checkpoint**: `scaffold update` fully functional with conflict-safe backup strategy

---

## Phase 12: User Story 10 - List Component Types (Priority: P3)

**Goal**: `scaffold list [--type driven-adapter|entry-point]` prints a catalogue of all supported component types with descriptions

**Independent Test**: `scaffold list` (no project required) prints all 11 driven-adapter types and all 7 entry-point types with names and short descriptions

- [ ] T023 [US10] Implement `scaffold list` command in `src/scaffold_ca_python/commands/list_components.py`: `--type` (optional, `driven-adapter|entry-point`); **no project-root guard** (FR-014 — discoverability command); define `ADAPTER_CATALOG: dict[str, str]` and `ENTRY_POINT_CATALOG: dict[str, str]` mapping type names to descriptions; print both catalogs (or filtered by `--type`) using Rich `Table`; respect `OutputMode`; register command with `cli.py` app

**Checkpoint**: `scaffold list` fully functional — all P3 user stories complete

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Confirm full CLI wiring, documentation, and packaging completeness

- [ ] T024 [P] Verify complete CLI wiring in `src/scaffold_ca_python/cli.py` and `src/scaffold_ca_python/commands/generate/__init__.py`: confirm `generate_app` contains all 5 generate sub-commands (model, use-case, driven-adapter, entry-point, helper); confirm top-level `app` contains validate, delete, update, list, new, version; confirm `--quiet`/`--verbose` propagates to all commands via `OutputMode`
- [ ] T025 [P] Update `README.md` with installation instructions (`pip install scaffold-ca-python`), full CLI reference for all commands matching `specs/002-scaffold-clean-arch/quickstart.md`, and the 7-layer architecture diagram
- [ ] T026 Update `pyproject.toml` project metadata: set `description`, `keywords`, `classifiers` (Development Status, Intended Audience, License, Programming Language); confirm `[project.scripts]` entry point is `scaffold-ca-python`; confirm `[tool.hatch.build.targets.wheel]` includes `src/scaffold_ca_python/templates/**`

---

## Dependencies

```
T001 → T002 → T003, T004, T005, T006
T003, T004, T005, T006 → T007, T008, T009, T010, T011, T012, T013, T014, T015, T016, T017, T018, T019, T020, T021, T022, T023
T007 → T008
T009 → T010
T011 → T012
T013 → T014
T015 → T016
T017 → T018
T019 → T020
T010, T012, T014, T016, T018, T020, T021, T022, T023 → T024
T024 → T025, T026
```

### Story Completion Order

```
Phase 3 (US1) → Phase 4 (US2)
              → Phase 5 (US3)
              → Phase 6 (US4)
              → Phase 7 (US5)
              → Phase 8 (US7)
              → Phase 9 (US6)
              → Phase 10 (US8)
              → Phase 11 (US9)
              → Phase 12 (US10)
```

US2–US7 are **independent** — they can be implemented in any order once Phase 2 is complete.  
US8 (delete) depends on components existing in `.scaffold-ca.json`, implying at least US2 or US4 should be done first (for a meaningful end-to-end test).  
US9 (update) requires boilerplate templates from US1 to exist.

---

## Parallel Execution Examples

### After T002 is done (Phase 2 parallelisation)

All of T003, T004, T005 can run simultaneously:
```
T003: core/naming.py   ← different file
T004: core/project.py  ← different file
T005: core/renderer.py ← different file
```
T006 should follow once T003–T005 are done (modifies cli.py, reads the core modules to understand OutputMode needs).

### After Phase 2 (US template + command pairs)

Template creation and command implementation are **not** parallel within a single user story (command depends on template paths), but different user story pairs are independent:

```
T007 then T008  (US1)
T009 then T010  (US2) ─┐
T011 then T012  (US3) ─┤  all can be done in any order
T013 then T014  (US4) ─┤
T015 then T016  (US5) ─┤
T017 then T018  (US7) ─┤
T019 then T020  (US6) ─┘
T021            (US8)
T022            (US9)
T023            (US10)
```

---

## Implementation Strategy

**MVP scope**: Complete Phases 1–3 (T001–T008) first. This delivers a working `scaffold new` that satisfies SC-001 and proves the entire template rendering and project-marker pipeline end-to-end.

**Increment 1 (P2 stories)**: T009–T018. Delivers all `generate` sub-commands for models, use cases, adapters, and entry points, plus `validate`. This is the production-ready feature set.

**Increment 2 (P3 stories)**: T019–T023. Delivers helpers, delete, update, and list — completing the full command surface.

**Increment 3 (Polish)**: T024–T026. Confirms wiring, finalises docs and packaging.

---

## Summary

| Metric | Value |
|---|---|
| Total tasks | 26 |
| Phase 1 (Setup) | 2 tasks |
| Phase 2 (Foundational) | 4 tasks |
| Phase 3 US1 (P1 MVP) | 2 tasks |
| Phase 4 US2 | 2 tasks |
| Phase 5 US3 | 2 tasks |
| Phase 6 US4 | 2 tasks |
| Phase 7 US5 | 2 tasks |
| Phase 8 US7 | 2 tasks |
| Phase 9 US6 | 2 tasks |
| Phase 10 US8 | 1 task |
| Phase 11 US9 | 1 task |
| Phase 12 US10 | 1 task |
| Final Phase (Polish) | 3 tasks |
| Parallelisable tasks [P] | 14 tasks |
| User stories covered | 10 (US1–US10) |
| MVP scope | T001–T008 (Phases 1–3) |
