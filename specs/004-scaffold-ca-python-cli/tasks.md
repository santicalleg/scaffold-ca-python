# Tasks: scaffold-ca-python CLI

**Input**: Design documents from `specs/004-scaffold-ca-python-cli/`
**Prerequisites**: plan.md ✅ | spec.md ✅ | research.md ✅ | data-model.md ✅ | contracts/ (10 files) ✅ | quickstart.md ✅

**Tests**: TDD is **NON-NEGOTIABLE** per Constitution Principle V. Every test task MUST be completed (and confirmed failing) BEFORE the corresponding implementation task begins.

**Spec US-9 (Dry-Run Preview) traceability**: This cross-cutting story has no dedicated task block. Coverage is distributed: `--dry-run` behavior is tested per-command inside each `[USx]` test task (e.g., T025, T034, T039, T044, T050, T062, T066, T071, T074); SC-007 checksum verification → T090. `vs --dry-run` is a no-op (read-only command) per spec US-9 scenario 3 → tested in T058.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

---

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel with other [P] tasks at the same phase level (operates on a different file or directory)
- **[Story]**: Which user story this task belongs to ([US1]–[US10])
- Every task includes an exact file path
- Setup and Foundational phases carry no story label

---

## Phase 1: Setup

**Purpose**: Configure the tool project itself — dependencies, toolchain, entry points, and the minimal CLI skeleton. These tasks are prerequisites for everything else.

- [X] T001 Add missing runtime dependencies (jinja2, pydantic>=2, pyyaml) to `[project.dependencies]` in pyproject.toml
- [X] T002 Create full source and test directory skeleton with `__init__.py` files: `src/scaffold_ca_python/{commands,core,models,templates}` and `tests/{commands,core,models,templates}` in the repository root
- [X] T003 [P] Add `[tool.ruff]` configuration (line-length=120, select=["E","F","I","UP","ANN"], target-version="py313") to pyproject.toml
- [X] T004 [P] Add `[tool.mypy]` strict configuration (strict=true, python_version="3.13") to pyproject.toml
- [X] T005 [P] Add `[tool.pytest.ini_options]` with `addopts = "--cov=scaffold_ca_python --cov-fail-under=80"` and `[tool.coverage.run]` source list to pyproject.toml
- [X] T006 Add `[tool.hatch.build.targets.wheel]` block declaring `packages = ["src/scaffold_ca_python"]` and `[tool.hatch.build.targets.wheel.force-include]` glob for `templates/**` to pyproject.toml
- [X] T007 Add `scaffold = "scaffold_ca_python.cli:app"` alias under `[project.scripts]` (alongside the existing `scaffold-ca-python` entry) in pyproject.toml
- [X] T008 Refactor `src/scaffold_ca_python/cli.py` to accept `register(app)` calls from each command module, remove the placeholder `version` command, and keep the Typer app as the sole exported symbol

**Checkpoint**: `uv sync` installs cleanly, `scaffold --help` shows an empty app, and all tool configs pass `ruff check .` and `mypy src/`.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models and engine components that every command depends on. No user story work can begin until this phase is complete.

> ⚠️ CRITICAL: Write ALL tests first (T009–T020); confirm each test file is importable and fails; then implement (T021–T024 models, T025–T028 core).
>
> **NOTE: Write tests FIRST, confirm they FAIL before implementation.**

### Model Tests *(write these BEFORE model implementations)*

- [X] T009 [P] Write tests for `Layer` enum: 6 values, `FORBIDDEN_IMPORTS` mapping, inner→outer detection logic in tests/models/test_layer.py
- [X] T010 [P] Write tests for `ProjectContext` and `ModuleContext`: field validation, `python_package` derivation, `^[A-Za-z][A-Za-z0-9_]*$` constraint in tests/models/test_context.py
- [X] T011 [P] Write tests for `GeneratedFile`, `CreateFile`, `DeleteFile`, and `FileOperation` union: field presence, `is_test` flag, `kind` discriminator in tests/models/test_file_operation.py
- [X] T012 [P] Write tests for `Violation` and `ValidationReport`: field population, `passed` property True/False, `files_scanned` counter in tests/models/test_violation.py

### Model Implementations

- [X] T013 [P] Implement `Layer` enum (6 values: DOMAIN_MODEL, DOMAIN_USECASE, ENTRY_POINTS, DRIVEN_ADAPTERS, HELPERS, APPLICATION) and `FORBIDDEN_IMPORTS` dependency dict in src/scaffold_ca_python/models/layer.py
- [X] T014 [P] Implement `ProjectContext` and `ModuleContext` as Pydantic v2 `BaseModel` with `@field_validator` for name and `@computed_field` for derived names in src/scaffold_ca_python/models/context.py
- [X] T015 [P] Implement `GeneratedFile`, `CreateFile`, `DeleteFile`, and `FileOperation = CreateFile | DeleteFile` union type in src/scaffold_ca_python/models/file_operation.py
- [X] T016 [P] Implement `Violation` and `ValidationReport` Pydantic v2 models with `@property passed` in src/scaffold_ca_python/models/violation.py

### Core Tests *(write these BEFORE core implementations)*

- [X] T017 [P] Write tests for `name_utils`: `to_snake_case`, `to_pascal_case`, `validate_name` regex accept/reject cases and normalisation in tests/core/test_name_utils.py
- [X] T018 [P] Write tests for `project_detector`: finds root when `[tool.scaffold-ca-python]` exists in parent pyproject.toml, raises `ScaffoldError` when not found, fallback to CA directory layout in tests/core/test_project_detector.py
- [X] T019 [P] Write tests for `FileWriter`: atomic create via `os.replace`, dry-run emits no disk writes, `DeleteFile` removes path+mirror, rollback on render error leaves no partial files in tests/core/test_file_writer.py
- [X] T020 [P] Write tests for `TemplateRenderer`: loads templates via `importlib.resources.files`, renders a fixture template with a `ProjectContext`, raises on missing template name in tests/core/test_template_renderer.py

### Core Implementations

- [X] T021 [P] Implement `to_snake_case`, `to_pascal_case`, and `validate_name` (raises `ScaffoldError` on regex mismatch) in src/scaffold_ca_python/core/name_utils.py
- [X] T022 [P] Implement `find_project_root`: walk `cwd` upward checking for `pyproject.toml` containing `[tool.scaffold-ca-python]`; fallback to CA directory markers; raise `ScaffoldError` if neither found in src/scaffold_ca_python/core/project_detector.py
- [X] T023 Implement `FileWriter` with `execute(operations: list[FileOperation], dry_run: bool)`: real mode uses tempdir staging + `os.replace` (R-06); dry-run mode returns preview list without touching disk in src/scaffold_ca_python/core/file_writer.py
- [X] T024 Implement `TemplateRenderer` with `importlib.resources.files("scaffold_ca_python.templates")` Jinja2 loader (R-05) and `render(template_name: str, context: BaseModel) -> str` using `context.model_dump()` spread (R-07) in src/scaffold_ca_python/core/template_renderer.py

**Checkpoint**: `pytest tests/models/ tests/core/` passes at 100%. Foundation is solid — user story implementation can now begin.

---

## Phase 3: User Story 1 — Project Bootstrapping (Priority: P1) 🎯 MVP

**Goal**: `scaffold ca --name MyProject --package com.acme` creates a fully working Clean Architecture skeleton in a new directory. This is the deliverable MVP.

**Independent Test**: Running the command on an empty directory produces a `my_project/` tree with all 6 layers, each containing `__init__.py`. Running `uv sync` inside it completes without errors.

> ⚠️ **Write T025 first. Confirm it fails. Then create templates T026–T031. Then implement T032.**

### Tests for User Story 1 *(write BEFORE implementation)*

- [X] T025 [P] [US1] Write tests for `ca`/`generate-project` command via Typer `CliRunner`: success creates all layer dirs + 6 config files, `--dry-run` writes nothing to disk, duplicate project name exits code 1 in tests/commands/test_generate_project.py

### Templates for User Story 1

- [X] T026 [P] [US1] Create `project/pyproject_toml.jinja2` rendering a `pyproject.toml` with `[tool.scaffold-ca-python]` metadata section in src/scaffold_ca_python/templates/project/
- [X] T027 [P] [US1] Create `project/README.jinja2` with async-first project description placeholder in src/scaffold_ca_python/templates/project/
- [X] T028 [P] [US1] Create `project/gitignore.jinja2` with standard Python, venv, coverage, and IDE patterns in src/scaffold_ca_python/templates/project/
- [X] T029 [P] [US1] Create `project/ruff_toml.jinja2` rendering to `ruff.toml` in generated projects (line-length=120, target-version=py313, select rules) in src/scaffold_ca_python/templates/project/
- [X] T030 [P] [US1] Create `project/mypy_ini.jinja2` rendering to `mypy.ini` in generated projects (`strict = True`, `python_version = 3.13`) in src/scaffold_ca_python/templates/project/
- [X] T031 [P] [US1] Create `project/layer_init.jinja2` reusable template for every layer `__init__.py` stub in src/scaffold_ca_python/templates/project/

### Implementation for User Story 1

- [X] T032 [US1] Implement `_generate_project_impl(name, package, dry_run)`: build `ProjectContext`, render all project templates, stage 6-layer directory tree + config files, delegate to `FileWriter` in src/scaffold_ca_python/commands/generate_project.py
- [X] T033 [US1] Register `ca` (hidden alias) and `generate-project` commands using the dual-wrapper pattern (R-01) via `register(app)` in src/scaffold_ca_python/commands/generate_project.py; call `register(app)` in src/scaffold_ca_python/cli.py

**Checkpoint**: `scaffold ca --name OrderService --package com.acme` on an empty dir produces a complete skeleton. `scaffold ca --dry-run` prints the file tree and writes nothing. Running `scaffold ca` twice on the same dir exits 1.

---

## Phase 4: User Story 2 — Domain Model (P2) + User Story 3 — Use Case (P3)

**Goal**: `scaffold gm --name Order` creates a typed Pydantic model and test stub. `scaffold guc --name CreateOrder` creates an async use case class with an injectable constructor and test stub.

**Independent Tests**:
- US-2: `scaffold gm --name Product` creates `src/<pkg>/domain/model/product.py` and `tests/domain/model/test_product.py`. Running `pytest` discovers the test file.
- US-3: `scaffold guc --name CreateOrder` creates `src/<pkg>/domain/usecase/create_order_use_case.py` and `tests/domain/usecase/test_create_order_use_case.py`. Both files are syntactically valid Python.

> ⚠️ US-2 stream (T034→T038) and US-3 stream (T039→T043) can proceed **in parallel** by different contributors. Within each stream, tests must precede implementation.

### Tests for User Story 2 *(write BEFORE implementation)*

- [X] T034 [P] [US2] Write tests for `gm`/`generate-model` via CliRunner: success creates model file + test mirror in correct paths, `--dry-run` writes nothing, duplicate name exits 1, no-project-root exits 1 in tests/commands/test_generate_model.py

### Templates for User Story 2

- [X] T035 [P] [US2] Create `model/model.py.jinja2`: Pydantic v2 `BaseModel` subclass with `class_name` and docstring placeholder in src/scaffold_ca_python/templates/model/
- [X] T036 [P] [US2] Create `model/test_model.py.jinja2`: pytest stub with one `test_<module_name>_can_be_instantiated` test in src/scaffold_ca_python/templates/model/

### Implementation for User Story 2

- [X] T037 [US2] Implement `_generate_model_impl(name, dry_run)`: build `ModuleContext(layer=Layer.DOMAIN_MODEL)`, render `model.py.jinja2` + `test_model.py.jinja2`, delegate to `FileWriter` in src/scaffold_ca_python/commands/generate_model.py
- [X] T038 [US2] Register `gm` (hidden alias) and `generate-model` commands via `register(app)` in src/scaffold_ca_python/commands/generate_model.py; call `register(app)` in src/scaffold_ca_python/cli.py

### Tests for User Story 3 *(write BEFORE implementation)*

- [X] T039 [P] [US3] Write tests for `guc`/`generate-use-case` via CliRunner: success creates `<name>_use_case.py` + test mirror, `--dry-run` writes nothing, duplicate exits 1, no-project-root exits 1 in tests/commands/test_generate_use_case.py

### Templates for User Story 3

- [X] T040 [P] [US3] Create `use_case/use_case.py.jinja2`: async use case class with `__init__(self)` accepting injected port arguments and `async def execute(self) -> None: raise NotImplementedError` in src/scaffold_ca_python/templates/use_case/
- [X] T041 [P] [US3] Create `use_case/test_use_case.py.jinja2`: pytest async stub with `pytest.mark.asyncio` decorator and one pending test in src/scaffold_ca_python/templates/use_case/

### Implementation for User Story 3

- [X] T042 [US3] Implement `_generate_use_case_impl(name, dry_run)`: build `ModuleContext(layer=Layer.DOMAIN_USECASE)` with `module_name = "<snake>_use_case"`, render templates, delegate to `FileWriter` in src/scaffold_ca_python/commands/generate_use_case.py
- [X] T043 [US3] Register `guc` (hidden alias) and `generate-use-case` commands via `register(app)` in src/scaffold_ca_python/commands/generate_use_case.py; call `register(app)` in src/scaffold_ca_python/cli.py

**Checkpoint**: US-2 — `scaffold gm --name Order` creates both files; `pytest tests/domain/model/` discovers the stub. US-3 — `scaffold guc --name PlaceOrder` creates both files; `pytest tests/domain/usecase/` discovers the async stub.

---

## Phase 5: User Story 4 — Driven Adapter (Priority: P4)

**Goal**: `scaffold gda --type rest-consumer` creates an async httpx-based adapter module in `infrastructure/driven_adapters/rest_consumer/` with `__init__.py`, implementation file, and test stub.

**Independent Test**: Running `scaffold gda --type rest-consumer` produces the three files. Running `scaffold gda --type generic` without `--name` exits 1 with a resolution hint. Running `scaffold gda --type generic --name CacheStore` produces a `cache_store` adapter.

> ⚠️ **Write T044 first. Confirm it fails. Then create templates T045–T047. Then implement T048.**

### Tests for User Story 4 *(write BEFORE implementation)*

- [X] T044 [P] [US4] Write tests for `gda`/`generate-driven-adapter` via CliRunner: `rest-consumer` type, `secrets` type, `generic` type success, `generic` without `--name` exits 1, duplicate adapter directory exits 1, no-project-root exits 1 in tests/commands/test_generate_driven_adapter.py

### Templates for User Story 4

- [X] T045 [P] [US4] Create `driven_adapter/rest_consumer/` templates: `__init__.py.jinja2`, `rest_consumer.py.jinja2` (async `httpx.AsyncClient` adapter), `test_rest_consumer.py.jinja2` (pytest stub with `respx` mock placeholder) in src/scaffold_ca_python/templates/driven_adapter/rest_consumer/
- [X] T046 [P] [US4] Create `driven_adapter/secrets/` templates: `__init__.py.jinja2`, `secrets_adapter.py.jinja2` (async secrets-store interface), `test_secrets_adapter.py.jinja2` in src/scaffold_ca_python/templates/driven_adapter/secrets/
- [X] T047 [P] [US4] Create `driven_adapter/generic/` templates: `__init__.py.jinja2`, `adapter.py.jinja2` (empty async adapter using `class_name`), `test_adapter.py.jinja2` in src/scaffold_ca_python/templates/driven_adapter/generic/

### Implementation for User Story 4

- [X] T048 [US4] Implement `_generate_driven_adapter_impl(type_, name, dry_run)`: validate `--name` required for `generic` type (exit 1 with hint if missing), dispatch template set by type, build `ModuleContext(layer=Layer.DRIVEN_ADAPTERS)`, delegate to `FileWriter` in src/scaffold_ca_python/commands/generate_driven_adapter.py
- [X] T049 [US4] Register `gda` (hidden alias) and `generate-driven-adapter` commands via `register(app)` in src/scaffold_ca_python/commands/generate_driven_adapter.py; call `register(app)` in src/scaffold_ca_python/cli.py

**Checkpoint**: All three adapter types create correct file structures. `gda --type generic` without `--name` exits 1 with a readable hint. `vs` on the generated project still exits 0 (adapters live in infrastructure, correct layer).

---

## Phase 6: User Story 5 — Entry Point (Priority: P5)

**Goal**: `scaffold gep --type restapi` creates a FastAPI async skeleton immediately (no extra flags); `--swagger` generates typed routes from an OpenAPI spec; `--type agent` supports `--enable-kafka` / `--enable-mcp-client` composition flags.

**Independent Test**: `scaffold gep --type restapi` produces `main.py`, `router.py`, `health.py`, `schemas.py`, and `test_router.py` with no additional configuration. `scaffold gep --type mcp` produces `server.py` and `test_server.py`.

> ⚠️ **Write T050 first. Confirm it fails. Then create templates T051–T054. Then implement T055.**

### Tests for User Story 5 *(write BEFORE implementation)*

- [ ] T050 [P] [US5] Write tests for `gep`/`generate-entry-point` via CliRunner: all 4 types produce correct file sets, `--swagger path/to/spec.yaml` reads the file and injects route count into context, `--enable-kafka` flag included in agent templates, `--enable-mcp-client` flag included, duplicate dir exits 1, no-project-root exits 1 in tests/commands/test_generate_entry_point.py

### Templates for User Story 5

- [ ] T051 [P] [US5] Create `entry_point/restapi/` templates: `__init__.py.jinja2`, `main.py.jinja2` (FastAPI app factory), `router.py.jinja2` (APIRouter with async example route), `health.py.jinja2` (`/health` endpoint), `schemas.py.jinja2` (request/response Pydantic models; also used when `--swagger` injects generated schemas), `test_router.py.jinja2` in src/scaffold_ca_python/templates/entry_point/restapi/
- [ ] T052 [P] [US5] Create `entry_point/agent/` templates: `__init__.py.jinja2`, `agent.py.jinja2` (A2A async handler stub with optional Kafka consumer block, optional MCP client block gated on Jinja2 `if enable_kafka` / `if enable_mcp_client`), `card.py.jinja2` (AgentCard definition), `test_agent.py.jinja2` in src/scaffold_ca_python/templates/entry_point/agent/
- [ ] T053 [P] [US5] Create `entry_point/mcp/` templates: `__init__.py.jinja2`, `server.py.jinja2` (MCP server stubs for tools, resources, prompts), `test_server.py.jinja2` in src/scaffold_ca_python/templates/entry_point/mcp/
- [ ] T054 [P] [US5] Create `entry_point/generic/` templates: `__init__.py.jinja2`, `handler.py.jinja2` (empty async handler), `test_handler.py.jinja2` in src/scaffold_ca_python/templates/entry_point/generic/

### Implementation for User Story 5

- [ ] T055 [US5] Implement `_generate_entry_point_impl(type_, swagger, enable_kafka, enable_mcp_client, dry_run)`: parse `--swagger` file (json/pyyaml) and inject `routes` into Jinja2 context if provided, build `ModuleContext(layer=Layer.ENTRY_POINTS, subtype=type_)`, pass `enable_kafka`/`enable_mcp_client` booleans in context dict, dispatch template set by type, delegate to `FileWriter` in src/scaffold_ca_python/commands/generate_entry_point.py
- [ ] T056 [US5] Register `gep` (hidden alias) and `generate-entry-point` commands via `register(app)` in src/scaffold_ca_python/commands/generate_entry_point.py; call `register(app)` in src/scaffold_ca_python/cli.py

**Checkpoint**: `scaffold gep --type restapi` produces a syntactically valid FastAPI app. `scaffold gep --type agent --enable-kafka` includes a Kafka consumer block. `scaffold vs` on the project still exits 0.

---

## Phase 7: User Story 6 — Structure Validation (Priority: P6)

**Goal**: `scaffold vs` scans all `.py` files under `src/` using Python's `ast` module and reports any cross-layer dependency violations (inner layer importing outer layer), exiting with code 1 if any are found.

**Independent Test**: `scaffold vs` on a freshly generated project exits 0. Adding `from my_project.infrastructure.driven_adapters.rest_consumer import ...` inside `domain/model/order.py` and re-running exits 1 with the exact file, line number, and import statement identified.

> ⚠️ **Write T057–T058 first. Confirm both fail. Then implement T059–T061.**

### Tests for User Story 6 *(write BEFORE implementation)*

- [ ] T057 [P] [US6] Write unit tests for `StructureValidator`: clean project fixture returns `ValidationReport(violations=[])`, domain→infrastructure violation returns `Violation` with correct `source_file`, `line_number`, `import_statement`, `source_layer`, `target_layer`; intra-layer imports do not raise violations in tests/core/test_structure_validator.py
- [ ] T058 [P] [US6] Write integration tests for `vs`/`validate-structure` command via CliRunner: exits 0 on clean project, exits 1 on project with known violation, `--dry-run` produces the same output and exit code as a normal run (since `vs` is read-only, `--dry-run` is a no-op per spec US-9 scenario 3), Rich table output contains file path and line number in tests/commands/test_validate_structure.py

### Implementation for User Story 6

- [ ] T059 [US6] Implement `StructureValidator.validate(project_root: Path) -> ValidationReport`: walk `src/` recursively, `ast.parse()` each `.py` file, walk `ast.Import` and `ast.ImportFrom` nodes (R-08), map module prefix to `Layer`, check against `FORBIDDEN_IMPORTS` dict, collect `Violation` for each breach in src/scaffold_ca_python/core/structure_validator.py
- [ ] T060 [US6] Implement `validate_structure` command: call `StructureValidator.validate()`, render Rich `Table` with violation rows (file, line, import, hint), print success panel or violation table, `raise typer.Exit(code=1)` when `not report.passed` (R-04) in src/scaffold_ca_python/commands/validate_structure.py
- [ ] T061 [US6] Register `vs` (hidden alias) and `validate-structure` commands via `register(app)` in src/scaffold_ca_python/commands/validate_structure.py; call `register(app)` in src/scaffold_ca_python/cli.py

**Checkpoint**: `scaffold vs` on a clean project: exits 0, prints "✓ Validated N files — no violations found." Introducing a domain→infrastructure import: exits 1, table identifies the exact violation with a resolution hint. Usable as a CI gate.

---

## Phase 8: User Story 7 — Helper (P7) + User Story 8 — CI/CD Pipeline (P8)

**Goal**: `scaffold gh --name LoggingHelper` creates a helper module in `infrastructure/helpers/` with a test stub; `scaffold gpipe --provider github` creates `.github/workflows/ci.yml` with lint, type-check, and test steps.

**Independent Tests**:
- US-7: `scaffold gh --name DateUtils` creates `infrastructure/helpers/date_utils/` with `date_utils.py` stub and `test_date_utils.py`.
- US-8: `scaffold gpipe --provider github` creates `.github/workflows/ci.yml`. `scaffold gpipe --provider azure` creates `azure-pipelines.yml`. Running without `--provider` exits 1.

> ⚠️ US-7 stream (T062→T065) and US-8 stream (T066→T070) can proceed **in parallel** by different contributors.

### Tests for User Story 7 *(write BEFORE implementation)*

- [ ] T062 [P] [US7] Write tests for `gh`/`generate-helper` via CliRunner: success creates `infrastructure/helpers/<name>/` dir with implementation file + `__init__.py` + test mirror, `--dry-run` writes nothing, duplicate exits 1, no-project-root exits 1 in tests/commands/test_generate_helper.py

### Templates for User Story 7

- [ ] T063 [P] [US7] Create `helper/` templates: `__init__.py.jinja2`, `helper.py.jinja2` (empty class stub using `class_name`), `test_helper.py.jinja2` (pytest stub) in src/scaffold_ca_python/templates/helper/

### Implementation for User Story 7

- [ ] T064 [US7] Implement `_generate_helper_impl(name, dry_run)`: build `ModuleContext(layer=Layer.HELPERS)`, create `infrastructure/helpers/<module_name>/` subdirectory, render three templates, delegate to `FileWriter` in src/scaffold_ca_python/commands/generate_helper.py
- [ ] T065 [US7] Register `gh` (hidden alias) and `generate-helper` commands via `register(app)` in src/scaffold_ca_python/commands/generate_helper.py; call `register(app)` in src/scaffold_ca_python/cli.py

### Tests for User Story 8 *(write BEFORE implementation)*

- [ ] T066 [P] [US8] Write tests for `gpipe`/`generate-pipeline` via CliRunner: `github` provider creates `.github/workflows/ci.yml`, `azure` provider creates `azure-pipelines.yml`, missing `--provider` exits 1 with resolution hint listing both providers, duplicate pipeline file exits 1 in tests/commands/test_generate_pipeline.py

### Templates for User Story 8

- [ ] T067 [P] [US8] Create `pipeline/github/ci.yml.jinja2`: GitHub Actions workflow with `ruff check`, `mypy src/`, `pytest --cov --cov-fail-under=80` steps using `project.python_version` in src/scaffold_ca_python/templates/pipeline/github/
- [ ] T068 [P] [US8] Create `pipeline/azure/azure_pipelines.yml.jinja2`: Azure Pipelines YAML with equivalent lint, type-check, and coverage-gated test steps in src/scaffold_ca_python/templates/pipeline/azure/

### Implementation for User Story 8

- [ ] T069 [US8] Implement `_generate_pipeline_impl(provider, dry_run)`: validate provider is one of `{github, azure}`, resolve output path (`.github/workflows/ci.yml` vs `azure-pipelines.yml`), detect conflict, render template with `ProjectContext`, delegate to `FileWriter` in src/scaffold_ca_python/commands/generate_pipeline.py
- [ ] T070 [US8] Register `gpipe` (hidden alias) and `generate-pipeline` commands via `register(app)` in src/scaffold_ca_python/commands/generate_pipeline.py; call `register(app)` in src/scaffold_ca_python/cli.py

**Checkpoint**: US-7 — `scaffold gh --name Metrics` creates correct helper structure; `vs` still exits 0. US-8 — `scaffold gpipe --provider github` creates a valid YAML; running without `--provider` shows both valid options.

---

## Phase 9: User Story 9 — Safe Deletion (P9) + User Story 10 — Update Dependencies (P10)

**Goal**: `scaffold dm --name OrderRepository` shows a dry-run preview by default; `--confirm` actually deletes module + test mirror. `scaffold up` runs `uv lock --upgrade && uv sync`.

**Independent Tests**:
- US-9: `scaffold dm --name Product` (no `--confirm`) prints a preview with two file paths and writes nothing. With `--confirm`, both paths are deleted.
- US-10: `scaffold up --dry-run` prints the two `uv` commands without executing them. `scaffold up` delegates to `subprocess.run(["uv", "lock", "--upgrade"])` (no `shell=True`, per R-09).

> ⚠️ US-9 stream (T071→T073) and US-10 stream (T074→T076) can proceed **in parallel** by different contributors.

### Tests for User Story 9 *(write BEFORE implementation)*

- [ ] T071 [P] [US9] Write tests for `dm`/`delete-module` via CliRunner: default (no `--confirm`) prints preview with both file paths and writes nothing, `--confirm` deletes module dir + test mirror, `--dry-run --confirm` combined shows preview with no deletions (`--dry-run` takes precedence per spec US-9 scenario 4), module name not found exits 1, `__init__.py` containing orphan import logs a resolution hint in tests/commands/test_delete_module.py

### Implementation for User Story 9

- [ ] T072 [US9] Implement `_delete_module_impl(name, confirm, dry_run)`: search all 5 layer paths for `<module_name>` (files and dirs), collect `DeleteFile` operations for module + test mirror, detect orphan `__init__.py` imports and emit warning hint, default to preview-only unless `confirm=True`, delegate to `FileWriter` in src/scaffold_ca_python/commands/delete_module.py
- [ ] T073 [US9] Register `dm` (hidden alias) and `delete-module` commands via `register(app)` in src/scaffold_ca_python/commands/delete_module.py; call `register(app)` in src/scaffold_ca_python/cli.py

### Tests for User Story 10 *(write BEFORE implementation)*

- [ ] T074 [P] [US10] Write tests for `up`/`update-project` via CliRunner: `--dry-run` prints both `uv` commands without calling `subprocess`, success path calls `subprocess.run` with correct argument lists (no `shell=True`), `uv` not on PATH exits 1, `uv lock` non-zero exit surfaces as exit 2 in tests/commands/test_update_project.py

### Implementation for User Story 10

- [ ] T075 [US10] Implement `_update_project_impl(dry_run)`: detect project root via `find_project_root`, run `subprocess.run(["uv", "lock", "--upgrade"], check=True, cwd=root)` then `subprocess.run(["uv", "sync"], check=True, cwd=root)` (R-09, no `shell=True`), catch `FileNotFoundError` for missing `uv` and `CalledProcessError` for failures in src/scaffold_ca_python/commands/update_project.py
- [ ] T076 [US10] Register `up` (hidden alias) and `update-project` commands via `register(app)` in src/scaffold_ca_python/commands/update_project.py; call `register(app)` in src/scaffold_ca_python/cli.py

**Checkpoint**: `scaffold dm --name SomeModel` (on a scaffolded project with a generated model) shows correct two-file preview. `scaffold dm --name SomeModel --confirm` deletes both. `scaffold up --dry-run` prints two `uv` commands.

---

## Final Phase: Polish & Cross-Cutting Concerns

**Purpose**: Elevate every command to production quality — consistent Rich output, resolution hints on all error paths, complete `--help` documentation, integration test coverage, and CI gate verification.

- [ ] T077 [P] Add Rich `Panel`, `Text` with color-coded `✓`/`✗`/`→` symbols, and file-count summary lines (e.g., "Created 7 files.") to all 10 command output functions in src/scaffold_ca_python/commands/
- [ ] T078 [P] Audit and complete resolution hints on every `ScaffoldError` raise and validation error path across src/scaffold_ca_python/commands/ and src/scaffold_ca_python/core/ (every error message must include a `Hint:` line per **FR-021**)
- [ ] T079 [P] Add `typer.Option(help=..., show_default=True, rich_help_panel=...)` annotations and `@app.command(epilog=...)` usage examples for all 10 commands in src/scaffold_ca_python/commands/ so `scaffold <cmd> --help` shows complete, accurate documentation
- [ ] T080 Write end-to-end workflow tests using Typer `CliRunner` against a temporary directory covering the full quickstart.md workflow: `ca → gm → guc → gda → gep → gpipe → vs` (must exit 0 at each step) in tests/commands/test_workflow.py
- [ ] T081 Run `pytest --cov=scaffold_ca_python --cov-fail-under=80 --cov-report=term-missing` and add targeted unit tests to close any coverage gaps below the 80% gate in tests/
- [ ] T082 Execute the full quickstart.md walkthrough end-to-end in a clean temporary directory (`ca → gm → guc → gda → gep → gh → gpipe → vs → dm --confirm → up --dry-run`) and confirm every command exits 0 without manual intervention; document any deviations in specs/004-scaffold-ca-python-cli/quickstart.md
- [ ] T090 Write checksum-based dry-run verification tests: for each of the 10 commands, hash the project directory tree before and after a `--dry-run` invocation using `hashlib.sha256` and assert the digest is unchanged — verifying SC-007 in tests/commands/test_dry_run_checksum.py
- [ ] T091 [P] Write `pytest-benchmark` performance tests asserting all generation commands (`gm`, `guc`, `gda`, `gep`, `gh`) complete within 3 seconds on a scaffolded project — verifying SC-002 (baseline: macOS 14+/Linux, M-series or equivalent x86-64, 8 GB RAM) in tests/commands/test_performance.py
- [ ] T092 [P] Extend performance tests to assert `scaffold vs` completes in under 5 seconds on a project containing 200 Python source files — verifying SC-003 in tests/commands/test_performance.py

**Checkpoint**: All tests pass. `pytest --cov-fail-under=80` exits 0. `scaffold --help` lists all 10 commands with correct descriptions. The quickstart.md walkthrough is fully automated.

---

## Phase 10 (Amendment v2.0.0): Template Rendering Tests — `tests/templates/`

**Purpose**: Constitutional mandate (Amendment v2.0.0, Principle II) — a `tests/templates/`
directory MUST exist with at least one test per template group. Each test renders the template
with a representative context and asserts structural correctness.

**Prerequisite**: Template files for each group must be present (Phases 3–9 complete).

> ⚠️ **Write each test first. Confirm it fails. Then iterate on the template until it passes.**

- [ ] T083 [P] Write template rendering test for the `project/` group — render `pyproject_toml.jinja2` with a representative `ProjectContext`, assert `[tool.scaffold-ca-python]` section present, package name correct, Python 3.13 target listed in `tests/templates/test_project_templates.py`
- [ ] T084 [P] Write template rendering test for the `model/` group — render `model.py.jinja2` with a representative `ModuleContext`, assert class name present, `BaseModel` import correct, async syntax used where applicable in `tests/templates/test_model_templates.py`
- [ ] T085 [P] Write template rendering test for the `use_case/` group — render `use_case.py.jinja2` with a representative `ModuleContext`, assert class name present, `async def execute` present, constructor signature correct in `tests/templates/test_use_case_templates.py`
- [ ] T086 [P] Write template rendering test for the `driven_adapter/` group (all 3 types) — render each driven adapter template with representative contexts, assert class name present, correct import statements per type (`httpx.AsyncClient` for `rest-consumer`), async syntax used in `tests/templates/test_driven_adapter_templates.py`
- [ ] T087 [P] Write template rendering test for the `entry_point/` group (all 4 types) — render each entry point template with representative contexts, assert class/function names present, `FastAPI` import for `restapi`, `async def` present, MCP and A2A stubs structurally correct in `tests/templates/test_entry_point_templates.py`
- [ ] T088 [P] Write template rendering test for the `helper/` group — render `helper.py.jinja2` with a representative `ModuleContext`, assert class name present, import statements correct, module lives in correct namespace in `tests/templates/test_helper_templates.py`
- [ ] T089 [P] Write template rendering test for the `pipeline/` group (both providers) — render `github/ci.yml.jinja2` and `azure/azure_pipelines.yml.jinja2` with representative contexts, assert `ruff`, `mypy`, `pytest --cov-fail-under=80` steps present in `tests/templates/test_pipeline_templates.py`

**Checkpoint**: `pytest tests/templates/` discovers all 7 test files. Each test renders at least one
template with a representative context and makes at least one structural assertion.
`pytest --cov-fail-under=80` continues to pass.

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)          → No dependencies; start immediately
Phase 2 (Foundational)   → Requires Phase 1 complete; BLOCKS all user stories
Phase 3 (US-1)           → Requires Phase 2 complete; no story dependencies
Phase 4 (US-2, US-3)     → Requires Phase 2 complete; US-2 and US-3 are independent
Phase 5 (US-4)           → Requires Phase 2 + Phase 3 complete (project must exist to test gda)
Phase 6 (US-5)           → Requires Phase 2 + Phase 3 complete (project must exist to test gep)
Phase 7 (US-6)           → Requires Phase 2 complete; benefits from Phases 3–6 (more to validate)
Phase 8 (US-7, US-8)     → Requires Phase 2 + Phase 3 complete; US-7 and US-8 are independent
Phase 9 (US-9, US-10)    → Requires Phase 2 + Phase 3 complete; US-9 and US-10 are independent
Final Phase (Polish)     → Requires all desired user stories complete
Phase 10 (tests/templates/) → Requires Phases 3–9 complete (all Jinja2 templates must be present)
```

### User Story Dependencies

| Story | Depends On | Reason |
|---|---|---|
| US-1 (ca) | Phase 2 | Needs core engine (file_writer, template_renderer, project_detector) |
| US-2 (gm) | Phase 2 | Needs core engine; does not depend on US-1 for unit tests |
| US-3 (guc) | Phase 2 | Needs core engine; independent of US-1 for unit tests |
| US-4 (gda) | Phase 2, US-1 | Integration tests scaffold a project first |
| US-5 (gep) | Phase 2, US-1 | Integration tests scaffold a project first |
| US-6 (vs) | Phase 2 | StructureValidator is pure core; benefits from US-1 for integration |
| US-7 (gh) | Phase 2, US-1 | Integration tests scaffold a project first |
| US-8 (gpipe) | Phase 2, US-1 | Integration tests scaffold a project first |
| US-9 (dm) | Phase 2, US-1 | Needs a module to delete |
| US-10 (up) | Phase 2 | Only needs project root detection and subprocess |

### Within Each User Story

1. **Tests** — write and confirm failing *(mandatory first step)*
2. **Templates** — create Jinja2 source files *(parallel with test authoring)*
3. **Implementation** — implement the command handler *(after tests and templates)*
4. **Registration** — register in cli.py *(after implementation)*

---

## Parallel Execution Examples

### Parallel Example: Phase 2 — Foundational

```text
Stream A (Models):  T009 → T010 → T011 → T012  (write tests)
                    T013 → T014 → T015 → T016  (implement, once tests written)

Stream B (Core):    T017 → T018 → T019 → T020  (write tests, after models exist)
                    T021 → T022 → T023 → T024  (implement)

All [P] tasks within each group can run concurrently.
```

### Parallel Example: Phase 4 — US-2 and US-3

```text
Stream A (US-2 gm):   T034 [P] [US2]  →  T035 [P] [US2]  →  T036 [P] [US2]
                      T037 [US2]       →  T038 [US2]

Stream B (US-3 guc):  T039 [P] [US3]  →  T040 [P] [US3]  →  T041 [P] [US3]
                      T042 [US3]       →  T043 [US3]

All of T034–T041 can run in parallel across both streams.
T037 starts only after T034 + T035 + T036 are complete.
T042 starts only after T039 + T040 + T041 are complete.
```

### Parallel Example: Phase 8 — US-7 and US-8

```text
Stream A (US-7 gh):    T062 [P] → T063 [P] → T064 → T065
Stream B (US-8 gpipe): T066 [P] → T067 [P] → T068 [P] → T069 → T070

T062 through T068 can all run in parallel across both streams.
```

---

## Implementation Strategy

### MVP Scope (deliver value immediately)

**Phase 1 + Phase 2 + Phase 3** constitutes a fully usable MVP:
- `scaffold ca` scaffolds a complete project ← US-1 alone demonstrates the tool's value

### Incremental Delivery Order

1. **Sprint 1 (MVP)**: Phases 1–3 → Ship `scaffold ca`
2. **Sprint 2 (Core Generation)**: Phase 4 → Ship `scaffold gm` + `scaffold guc`
3. **Sprint 3 (Infrastructure)**: Phases 5–6 → Ship `scaffold gda` + `scaffold gep`
4. **Sprint 4 (Governance)**: Phase 7 → Ship `scaffold vs` (CI gate ready)
5. **Sprint 5 (Utilities)**: Phases 8–9 → Ship `gh`, `gpipe`, `dm`, `up`
6. **Sprint 6 (Production)**: Final Phase → Polish, 80% coverage gate, integration tests

---

## Summary

| Metric | Count |
|---|---|
| **Total tasks** | **89** |
| **Phase 1 (Setup)** | 8 tasks |
| **Phase 2 (Foundational)** | 16 tasks |
| **Phase 3 (US-1 ca)** | 9 tasks |
| **Phase 4 (US-2 gm + US-3 guc)** | 10 tasks |
| **Phase 5 (US-4 gda)** | 6 tasks |
| **Phase 6 (US-5 gep)** | 7 tasks |
| **Phase 7 (US-6 vs)** | 5 tasks |
| **Phase 8 (US-7 gh + US-8 gpipe)** | 9 tasks |
| **Phase 9 (US-9 dm + US-10 up)** | 6 tasks |
| **Final Phase (Polish)** | 9 tasks |
| **Phase 10 (tests/templates/)** | 7 tasks |
| **Parallelizable tasks ([P])** | 56 tasks |
| **TDD test tasks (precede implementation)** | 18 test tasks |

### Independent Test Criteria per Story

| Story | Independent Test |
|---|---|
| US-1 (ca) | `scaffold ca --name X` on empty dir → all 6 layers + 6 config files created; `uv sync` succeeds |
| US-2 (gm) | `scaffold gm --name Product` → `domain/model/product.py` + test mirror; `pytest` discovers stub |
| US-3 (guc) | `scaffold guc --name CreateOrder` → `domain/usecase/create_order_use_case.py` + test; async stub valid |
| US-4 (gda) | `scaffold gda --type rest-consumer` → 3-file module; `generic` without `--name` exits 1 with hint |
| US-5 (gep) | `scaffold gep --type restapi` → valid FastAPI app immediately; `--swagger` injects routes |
| US-6 (vs) | Clean project → exit 0 with count; domain→infra import → exit 1 with file:line:import |
| US-7 (gh) | `scaffold gh --name Logger` → `infrastructure/helpers/logger/` + test mirror; `vs` still exits 0 |
| US-8 (gpipe) | `scaffold gpipe --provider github` → valid `.github/workflows/ci.yml`; no `--provider` → exit 1 |
| US-9 (dm) | Default → preview only, no disk writes; `--confirm` deletes module + test mirror |
| US-10 (up) | `--dry-run` → prints 2 `uv` commands; real run → delegates to `subprocess` (no `shell=True`) |

### Format Validation

All 92 tasks follow the required checklist format:
- ✅ Every task starts with `- [ ]`
- ✅ Every task has a sequential ID (`T001`–`T092`)
- ✅ Every task in a user story phase has a `[USx]` label
- ✅ Every parallelizable task has a `[P]` marker
- ✅ Every task includes an exact file path or directory path
- ✅ Setup and Foundational tasks carry no story label
