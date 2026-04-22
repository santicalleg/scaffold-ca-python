# Feature Specification: scaffold-ca-python CLI

**Feature Branch**: `004-scaffold-ca-python-cli`  
**Created**: 2026-03-25  
**Status**: Ready  
**Input**: Build scaffold-ca-python, a command-line tool that allows Python developers to instantly scaffold production-ready Python applications following Clean Architecture principles, without having to manually set up the folder structure, boilerplate code, configuration files, or test scaffolds.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Project Bootstrapping (Priority: P1)

A developer wants to start a new Python project that follows Clean Architecture. They run a single command and receive a complete, immediately runnable project skeleton with the correct layer structure, dependency configuration, and basic boilerplate — without reading documentation or manually creating any files or folders.

**Why this priority**: It is the entry point for every other user story. Without a correctly scaffolded project, all generation commands have no target to operate on. This story alone constitutes a usable MVP.

**Independent Test**: Running `scaffold-ca-python ca --name MyProject --package com.example` on an empty directory produces a project that can be started without any additional manual setup. Verified by: (a) `uv sync` inside the generated directory completes without errors, and (b) `python -c "import my_project"` succeeds under the installed virtual environment — confirming all imports resolve and no unhandled exception is raised (per the "immediately runnable" definition in Assumptions).

**Acceptance Scenarios**:

1. **Given** an empty target directory, **When** the developer runs `scaffold-ca-python ca --name MyProject --package com.example`, **Then** the tool generates `domain/model/`, `domain/usecase/`, `infrastructure/entry-points/`, `infrastructure/driven-adapters/`, `infrastructure/helpers/`, and `application/` directories, each with a valid `__init__.py`.
2. **Given** the generated project, **When** the developer installs its dependencies, **Then** no import errors occur and the application starts without modification.
3. **Given** any generated project, **When** the developer inspects the generated boilerplate, **Then** all I/O operations use `async def` and `await` consistently — synchronous mode is not supported.
4. **Given** a target directory that already contains a project, **When** the developer runs `ca` again with the same name, **Then** the tool displays a clear error and does not overwrite any existing files.

---

### User Story 2 — Domain Model Generation (Priority: P2)

A developer working inside a scaffolded project wants to add a new domain entity. They run a single command and receive a typed model class in the correct layer directory, along with a corresponding test file — without manually navigating the folder structure or writing boilerplate.

**Why this priority**: Domain models are the foundation of the inner layer and are the first artefact most developers need after a project is bootstrapped. Generating them correctly enforces the layer location rule from the start.

**Independent Test**: Running `scaffold-ca-python gm --name Product` inside a scaffolded project creates `domain/model/product.py` and a corresponding test file that the developer can immediately populate.

**Acceptance Scenarios**:

1. **Given** a scaffolded project, **When** the developer runs `scaffold-ca-python gm --name Product`, **Then** `domain/model/product.py` is created with a typed model class and the test mirror file is created at `tests/domain/model/test_product.py`.
2. **Given** the generated model file, **When** the developer inspects it, **Then** it contains type hints and uses Pydantic as the base model class.
3. **Given** a model that already exists, **When** the developer runs `gm` with the same name, **Then** the tool shows a clear error message and does not overwrite the existing file.

---

### User Story 3 — Use Case Generation (Priority: P3)

A developer wants to add application logic. They run a single command and receive a use case class in `domain/usecase/` that accepts injected port interfaces via its constructor, along with a test file — mirroring the reference plugin's pattern.

**Why this priority**: Use cases are the core of the application logic layer. After models exist, this is the next artefact teams need to express business behaviour.

**Independent Test**: Running `scaffold-ca-python guc --name CreateProduct` produces a use case class with an injectable constructor and a failing test scaffold that the developer can evolve with TDD.

**Acceptance Scenarios**:

1. **Given** a scaffolded project, **When** the developer runs `scaffold-ca-python guc --name CreateProduct`, **Then** `domain/usecase/create_product_use_case.py` is created with a class that accepts port interface arguments in its constructor.
2. **Given** the generated use case file, **When** the developer inspects it, **Then** the class contains a stub `execute` method and type hints on all public interfaces.
3. **Given** the generated test file, **When** the developer runs the test suite, **Then** the test file is discovered by the test runner (even if assertions are pending/skipped).
4. **Given** a use case with the same name already exists, **When** the developer runs `guc`, **Then** a clear error is shown and no file is overwritten.

---

### User Story 4 — Driven Adapter Generation (Priority: P4)

A developer needs to connect the application to an external system (a database, message queue, cloud storage, etc.). They run a single command specifying the technology type and receive a driven adapter module in `infrastructure/driven-adapters/` with all necessary boilerplate, configuration, and a test scaffold.

**Why this priority**: Driven adapters are the most common infrastructure component developers add. Automating them saves significant repetitive effort and enforces the port/adapter pattern.

**Independent Test**: Running `scaffold-ca-python gda --type rest-consumer` produces a self-contained adapter module with a repository class that implements a port interface, verifiable by inspecting the generated files.

**Acceptance Scenarios**:

1. **Given** a scaffolded project, **When** the developer runs `scaffold-ca-python gda --type rest-consumer`, **Then** `infrastructure/driven-adapters/rest-consumer/` is created with a REST client adapter, a configuration module, and a test scaffold in the test mirror.
2. **Given** the generated adapter, **When** the developer inspects it, **Then** the adapter class implements the port interface pattern (references an abstract base class or protocol defined in `domain/model/`).
3. **Given** `--type generic`, **When** the developer does not supply `--name`, **Then** the tool shows a validation error with a resolution hint explaining that `--name` is required for `generic` adapters.
4. **Given** `--type generic --name CacheStore`, **When** executed, **Then** a generic adapter named `CacheStore` is created following the same structure as typed adapters.
5. **Given** any supported type, **When** the adapter directory already exists, **Then** a clear error is shown and no files are overwritten.

**Supported types**: `rest-consumer`, `secrets`, `generic`

---

### User Story 5 — Entry Point Generation (Priority: P5)

A developer wants to expose the application's use cases to the outside world via a transport or protocol. They run a single command specifying the entry point type and receive a complete skeleton in `infrastructure/entry-points/` with routing, handler stubs, and a test scaffold.

**Why this priority**: Entry points define how the application is triggered (HTTP, events, agents). Teams need to generate them reliably for each transport they support.

**Independent Test**: Running `scaffold-ca-python gep --type restapi` immediately produces a functional FastAPI router skeleton — no additional configuration or flags are required.

**Acceptance Scenarios**:

1. **Given** a scaffolded project, **When** the developer runs `scaffold-ca-python gep --type restapi`, **Then** `infrastructure/entry-points/restapi/` is created immediately with a complete FastAPI router, at least one example handler stub, and a test scaffold — no additional flags are needed to activate FastAPI.
2. **Given** `--type restapi --swagger path/to/openapi.yaml`, **When** the OpenAPI file exists, **Then** the router is generated with routes derived from the provided specification.
3. **Given** `--type mcp`, **When** executed, **Then** `infrastructure/entry-points/mcp/` is created with an MCP server stub containing placeholder definitions for at least one tool, one resource, and one prompt handler, plus a test scaffold.
4. **Given** `--type agent`, **When** combined with `--enable-kafka`, **Then** a Kafka consumer is included in the generated agent entry point.
5. **Given** `--type agent`, **When** combined with `--enable-mcp-client`, **Then** an MCP client initialisation block is included in the generated agent entry point.
6. **Given** any entry point type that already exists in the project, **When** the command is run again, **Then** a clear error is shown and no files are overwritten.

**Supported types**: `restapi` (FastAPI), `agent` (A2A), `mcp`, `generic`

---

### User Story 6 — Structure Validation (Priority: P6)

A developer or CI pipeline wants to verify that the project's dependency rule is intact — no inner layer imports from an outer layer. They run a single command and receive an immediate pass/fail result with a human-readable violation report.

**Why this priority**: Continuous enforcement of the dependency rule is what makes the architecture non-negotiable rather than advisory. CI integration is a key adoption driver.

**Independent Test**: Running `scaffold-ca-python vs` on a freshly generated project returns exit code 0; adding a domain module import from infrastructure and re-running returns exit code 1 with the violating import identified.

**Acceptance Scenarios**:

1. **Given** a project where all imports respect the dependency rule, **When** the developer runs `scaffold-ca-python vs`, **Then** the command exits with code 0 and displays a success message.
2. **Given** a project where `domain/model/product.py` imports from `infrastructure/driven-adapters/`, **When** the developer runs `scaffold-ca-python vs`, **Then** the command exits with code 1 and the violation report identifies the exact file, line number, and offending import statement.
3. **Given** a violation report, **When** the developer reads it, **Then** each violation includes a resolution hint explaining which import to remove.
4. **Given** a GitHub Actions workflow that runs `scaffold-ca-python vs`, **When** a violation is committed, **Then** the workflow step fails, blocking the merge.

---

### User Story 7 — Helper and Pipeline Generation (Priority: P7)

A developer wants to add a cross-cutting utility module or a CI/CD pipeline, following the project conventions. They run a single command and receive the file in the correct location with the correct structure.

**Why this priority**: Helpers and pipelines are supporting artefacts that standardise operational practices and reduce copy-paste drift across projects and teams.

**Tasks traceability note**: For implementation purposes this story is split into two independent task streams — `[US7]` (helper generation, `gh`) and `[US8]` (pipeline generation, `gpipe`) — to allow parallel work. Both streams are fully covered by this single user story because the commands share the same developer intent ("add a supporting artefact in the right place with the right structure") and the same priority.

**Independent Test**: Running `scaffold-ca-python gh --name LoggingHelper` creates a helper module in `infrastructure/helpers/` and a test mirror file; running `scaffold-ca-python gpipe --provider github` creates `.github/workflows/ci.yml` with lint, test, and coverage steps.

**Acceptance Scenarios**:

1. **Given** a scaffolded project, **When** the developer runs `scaffold-ca-python gh --name LoggingHelper`, **Then** `infrastructure/helpers/logging_helper.py` is created with a stub class and `tests/infrastructure/helpers/test_logging_helper.py` is created.
2. **Given** a scaffolded project, **When** the developer runs `scaffold-ca-python gpipe --provider github`, **Then** `.github/workflows/ci.yml` is created with steps for linting, running tests, and enforcing the coverage threshold.
3. **Given** a scaffolded project, **When** the developer runs `scaffold-ca-python gpipe --provider azure`, **Then** `azure-pipelines.yml` is created with equivalent steps for linting, running tests, and enforcing the coverage threshold.
4. **Given** `gpipe` is run without `--provider`, **Then** the tool shows a validation error with a resolution hint listing the two supported providers.
5. **Given** a helper with the same name already exists, **When** `gh` is run again, **Then** a clear error is shown and the file is not overwritten.
6. **Given** a pipeline file for the chosen provider already exists, **When** `gpipe` is run with the same provider, **Then** a clear error is shown and the file is not overwritten.

---

### User Story 8 — Safe Module Deletion (Priority: P8)

A developer wants to remove a generated module and all its associated test files cleanly. They run a deletion command that by default previews the changes and only executes when explicitly confirmed.

**Why this priority**: Deleting generated modules without cleaning up test mirrors and configuration references is a common source of broken projects. Automating safe deletion prevents this.

**Independent Test**: Running `scaffold-ca-python dm --name ProductRepository` (without `--confirm`) displays a rich-formatted list of files that would be deleted, but no files are actually removed.

**Acceptance Scenarios**:

1. **Given** an existing driven adapter named `ProductRepository`, **When** the developer runs `scaffold-ca-python dm --name ProductRepository`, **Then** the tool shows a dry-run preview listing the adapter directory and its test mirror, without deleting anything.
2. **Given** the same command with `--confirm` appended, **When** executed, **Then** both the module folder and its test counterpart are removed.
3. **Given** a module name that does not exist in the project, **When** `dm` is run, **Then** a clear error is shown with guidance on listing available modules.
4. **Given** a deletion of a module that is referenced by an `__init__.py`, **When** `dm --confirm` is executed, **Then** the orphan import is also removed or the user is warned with a resolution hint.

---

### User Story 9 — Dry-Run Preview (Priority: P9)

A developer wants to preview what any generation command would produce, without committing any changes to disk. Every command supports a `--dry-run` flag that shows a rich-formatted summary of all files that would be created or modified.

**Why this priority**: Dry-run capability is a safety net that builds developer confidence and lends itself naturally to code review workflows and documentation.

**Independent Test**: Running any generation command with `--dry-run` on a scaffolded project produces a Rich-formatted output listing files and content previews, and afterwards no new files exist on disk.

**Acceptance Scenarios**:

1. **Given** any generation command (`ca`, `gm`, `guc`, `gda`, `gep`, `gh`, `gpipe`, `vs`, `dm`, `up`), **When** `--dry-run` is appended, **Then** the command outputs a Rich-formatted list of file paths with content previews and a summary line (e.g., "Would create 5 files, modify 1 file").
2. **Given** a dry-run execution, **When** it completes, **Then** no files are created, modified, or deleted on disk.
3. **Given** a dry-run on `vs`, **When** executed, **Then** it outputs the validation result without any side effects (same as running without `--dry-run`, since `vs` is read-only).
4. **Given** a dry-run on `dm`, **When** combined with `--confirm`, **Then** `--dry-run` takes precedence and no files are deleted.

---

### User Story 10 — Update Project Dependencies (Priority: P10)

A developer working inside a scaffolded project wants to update all declared dependencies to their latest compatible versions without manually editing any configuration files.

**Why this priority**: Dependency freshness is an ongoing maintenance concern; automating it removes friction and reduces the risk of stale transitive dependencies accumulating over time.

**Independent Test**: Running `scaffold-ca-python up --dry-run` inside a scaffolded project prints the two `uv` commands that would be executed without spawning any subprocess. Running `scaffold-ca-python up` invokes `uv lock --upgrade` then `uv sync` in sequence inside the detected project root.

**Acceptance Scenarios**:

1. **Given** a scaffolded project with `uv` on PATH, **When** the developer runs `scaffold-ca-python up`, **Then** `uv lock --upgrade` and `uv sync` are invoked in sequence in the detected project root and the command exits 0 on success.
2. **Given** `--dry-run`, **When** executed, **Then** the two `uv` commands are printed to stdout with their `cwd` shown, and no subprocess is spawned.
3. **Given** `uv` is not installed or not on PATH, **When** `up` is run, **Then** the command exits 1 with a resolution hint directing the developer to the `uv` installation page.
4. **Given** `uv lock --upgrade` returns a non-zero exit code, **When** that occurs, **Then** `uv sync` is NOT executed and the command exits 2 with the `uv` error output displayed.

---

### Edge Cases

- What happens when the target directory has restricted write permissions? → The tool displays a permission error with the affected path and no partial writes are left on disk.
- What happens when two generation commands are run concurrently on the same project? → Each command is atomic per the files it manages; no file is left in a partially written state.
- What happens when a `--name` contains invalid Python identifier characters (spaces, hyphens in class names)? → The tool validates and sanitises the name, converting to snake_case for filenames and PascalCase for class names, and informs the user of the normalisation applied.
- What happens when the project root cannot be detected (no `pyproject.toml` or CA structure marker)? → Generation commands that require a scaffolded project context fail with a clear error: "No scaffold-ca-python project detected. Run `scaffold-ca-python ca` to initialise one."
- What happens when `vs` is run on a project with circular imports that do not cross layer boundaries? → Only cross-layer violations are reported; intra-layer circular imports are out of scope.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The tool MUST provide a `generate-project` command (alias `ca`) that scaffolds a complete Clean Architecture Python project structure with all six layers.
- **FR-002**: Generated projects MUST include `pyproject.toml`, `README.md`, and `.gitignore`. (Logging configuration support is explicitly deferred to a follow-up feature and is not part of this specification.)
- **FR-003**: All generated project boilerplate MUST use `async def` and `await` for I/O operations; synchronous mode is not supported.
- **FR-004**: All generated domain model classes MUST use Pydantic as their base model; there is no opt-out or alternative model style.
- **FR-005**: The tool MUST provide a `generate-model` command (alias `gm`) that creates a typed model class in `domain/model/` and a corresponding test scaffold.
- **FR-006**: The tool MUST provide a `generate-use-case` command (alias `guc`) that creates a use case class with injectable port constructor arguments in `domain/usecase/` and a corresponding test scaffold.
- **FR-007**: The tool MUST provide a `generate-driven-adapter` command (alias `gda`) that creates a driven adapter module in `infrastructure/driven-adapters/` for the three supported types: `rest-consumer`, `secrets`, and `generic`.
- **FR-008**: The `gda` command MUST require a `--name` parameter when `--type generic` is specified.
- **FR-009**: The tool MUST provide a `generate-entry-point` command (alias `gep`) that creates an entry point module in `infrastructure/entry-points/` for the four supported types: `restapi`, `agent`, `mcp`, and `generic`.
- **FR-010**: The `gep --type restapi` command MUST immediately generate a complete FastAPI router skeleton without requiring additional flags; it MUST additionally support a `--swagger` flag to generate routes from an OpenAPI specification file.
- **FR-011**: The `gep --type agent` command MUST support `--enable-kafka` and `--enable-mcp-client` flags to compose additional capabilities.
- **FR-012**: The tool MUST provide a `validate-structure` command (alias `vs`) that inspects all Python imports in the project and reports any cross-layer dependency violations, exiting with code 1 when violations exist and code 0 otherwise.
- **FR-013**: Each violation reported by `vs` MUST identify the file path, line number, and the specific import statement that violates the dependency rule.
- **FR-014**: The tool MUST provide a `generate-helper` command (alias `gh`) that creates a utility module in `infrastructure/helpers/` and a test scaffold.
- **FR-015**: The tool MUST provide a `generate-pipeline` command (alias `gpipe`) that generates a CI pipeline file for the provider specified via `--provider`; supported providers are `github` (outputs `.github/workflows/ci.yml`) and `azure` (outputs `azure-pipelines.yml`). The `--provider` flag is mandatory. Each generated pipeline MUST include lint, test, and coverage enforcement steps.
- **FR-016**: The tool MUST provide a `delete-module` command (alias `dm`) that by default shows a dry-run preview and requires `--confirm` to execute the deletion.
- **FR-017**: The `dm` command MUST remove both the module folder and its corresponding test mirror when confirmed.
- **FR-018**: Every generation and deletion command MUST support a `--dry-run` flag that previews all file operations without writing to disk.
- **FR-019**: Dry-run output MUST be Rich-formatted showing file paths, content previews, and a summary of affected files.
- **FR-020**: Every command MUST produce Rich-formatted terminal output with progress indicators during execution.
- **FR-021**: Every error message MUST include a resolution hint that tells the user what action to take.
- **FR-022**: No generation command MUST overwrite an existing file; attempting to do so MUST produce a clear error.
- **FR-023**: The tool MUST provide an `update-project` command (alias `up`) that updates a generated project's declared dependencies to their latest compatible versions.

### Key Entities

- **Generated Project**: the artefact produced by `ca`; defined by its name and package identifier. All generated projects are async-only and use Pydantic for domain models.
- **Layer**: one of the six structural units (`domain/model`, `domain/usecase`, `infrastructure/entry-points`, `infrastructure/driven-adapters`, `infrastructure/helpers`, `application`) that define position within the dependency hierarchy.
- **Module**: a generated unit inside a layer (a model class, a use case, an adapter, a helper, or an entry point). Each module has a canonical directory location and a paired test mirror.
- **Dependency Violation**: a Python import statement where an inner-layer module imports from an outer layer, as detected by `validate-structure`.
- **Template**: a parameterised source file that the tool renders to produce all generated output. Templates are not visible to end users but define the shape of every generated module.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can go from zero to a runnable, correctly structured Clean Architecture Python project in under 60 seconds using `scaffold-ca-python ca`. *(Non-automatable outcome metric: validated by the end-to-end walkthrough in T082, not by an automated timing assertion. Establishes the human-perceived UX bar.)*
- **SC-002**: Every generation command (`gm`, `guc`, `gda`, `gep`, `gh`) completes within 3 seconds on a standard developer machine (macOS 14+ or Linux with an Apple M-series or equivalent x86-64 processor and at least 8 GB RAM).
- **SC-003**: The `validate-structure` command completes a full project scan in under 5 seconds for projects with up to 200 Python source files.
- **SC-004**: All 10 user stories produce generated output that passes the project's own test suite with 0 failures and ≥ 80% coverage on the CLI codebase.
- **SC-005**: A developer can integrate `validate-structure` into a CI pipeline and receive a failing build within 2 minutes of a layer violation being merged.
- **SC-006**: 100% of supported command types (`gda` types and `gep` types as defined in the constitution) are implemented and covered by tests.
- **SC-007**: Dry-run mode produces zero file-system side effects, verifiable by a checksum of the project directory before and after any dry-run invocation.
- **SC-008**: No generation or deletion command leaves the project in a partially written state when interrupted mid-execution.

## Assumptions

- Developers run the tool inside a terminal on macOS or Linux; Windows support is not a requirement for v1.
- The tool is installed from PyPI via `uv` or `pip`; no additional system dependencies beyond Python 3.13+ are required.
- "Immediately runnable" is defined as: all imports resolve and the application process starts without raising an unhandled exception under a clean virtual environment with generated dependencies installed.
- Generated projects use `uv` for dependency management and `pyproject.toml` as the build descriptor, matching the tool's own stack.
- All generated projects are async-only; there is no synchronous generation mode.
- All generated domain models use Pydantic; there is no opt-out and no dataclass alternative.
- The `--swagger` flag for `gep --type restapi` expects a valid OpenAPI 3.x YAML or JSON file; older Swagger 2.x files are assumed out of scope for v1.
- Acceptance test generation (`gat`) and performance test generation (`gpt`) are explicitly excluded from this scope; they are planned as separate features.
- The reference implementation (bancolombia/scaffold-clean-architecture) is used as the authoritative specification for layer naming, command behaviour, and generated project structure when any detail is ambiguous.
- The CLI tool's own source code does not need to follow Clean Architecture internally; only projects generated by the tool are subject to that constraint.

