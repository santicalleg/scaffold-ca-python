# Feature Specification: Python Clean Architecture Scaffold

**Feature Branch**: `002-scaffold-clean-arch`  
**Created**: 2026-03-25  
**Status**: Draft  
**Input**: User description: "Create Python scaffold based on bancolombia/scaffold-clean-architecture"

## Overview

A command-line tool that generates opinionated Python project structures following Clean Architecture principles, directly translating the feature set of the bancolombia/scaffold-clean-architecture Gradle plugin into idiomatic Python. Developers invoke the CLI to produce a ready-to-run project skeleton with correctly separated layers, and continue using the same tool throughout the project lifecycle to generate additional components (models, use cases, driven adapters, entry points, helpers), validate architectural constraints, delete modules, and keep the project up to date—eliminating manual setup and enforcing layer-dependency rules across teams.

**Reference architecture** (Java Gradle plugin → Python CLI translation):

| Java layer | Python package |
|---|---|
| `domain/model` | `domain/model/` — entities (dataclasses / value objects) + gateway interfaces (ports) |
| `domain/usecase` | `domain/usecase/` — use case classes orchestrating business logic |
| `infrastructure/driven-adapters` | `infrastructure/driven_adapters/` — concrete implementations of domain ports |
| `infrastructure/entry-points` | `infrastructure/entry_points/` — delivery mechanisms (REST, events, CLI, etc.) |
| `infrastructure/helpers` | `infrastructure/helpers/` — shared utilities for adapters and entry points |
| `applications/app-service` | `app/` — dependency injection wiring and application entry point |
| `deployment/` | `deployment/` — Dockerfile, CI/CD pipeline files |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate a New Clean Architecture Project (Priority: P1)

A developer wants to start a new Python project conforming to Clean Architecture. They run `scaffold new` with a project name and receive a fully structured project directory with all layers, boilerplate configuration, a working DI wiring stub, a default test suite, and an executable entry point.

**Why this priority**: This is the core value proposition. Every other command depends on a properly scaffolded project existing.

**Independent Test**: Run `scaffold new --name my_project` and verify that the expected directory tree is created with all required layer packages, that the bundled test suite passes without modification, and that the application entry point runs without errors.

**Acceptance Scenarios**:

1. **Given** the tool is installed, **When** the developer runs `scaffold new --name my_project`, **Then** a directory `my_project/` is created with `domain/model/`, `domain/usecase/`, `infrastructure/driven_adapters/`, `infrastructure/entry_points/`, `infrastructure/helpers/`, `app/`, and `deployment/` directories and their stub files.
2. **Given** a newly scaffolded project, **When** the developer runs the bundled test command from the project root, **Then** all default tests pass without any modification.
3. **Given** a project name containing invalid characters (spaces, hyphens converted, special chars), **When** the developer runs the command, **Then** the tool normalizes to snake_case, informs the developer, or rejects the input with a clear error before creating any files.
4. **Given** a target directory already exists, **When** the developer runs `scaffold new`, **Then** the tool warns and aborts unless `--force` is explicitly passed.
5. **Given** the developer passes `--package myorg.payments`, **When** the project is generated, **Then** the top-level Python package becomes `payments` (last segment) and all generated modules use that as the root namespace (e.g., `payments/domain/model/`). The `--package` option is a simple dot-separated Python namespace; reverse-domain notation is not used.

---

### User Story 2 - Generate a Domain Model (Priority: P2)

A developer needs a new domain entity and its corresponding gateway interface (port). They run `scaffold generate model --name Order` and receive an entity class stub and a gateway interface stub in the `domain/model/` layer.

**Why this priority**: Domain models are the innermost layer and the building block for use cases and adapters; generating them consistently prevents naming and location errors.

**Independent Test**: Inside a scaffolded project, run `scaffold generate model --name Order` and verify that `domain/model/order.py` (entity) and `domain/model/gateways/order_gateway.py` (interface) are created.

**Acceptance Scenarios**:

1. **Given** an existing scaffolded project, **When** the developer runs `scaffold generate model --name Order`, **Then** an entity stub and a gateway interface stub are created in `domain/model/` with the correct naming convention.
2. **Given** a model name that already exists, **When** the developer runs the command without `--force`, **Then** the tool warns and aborts without overwriting.
3. **Given** a PascalCase name like `OrderItem`, **When** the command runs, **Then** the generated filename uses snake_case (`order_item.py`) and the class name uses PascalCase.

---

### User Story 3 - Generate a Use Case (Priority: P2)

A developer needs a new application use case. They run `scaffold generate use-case --name ProcessOrder` and receive a use case class stub and its test stub in the `domain/usecase/` layer.

**Why this priority**: Ongoing use case generation is the most frequent workflow after initial scaffolding; consistent stubs enforce the architectural rule that use cases only depend on the model layer.

**Independent Test**: Inside a scaffolded project, run `scaffold generate use-case --name ProcessOrder` and verify that the use case stub and its test stub are created in `domain/usecase/` and that the test stub passes.

**Acceptance Scenarios**:

1. **Given** an existing scaffolded project, **When** the developer runs `scaffold generate use-case --name ProcessOrder`, **Then** a use case stub and a corresponding test stub are created in the correct directories.
2. **Given** a use case name that already exists, **When** the developer runs the command without `--force`, **Then** the tool warns and aborts.
3. **Given** a name in non-snake-case format, **When** the command runs, **Then** the tool normalizes and informs the developer.

---

### User Story 4 - Generate a Driven Adapter (Priority: P2)

A developer needs to connect an external dependency (database, HTTP service, message broker, cloud storage, cache, etc.). They run `scaffold generate driven-adapter --type <type> --name <name>` and receive an infrastructure adapter stub in `infrastructure/driven_adapters/` along with a gateway interface stub already in `domain/model/gateways/` if not already present.

**Why this priority**: Driven adapters are the most varied and error-prone component to set up manually; generating consistent stubs with proper interface wiring prevents architectural drift.

**Independent Test**: Run `scaffold generate driven-adapter --type repository --name OrderRepository` and verify that the domain gateway interface and the adapter stub are created in the correct directories with a passing test stub.

**Acceptance Scenarios**:

1. **Given** an existing scaffolded project, **When** the developer runs `scaffold generate driven-adapter --type repository --name OrderRepository`, **Then** a domain gateway interface stub and an adapter stub are created in the correct directories.
2. **Given** an unsupported adapter type, **When** the developer runs the command, **Then** the tool lists all supported types and exits with a non-zero code.
3. **Given** a type that requires extra options (e.g., `--url` for a REST client adapter), **When** the developer omits the option, **Then** the tool prompts or errors clearly.

**Supported adapter types (Python equivalents)**:

| Type | Java equivalent | Python adaptation |
|---|---|---|
| `generic` | generic | Empty adapter stub |
| `repository` | jpa / r2dbc | SQLAlchemy / asyncpg repository stub |
| `rest-client` | restconsumer | HTTP client adapter stub (with `--url`) |
| `mongodb` | mongodb | MongoDB adapter stub |
| `redis` | redis | Redis adapter stub (with `--mode template\|repository`) |
| `dynamo` | dynamodb | DynamoDB adapter stub |
| `s3` | s3 | AWS S3 adapter stub |
| `sqs-sender` | sqs | SQS message sender stub |
| `kafka-sender` | asynceventbus/kafka | Kafka producer stub |
| `rabbitmq-sender` | asynceventbus/rabbitmq | RabbitMQ publisher stub |
| `secrets` | secrets | Secrets provider adapter stub |

---

### User Story 5 - Generate an Entry Point (Priority: P2)

A developer wants to expose the application via a delivery mechanism. They run `scaffold generate entry-point --type <type> --name <name>` and receive a wired entry point stub in `infrastructure/entry_points/`.

**Why this priority**: Entry points define how the application is consumed; generating them consistently ensures they reference use cases through the correct interface.

**Independent Test**: Run `scaffold generate entry-point --type rest-api --name OrderApi` and verify that entry point stub files are created in `infrastructure/entry_points/` with a passing test stub.

**Acceptance Scenarios**:

1. **Given** an existing scaffolded project, **When** the developer runs `scaffold generate entry-point --type rest-api --name OrderApi`, **Then** an entry point stub is created in `infrastructure/entry_points/` wired to the use case interface.
2. **Given** an unsupported entry-point type, **When** the developer runs the command, **Then** the tool lists supported types and exits with an error.

**Supported entry-point types (Python equivalents)**:

| Type | Java equivalent | Python adaptation |
|---|---|---|
| `generic` | generic | Empty entry point stub |
| `rest-api` | restmvc / webflux | REST API router stub (sync or async depending on project mode) |
| `graphql` | graphql | GraphQL schema and resolver stub |
| `kafka-consumer` | kafka / kafkastrimzi | Kafka consumer stub |
| `sqs-listener` | sqs | SQS listener stub |
| `async-event-handler` | asynceventhandler | Async event handler stub (rabbitmq/kafka with `--tech`) |
| `cli` | — (Python-specific) | CLI command stub |

---

### User Story 6 - Generate a Helper (Priority: P3)

A developer needs a shared utility used by multiple adapters or entry points. They run `scaffold generate helper --name LoggingHelper` and receive a helper module stub in `infrastructure/helpers/`.

**Why this priority**: Helpers prevent code duplication across adapters; lower priority as they are a supporting concern.

**Independent Test**: Run `scaffold generate helper --name JwtHelper` and verify that a helper stub is created in `infrastructure/helpers/`.

**Acceptance Scenarios**:

1. **Given** an existing scaffolded project, **When** the developer runs `scaffold generate helper --name JwtHelper`, **Then** a helper stub is created in `infrastructure/helpers/jwt_helper.py`.
2. **Given** a helper name that already exists, **When** the command runs without `--force`, **Then** the tool aborts without overwriting.

---

### User Story 7 - Validate Project Structure (Priority: P2)

A developer wants to confirm the project still complies with Clean Architecture dependency rules after many changes. They run `scaffold validate` and receive a pass/fail report listing any violations.

**Why this priority**: Structural validation is the enforcement mechanism for the architecture; without it, layer violations can silently accumulate.

**Independent Test**: In a scaffolded project, introduce a deliberate import of an infrastructure module inside `domain/model/`, run `scaffold validate`, and verify that a violation is reported with the offending file and rule.

**Acceptance Scenarios**:

1. **Given** a clean scaffolded project, **When** the developer runs `scaffold validate`, **Then** the command exits with code 0 and reports no violations.
2. **Given** a project where `domain/model/` imports from `infrastructure/`, **When** the developer runs `scaffold validate`, **Then** the command exits with a non-zero code and reports the specific violation.
3. **Given** a project where `domain/usecase/` imports from `infrastructure/`, **When** the developer runs `scaffold validate`, **Then** the command reports the violation.
4. **Given** a project where `infrastructure/` correctly imports only from `domain/`, **When** the developer runs `scaffold validate`, **Then** no violations are reported.

**Dependency rules enforced** (cross-layer direction only; circular imports within the same layer are out of scope for v1):
- `domain/model/` MUST have no imports from any other layer.
- `domain/usecase/` MUST only import from `domain/model/`.
- `infrastructure/` MAY import from `domain/` but MUST NOT import from `app/`.
- `app/` MAY import from any layer (it is the composition root).

---

### User Story 8 - Delete a Module (Priority: P3)

A developer needs to remove a previously generated component (adapter, entry point, helper, model, or use case). They run `scaffold delete --module <name>` and the tool removes the corresponding files and directory.

**Why this priority**: Without a delete command, developers manually remove files and risk leaving orphan references; lower priority as it is a less frequent operation.

**Independent Test**: Generate a driven adapter, then run `scaffold delete --module order_repository` and verify that the adapter files are removed.

**Acceptance Scenarios**:

1. **Given** an existing module, **When** the developer runs `scaffold delete --module order_repository`, **Then** the module directory and files are removed.
2. **Given** a module name that does not exist, **When** the command runs, **Then** the tool reports the error and exits without modifying any files.

---

### User Story 9 - Update Project (Priority: P3)

A developer wants to bring an existing scaffolded project up to date with the latest tool version (updated boilerplate, configuration files, dependency stubs). They run `scaffold update` and the tool refreshes structural files while preserving user code.

**Why this priority**: Long-lived projects need a migration path as the scaffold evolves; lower priority for v1 but critical for adoption.

**Independent Test**: Run `scaffold update` on a project generated with a previous tool version and verify that boilerplate structural files are updated without altering files in `domain/` or `infrastructure/` that contain user logic.

**Acceptance Scenarios**:

1. **Given** a scaffolded project, **When** the developer runs `scaffold update`, **Then** structural boilerplate files (configuration, DI wiring stub, pyproject.toml dependencies) are refreshed.
2. **Given** files containing user-written code, **When** `scaffold update` runs, **Then** those files are not overwritten.
3. **Given** no staged Git changes, **When** the developer runs `scaffold update`, **Then** the tool warns to commit first (passes safely with `--skip-git-check`).

---

### User Story 10 - List Available Component Types (Priority: P3)

A developer wants to know what driven adapter and entry-point types are available. They run `scaffold list` and receive a formatted catalog of all supported component types with short descriptions.

**Why this priority**: Discoverability reduces friction; does not block any core flow.

**Independent Test**: Run `scaffold list` and verify that all built-in adapter and entry-point types from the spec are listed with names and descriptions.

**Acceptance Scenarios**:

1. **Given** the tool is installed, **When** the developer runs `scaffold list`, **Then** all supported types for driven-adapter and entry-point are displayed with names and short descriptions.
2. **Given** the developer runs `scaffold list --type driven-adapter`, **Then** only driven-adapter types are shown.

---

### Edge Cases

- What happens when `scaffold generate` is run outside a scaffolded project directory (no project marker file)?
- What happens when a generated file has a syntax error in its template?
- How does the tool handle project names that are Python reserved keywords (e.g., `import`, `class`)?
- How does `scaffold validate` behave with circular imports within the same layer?
- What happens when `scaffold delete` is asked to delete the only entry point or model in the project?
- How does `scaffold update` handle conflicts when a boilerplate file has been manually edited?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The tool MUST provide a `new` command accepting `--name` (required) and `--package` (optional, default: project name) that generates the complete seven-layer project structure. The `--package` option accepts a dot-separated Python namespace; the last segment becomes the top-level package directory (e.g., `--package org.example.payments` → top-level dir `payments/`). Reverse-domain notation is accepted as input but only the final segment is used as the Python package root.
- **FR-002**: The generated project MUST contain the layers: `domain/model/`, `domain/usecase/`, `infrastructure/driven_adapters/`, `infrastructure/entry_points/`, `infrastructure/helpers/`, `app/`, and `deployment/`, each with the required stub files.
- **FR-003**: The generated `app/` module MUST include a dependency injection wiring stub that wires all generated components together and serves as the application entry point.
- **FR-004**: The generated project MUST include a default test suite that passes without any modification immediately after scaffolding.
- **FR-005**: The generated project MUST include an `ArchitectureTest` test file in `app/` that programmatically enforces the layer-dependency rules on every test run.
- **FR-006**: The tool MUST provide a `generate model --name <name>` command that creates an entity stub and a gateway interface stub in `domain/model/`.
- **FR-007**: The tool MUST provide a `generate use-case --name <name>` command that creates a use case stub and a test stub in `domain/usecase/`.
- **FR-008**: The tool MUST provide a `generate driven-adapter --type <type> --name <name>` command that creates an adapter stub in `infrastructure/driven_adapters/` and the corresponding gateway interface in `domain/model/gateways/` if not already present. Supported types are listed in User Story 4.
- **FR-009**: The tool MUST provide a `generate entry-point --type <type> --name <name>` command that creates an entry point stub in `infrastructure/entry_points/`. Supported types are listed in User Story 5.
- **FR-010**: The tool MUST provide a `generate helper --name <name>` command that creates a helper utility stub in `infrastructure/helpers/`.
- **FR-011**: The tool MUST provide a `validate` command that inspects import statements (via AST-level static analysis) across all layers and reports any cross-layer dependency-rule violations as described in User Story 7. Circular imports within the same layer are out of scope for v1.
- **FR-012**: The tool MUST provide a `delete --module <name>` command that removes the directory and files of a previously generated module.
- **FR-013**: The tool MUST provide an `update` command that refreshes boilerplate structural files without overwriting user-authored code, and warns the developer to commit first (skippable with `--skip-git-check`). If a boilerplate file has been manually modified since it was generated, the tool MUST create a `.bak` backup of the existing file before overwriting it, and MUST report each backup to the developer.
- **FR-014**: The tool MUST provide a `list` command (and `list --type <driven-adapter|entry-point>`) that displays all supported component types with names and descriptions.
- **FR-015**: The tool MUST validate all user-provided names and reject invalid or reserved-keyword names with actionable error messages before writing any files.
- **FR-016**: The tool MUST refuse to overwrite existing files without an explicit `--force` flag.
- **FR-017**: All `generate`, `validate`, `delete`, and `update` commands MUST be run from within a recognized scaffolded project directory; the tool MUST provide a clear error if run elsewhere.
- **FR-018**: The tool MUST normalize all component names to snake_case for filenames and PascalCase for class names, informing the developer of any normalization applied.
- **FR-019**: The tool MUST generate a single opinionated project layout (one service per project) in v1. Monorepo support is explicitly out of scope.
- **FR-020**: The tool MUST write a project marker file named `.scaffold-ca.json` at the project root in JSON format. The file MUST store at minimum: project name, base package, project mode (sync/async), tool version used to create the project, and the list of registered components (type, name, layer, generated files). This file is the authoritative source for project metadata and is used by all `generate`, `validate`, `delete`, and `update` commands.
- **FR-021**: The tool MUST support the following output verbosity flags on all commands: `--quiet` (suppress all informational output, show only errors) and `--verbose` (show debug-level output including file paths, template selections, and normalization steps). Default output is human-readable informational messages.

### Key Entities

- **Project**: The top-level scaffolded unit. Attributes: name, base package, project mode (sync/async), registered components, tool version.
- **Layer**: A logical subdivision of the project enforcing Clean Architecture dependency rules. Layers (in dependency order): model → usecase → driven_adapters / entry_points / helpers → app.
- **Component**: A generated artifact occupying a specific layer. Attributes: name, type, owning layer, generated files list.
- **Gateway (Port)**: An interface defined in `domain/model/gateways/` that decouples use cases from infrastructure implementations.
- **Template**: The blueprint used to render a component's files. Attributes: component type, target layer, file list, supported options.
- **Project Marker**: A metadata file (`.scaffold-ca`) at the project root storing the project name, base package, mode, and registered components.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can scaffold a new project and have it running (tests passing, entry point executable) in under 2 minutes from a fresh environment.
- **SC-002**: Adding or generating any supported component (model, use case, adapter, entry point, helper) completes in under 5 seconds and creates all expected files without manual edits.
- **SC-003**: 100% of generated default test suites (including `ArchitectureTest`) pass without modification immediately after `scaffold new`.
- **SC-004**: The tool rejects 100% of invalid, reserved-keyword, or duplicate component names with a human-readable error before touching the filesystem.
- **SC-005**: `scaffold validate` detects 100% of intentionally introduced layer-dependency violations in a test project.
- **SC-006**: Developers unfamiliar with Clean Architecture can identify the purpose of each layer and place new code in the correct layer on first attempt in at least 80% of observed cases, using only the generated README and inline comments.
- **SC-007**: All 11 supported driven-adapter types and 7 supported entry-point types each produce a stub that compiles/imports without errors and has at least one passing test stub.

## Assumptions

- Target users are Python developers with basic command-line familiarity; no prior Clean Architecture or bancolombia plugin knowledge is assumed.
- The scaffold adopts a single opinionated layout (one service per project) in v1; monorepo support is out of scope (FR-019).
- The tool supports both synchronous and asynchronous project modes (controlled by a `--async` flag on `scaffold new`); async mode uses `asyncio`-compatible stubs throughout.
- Dependency injection wiring in `app/` uses a lightweight, library-agnostic pattern (manual wiring) unless a DI library becomes part of a future spec revision.
- The tool is distributed as a standard Python package and installed via the standard Python package manager; no additional system-level installations are required.
- The existing project structure and CLI entry point in `src/scaffold_ca_python/cli.py` serve as the implementation foundation.
- Generated projects are self-contained; network access is not required to run them or their tests.
- The bancolombia/scaffold-clean-architecture plugin's Gradle-specific features (BOM management, Gradle wrapper, Lombok, Spring-specific patterns) are not translated verbatim; Python-idiomatic equivalents are used instead (e.g., pyproject.toml for dependency management, dataclasses/Pydantic for models, pytest for testing).
- The `validate` command inspects static imports (AST-level analysis) rather than requiring the project to be installed or running. Circular import detection within the same layer is out of scope for v1.
- The `--package` option follows standard Python flat-namespace convention (no reverse-domain directories); reverse-domain input is accepted but only the last segment is used as the top-level package directory.
- Project metadata is persisted in `.scaffold-ca.json` (JSON format) at the project root; no database or remote storage is required.
- The `.scaffold-ca.json` marker file is committed to version control alongside the project.
- All CLI commands emit human-readable informational output by default; developers can suppress or expand output via `--quiet` / `--verbose`.
- When `scaffold update` finds a modified boilerplate file, it creates a `.bak` sibling before overwriting; the developer is responsible for manually merging any desired customizations from the `.bak` file.
- Generated CI/CD pipeline files in `deployment/` target GitHub Actions by default for v1.
