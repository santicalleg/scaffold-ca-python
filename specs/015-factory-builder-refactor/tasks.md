# Tasks: CLI Factory + Builder Architecture Refactor

**Feature**: `015-factory-builder-refactor`  
**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)  
**Total tasks**: 52 | **User stories**: US1 (P1) · US2 (P1) · US3 (P1) · US4 (P2)

---

## Phase 1 — Setup

Initialize the `factory/` sub-package and `tests/factory/` directory structure so
subsequent phases can add files without creating directories.

- [x] T001 Create `src/scaffold_ca_python/factory/__init__.py` with empty module stub
- [x] T002 Create `src/scaffold_ca_python/factory/entry_points/__init__.py` with empty module stub
- [x] T003 Create `src/scaffold_ca_python/factory/driven_adapters/__init__.py` with empty module stub
- [x] T004 Create `src/scaffold_ca_python/factory/simple/__init__.py` with empty module stub
- [x] T005 [P] Create `tests/factory/__init__.py` empty stub
- [x] T006 [P] Create `tests/factory/entry_points/__init__.py` empty stub
- [x] T007 [P] Create `tests/factory/driven_adapters/__init__.py` empty stub
- [x] T008 [P] Create `tests/factory/simple/__init__.py` empty stub

---

## Phase 2 — Foundational

`ModuleFactory` Protocol and `ModuleBuilder` must exist and be fully tested
before any command file is touched. This phase unblocks all user-story phases.

**Story goal**: Prove the contract and builder work in isolation before wiring
commands.

**Independent test**: `uv run pytest tests/factory/test_module_builder.py --no-cov -q`
must be green; all 487 prior tests must still pass.

- [ ] T009 Define `ModuleFactory` `@runtime_checkable` Protocol with `build(self, builder: ModuleBuilder) -> None` in `src/scaffold_ca_python/factory/__init__.py`
- [ ] T010 Write failing tests for `ModuleBuilder` in `tests/factory/test_module_builder.py` (add_file, delete_file, add_dependency, add_param/get_param, render delegates to TemplateRenderer, persist dry-run returns paths without writing, persist real writes files and injects deps; also test that a factory calling `Path.exists()` inside `build()` executes normally when `dry_run=True` — filesystem reads must not be suppressed)
- [ ] T011 Implement `ModuleBuilder` class in `src/scaffold_ca_python/core/module_builder.py` (constructor, all public methods, internal FileWriter/TemplateRenderer/pyproject_writer collaborators)
- [ ] T012 [P] Run `uv run pytest tests/factory/test_module_builder.py --no-cov -q` and confirm green
- [ ] T013 [P] Run `uv run pytest --no-cov -q` to confirm all 487 prior tests still pass
- [ ] T013b Capture pre-refactor dry-run path snapshots: for each type in `gep` (restapi, agent, mcp, generic) and `gda` (rest-consumer, secrets, generic), run `scaffold <cmd> --type <type> --dry-run` against a temp project and save the sorted path lists as JSON fixtures in `tests/factory/fixtures/dry_run_baseline.json` — this MUST be done before any command file is modified

---

## Phase 3 — US1: Contributor Adds a New Type Without Touching Command Files

**Story goal**: Extract entry-point type-specific logic into four factory classes;
`generate_entry_point.py` becomes thin + registry. Proves US1: a new type is addable
via one factory file + one registry entry.

**Independent test**: `uv run pytest tests/factory/entry_points/ tests/commands/test_generate_entry_point.py --no-cov -q`

- [ ] T014 [US1] Write failing tests for `EntryPointRestApi.build()` in `tests/factory/entry_points/test_ep_restapi.py` (verifies files queued: app.py, server.py, rest_controller, exception_handler, test stubs; add_dependency called with fastapi deps; delete_file called for main.py; scripts param set)
- [ ] T015 [US1] Implement `EntryPointRestApi` in `src/scaffold_ca_python/factory/entry_points/ep_restapi.py` — imports only `ModuleBuilder`, `ModuleFactory`, `Path`, domain models
- [ ] T016 [US1] Write failing tests for `EntryPointAgent.build()` in `tests/factory/entry_points/test_ep_agent.py` (files queued, a2a-sdk dep, kafka/mcp-client flag handling, main.py overwrite)
- [ ] T017 [US1] Implement `EntryPointAgent` in `src/scaffold_ca_python/factory/entry_points/ep_agent.py`
- [ ] T018 [P] [US1] Write failing tests for `EntryPointMcp.build()` in `tests/factory/entry_points/test_ep_mcp.py`
- [ ] T019 [P] [US1] Implement `EntryPointMcp` in `src/scaffold_ca_python/factory/entry_points/ep_mcp.py`
- [ ] T020 [P] [US1] Write failing tests for `EntryPointGeneric.build()` in `tests/factory/entry_points/test_ep_generic.py`
- [ ] T021 [P] [US1] Implement `EntryPointGeneric` in `src/scaffold_ca_python/factory/entry_points/ep_generic.py`
- [ ] T022 [US1] Replace `_ALLOWED_TYPES` tuple with `_REGISTRY: dict[str, type[ModuleFactory]]` in `src/scaffold_ca_python/commands/generate_entry_point.py`; remove all factory/file/dep imports; reduce `_generate_entry_point_impl` to: validate flags → exclusivity guard → build context → lookup factory → construct builder → `factory().build(builder)` → `builder.persist()`
- [ ] T023 [US1] Run `uv run pytest tests/factory/entry_points/ tests/commands/test_generate_entry_point.py --no-cov -q` and confirm all pass

---

## Phase 4 — US2 (partial): Driven-Adapter Factories + Regression Gate

**Story goal**: Migrate `generate_driven_adapter` (the second multi-type command).
Full US2 (all commands produce identical output) is confirmed only at T045 after
all six commands are migrated and the full regression suite passes.

**Independent test**: `uv run pytest tests/commands/ --no-cov -q` — all existing
command tests pass with no modifications.

- [ ] T024 [US2] Write failing tests for `DrivenAdapterRestConsumer.build()` in `tests/factory/driven_adapters/test_da_rest_consumer.py` (files queued, httpx dep, test stub)
- [ ] T025 [US2] Implement `DrivenAdapterRestConsumer` in `src/scaffold_ca_python/factory/driven_adapters/da_rest_consumer.py`
- [ ] T026 [P] [US2] Write failing tests for `DrivenAdapterSecrets.build()` in `tests/factory/driven_adapters/test_da_secrets.py`
- [ ] T027 [P] [US2] Implement `DrivenAdapterSecrets` in `src/scaffold_ca_python/factory/driven_adapters/da_secrets.py`
- [ ] T028 [P] [US2] Write failing tests for `DrivenAdapterGeneric.build()` in `tests/factory/driven_adapters/test_da_generic.py`
- [ ] T029 [P] [US2] Implement `DrivenAdapterGeneric` in `src/scaffold_ca_python/factory/driven_adapters/da_generic.py`
- [ ] T030 [US2] Refactor `src/scaffold_ca_python/commands/generate_driven_adapter.py` to thin + `_REGISTRY`; remove FileWriter/TemplateRenderer/pyproject_writer imports
- [ ] T031 [US2] Run `uv run pytest tests/commands/ --no-cov -q` and confirm zero regressions (no test file modified)

---

## Phase 5 — US3: All Shared Build Operations Through Builder API

**Story goal**: Migrate the four simple commands (`gm`, `guc`, `gh`, `dm`) so every
command in scope uses only `ModuleBuilder`. After this phase, no command file imports
`FileWriter`, `TemplateRenderer`, or `pyproject_writer` directly.

**Independent test**: `uv run pytest tests/factory/simple/ tests/commands/test_generate_model.py tests/commands/test_generate_use_case.py tests/commands/test_generate_helper.py tests/commands/test_delete_module.py --no-cov -q`

- [ ] T032 [US3] Write failing tests for `ModelFactory.build()` in `tests/factory/simple/test_model_factory.py`
- [ ] T033 [US3] Implement `ModelFactory` in `src/scaffold_ca_python/factory/simple/model_factory.py`; refactor `src/scaffold_ca_python/commands/generate_model.py` to use `ModuleBuilder` and add `_REGISTRY: dict[str, type[ModuleFactory]] = {"<type>": ModelFactory}` (FR-006)
- [ ] T034 [P] [US3] Write failing tests for `UseCaseFactory.build()` in `tests/factory/simple/test_use_case_factory.py`
- [ ] T035 [P] [US3] Implement `UseCaseFactory` in `src/scaffold_ca_python/factory/simple/use_case_factory.py`; refactor `src/scaffold_ca_python/commands/generate_use_case.py` and add `_REGISTRY` (FR-006)
- [ ] T036 [P] [US3] Write failing tests for `HelperFactory.build()` in `tests/factory/simple/test_helper_factory.py`
- [ ] T037 [P] [US3] Implement `HelperFactory` in `src/scaffold_ca_python/factory/simple/helper_factory.py`; refactor `src/scaffold_ca_python/commands/generate_helper.py` and add `_REGISTRY` (FR-006)
- [ ] T038 [P] [US3] Write failing tests for `DeleteModuleFactory.build()` in `tests/factory/simple/test_delete_module_factory.py`
- [ ] T039 [P] [US3] Implement `DeleteModuleFactory` in `src/scaffold_ca_python/factory/simple/delete_module_factory.py`; refactor `src/scaffold_ca_python/commands/delete_module.py` and add `_REGISTRY` (FR-006)
- [ ] T040 [US3] Verify FR-007 compliance: assert no file under `src/scaffold_ca_python/factory/` imports `FileWriter`, `TemplateRenderer`, or `pyproject_writer` directly (grep `from scaffold_ca_python.core.file_writer|template_renderer|pyproject_writer` on the factory/ tree must return 0 results); also assert no command file in `src/scaffold_ca_python/commands/` imports those utilities (commands must route through `ModuleBuilder`)
- [ ] T041 [US3] Run `uv run pytest tests/factory/simple/ tests/commands/ --no-cov -q` and confirm all pass

---

## Phase 6 — US4: Type Registry Consolidates All Available Types Per Command

**Story goal**: Confirm registries are the single source of type truth; add
`test_dry_run_parity.py` and the SC-002 extensibility proof test.

**Independent test**: `uv run pytest tests/factory/test_registry.py tests/factory/test_dry_run_parity.py --no-cov -q`

- [ ] T042 [US4] Write `tests/factory/test_registry.py` — assert `_REGISTRY` for `gep` contains exactly {restapi, agent, mcp, generic}; assert `_REGISTRY` for `gda` contains exactly {rest-consumer, secrets, generic}; assert unknown type lookup produces error listing valid keys
- [ ] T043 [US4] Write `tests/factory/test_dry_run_parity.py` — for each type in both commands, compare dry-run preview path set against a captured pre-refactor baseline fixture
- [ ] T044 [US4] Write SC-002 extensibility proof test in `tests/factory/test_extensibility.py` — define a stub factory inline, register it under a new key in a patched `_REGISTRY`, invoke the command with the stub type, assert factory was called; zero existing command files modified

---

## Phase 7 — Polish & Quality Gates

- [ ] T045 Run `uv run pytest` and confirm all tests pass with ≥ 95% coverage
- [ ] T045b Assert template immutability: `git diff HEAD -- src/scaffold_ca_python/templates/` must be empty — no template file modified during implementation (FR-009)
- [ ] T045c Assert model immutability: confirm no new files exist under `src/scaffold_ca_python/models/` beyond the pre-refactor baseline (FR-010)
- [ ] T046 [P] Run `uv run ruff check src/ tests/` and fix any violations
- [ ] T047 [P] Run `uv run ruff format src/ tests/` to normalise formatting
- [ ] T048 [P] Run `uv run mypy src/` and confirm 0 new errors under strict mode

---

## Dependency Graph

```
T001-T008 (Setup)
    └── T009-T013 (Foundational — ModuleFactory + ModuleBuilder)
            ├── T014-T023 (US1 — Entry-point factories + thin gep)
            │       └── T024-T031 (US2 — Driven-adapter factories + thin gda)
            │               └── T032-T041 (US3 — Simple command factories)
            │                       └── T042-T044 (US4 — Registry tests + parity)
            │                               └── T045-T048 (Quality gates)
            └── (T018-T021 parallelise within US1)
            └── (T026-T029 parallelise within US2)
            └── (T034-T039 parallelise within US3)
```

**Critical path**: T001 → T009 → T010 → T011 → T014 → T015 → T022 → T024 → T030 → T032 → T033 → T040 → T042 → T045

---

## Parallel Execution Examples

### Within US1 (after T013)
- T018/T019 (mcp) in parallel with T020/T021 (generic) — different files, no deps

### Within US2 (after T023)
- T026/T027 (secrets) in parallel with T028/T029 (generic) — different files, no deps

### Within US3 (after T031)
- T034/T035, T036/T037, T038/T039 all parallelisable — distinct commands, no deps

### Quality gates (after T044)
- T046, T047, T048 all parallelisable — read-only lint/type checks

---

## Implementation Strategy

**MVP scope**: Phases 1–3 (T001–T023). After T023:
- US1 is fully satisfied: adding a new entry-point type requires only one new file + one
  registry entry
- US3 partial: ModuleBuilder exists and is the only API used by entry-point factories
- All US2 entry-point tests pass

**Incremental delivery**:
1. Phase 1 (Setup, ~30 min) — no logic
2. Phase 2 (Foundational, ~2 h) — TDD `ModuleBuilder`; no command changes yet
3. Phase 3 (US1, ~3 h) — four factories + refactor `gep`; all existing tests must pass
4. Phase 4 (US2, ~2 h) — three factories + refactor `gda`
5. Phase 5 (US3, ~2 h) — four simple factories
6. Phase 6 (US4, ~1 h) — registry + parity tests
7. Phase 7 (Quality, ~30 min) — green gates

**Format validation**: All tasks follow the required format:
`- [ ] T### [P?] [US#?] Description with file path`
