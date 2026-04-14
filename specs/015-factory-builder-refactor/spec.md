# Feature Specification: CLI Factory + Builder Architecture Refactor

**Feature Branch**: `015-factory-builder-refactor`
**Created**: 2025-07-22
**Status**: Draft
**Input**: User description: "Refactor CLI commands to Factory + Builder architecture"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Contributor Adds a New Module Type Without Touching Command Files (Priority: P1)

A contributor wants to add support for a new entry-point or driven-adapter type. With the
current architecture, they must modify the central command module, adding another branch to
an existing if/elif block. This creates risk of unintended side effects and makes the change
harder to review.

After this refactor, the same contributor creates one new file implementing the
module-factory interface, adds one entry to the type registry, and the new type is
immediately available — with no modifications to existing command files.

**Why this priority**: Reducing the modification surface for new features is the primary
architectural goal. Proving that a type can be added in isolation validates the Factory
pattern is working as intended.

**Independent Test**: Can be fully tested by creating a stub `ModuleFactory` implementation,
registering it under a new type key, and verifying the command invokes it correctly — no
other command behavior or story needs to be implemented first.

**Acceptance Scenarios**:

1. **Given** a new module-factory class registered under a new type key, **When** a CLI
   command is invoked with that type, **Then** the factory method is called and files are
   generated without any modification to the existing command module.
2. **Given** the refactored codebase, **When** a developer reads any command module,
   **Then** it contains no type-specific template paths, dependency lists, or subdirectory
   rules.
3. **Given** any module-factory class, **When** its imports are inspected, **Then** it
   references only the builder interface and domain model types — not lower-level file,
   template, or dependency utilities.

---

### User Story 2 - All Existing CLI Commands Produce Identical Output (Priority: P1)

An end user (a developer who uses the scaffold tool) runs the same `scaffold gep` and
`scaffold gda` commands they used before the refactor. They observe no behavioral changes:
same generated files, same injected dependencies, same error messages, same dry-run preview.

**Why this priority**: The refactor must be invisible to tool users. Any functional
regression directly breaks the primary tool value proposition.

**Independent Test**: Can be verified by running the full existing automated test suite
against the refactored codebase and confirming every test passes with output matching the
pre-refactor baseline.

**Acceptance Scenarios**:

1. **Given** an existing scaffold project, **When** any current command is invoked with its
   current flags and type values, **Then** the generated files and injected dependencies are
   identical to the pre-refactor baseline.
2. **Given** an invalid type string is supplied, **When** the command runs, **Then** the
   same error message is displayed as before.
3. **Given** dry-run mode is activated, **When** any scaffold command runs, **Then** no
   files are written and the same structured preview is shown as before.
4. **Given** an incompatible flag combination (e.g., `--swagger` with a non-restapi type),
   **When** the command runs, **Then** validation rejects the input with the same message as
   before.

---

### User Story 3 - All Shared Build Operations Accessed Through a Single Builder API (Priority: P1)

A contributor reviews a module-factory class and sees it calls methods only on a single
`ModuleBuilder` object. They do not need to know whether files go through `FileWriter`,
templates go through `TemplateRenderer`, or dependencies go through `pyproject_writer`. The
builder abstracts all coordination details.

**Why this priority**: Centralizing shared operations in the builder is the core structural
improvement. Without it, the Factory pattern provides coordination value but still scatters
infrastructure concerns across factory files.

**Independent Test**: Can be verified by inspecting any factory file's import list (no
lower-level utilities present) and running the integration test for that factory type in
isolation to confirm the builder delegates all operations correctly.

**Acceptance Scenarios**:

1. **Given** any module-factory implementation, **When** its import list is inspected,
   **Then** it imports only the builder interface and shared domain model types.
2. **Given** a `ModuleBuilder` instance, **When** a factory calls add-file, add-dependency,
   and render-template methods, **Then** the builder accumulates all operations and applies
   them atomically in a single persist step.
3. **Given** dry-run mode is set on the builder, **When** `persist()` is called, **Then**
   no files are written and the builder returns a structured description of all pending
   operations.

---

### User Story 4 - Type Registry Consolidates All Available Types Per Command (Priority: P2)

A contributor or maintainer wants to understand what module types a command supports.
Instead of tracing an if/elif chain through a large function, they look at a single
type-to-factory mapping and immediately see all registered types.

**Why this priority**: Provides a quality-of-life improvement for maintainability. The core
P1 stories deliver most of the architectural value, so registry consolidation is an
optimization layer, not a prerequisite.

**Independent Test**: Can be tested by loading the registry for a given command and
asserting all known type strings appear as valid keys.

**Acceptance Scenarios**:

1. **Given** the entry-point command, **When** the type registry is inspected, **Then** all
   currently supported types (restapi, mcp, agent, generic) appear as registered entries.
2. **Given** an unrecognized type string, **When** the registry is queried, **Then** a
   clear error lists all valid types — the same behavior as validating against the allowed
   types list today.
3. **Given** the driven-adapter command, **When** the type registry is inspected, **Then**
   all currently supported types (rest-consumer, secrets, generic) appear as registered
   entries.

---

### Edge Cases

- What happens when a factory raises an error mid-build? The builder must not persist
  partial results — either all operations succeed or none are written to disk.
- What happens when both entry-point exclusivity validation and factory logic both need
  project context? Both must receive the same resolved context without loading it twice.
- What happens if dry-run is requested but a factory validates filesystem state (e.g., checks
  for an incompatible existing directory)? Validation must still run in dry-run mode; only
  file writes are skipped.
- What happens when commands with single-path logic (`generate_model`, `generate_use_case`,
  `generate_helper`) are migrated? The Factory pattern is applied for structural
  consistency; their registries each contain a single entry.
- What happens if a factory tries to render a template that does not exist? The error must
  surface with a clear message before any disk writes occur.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Each supported module type MUST be implemented as a separate class fulfilling
  the module-factory contract (a single method that accepts a `ModuleBuilder` and populates
  it with files, dependencies, and parameters for that type).
- **FR-002**: The module-factory contract MUST expose exactly one method as its public
  interface; the method receives a `ModuleBuilder` and has no return value.
- **FR-003**: `ModuleBuilder` MUST expose operations for adding files, rendering templates,
  adding dependencies, reading project properties, and persisting all accumulated operations
  to disk.
- **FR-004**: `ModuleBuilder` MUST carry a dry-run flag; when set, `persist()` MUST skip
  all disk writes and instead return a structured description of pending operations
  equivalent to the current dry-run preview output.
- **FR-005**: CLI command modules MUST be limited to input parsing, validation, and
  delegation to a factory via the builder; they MUST NOT contain type-specific template
  paths, dependency lists, or subdirectory rules.
- **FR-006**: The type-to-factory mapping for each command MUST be defined in a single
  registry location; the command retrieves the appropriate factory by looking up the type
  string in this registry.
- **FR-007**: Module-factory implementations MUST NOT import lower-level utilities
  (`FileWriter`, `TemplateRenderer`, `pyproject_writer`) directly; such capabilities are
  accessed exclusively through `ModuleBuilder` methods.
- **FR-008**: All existing CLI commands, flags, flag combinations, and error messages MUST
  remain identical to the pre-refactor behavior from the user's perspective.
- **FR-009**: All Jinja2 template files MUST remain unchanged; the refactor is limited to
  Python source files only.
- **FR-010**: Existing `ProjectContext` and `ModuleContext` domain models MUST be used
  as-is; no new domain models are introduced as part of this refactor.
- **FR-011**: The entry-point exclusivity guard (restapi conflicts with mcp/agent) MUST be
  preserved, either in the command module or as a precondition within applicable factory
  classes.

### Key Entities

- **ModuleFactory**: The contract for a type-specific module generator. Accepts a
  `ModuleBuilder` and populates it; has no knowledge of CLI, filesystem mechanics, or
  template rendering internals.
- **ModuleBuilder**: Central orchestrator that accumulates file operations, dependencies,
  parameters, and project context. Exposes high-level operations (add file, add dependency,
  render template, persist). Wraps existing lower-level utilities internally.
- **Type Registry**: A mapping from type-string to factory class (or callable) for each
  command. Defines the complete valid-type set and enables dispatch without conditional
  branching.
- **ProjectContext / ModuleContext**: Existing domain models (unchanged) that carry the
  resolved project root, package name, module name, layer, and related metadata.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All pre-existing automated tests pass without modification after the refactor
  is complete.
- **SC-002**: Adding support for a new module type requires creating exactly one new factory
  file and one registry entry — no modifications to existing command modules.
- **SC-003**: A contributor can understand all type-specific behavior for a given module
  type by reading a single factory class file, without needing to trace logic spread across
  a larger command module.
- **SC-004**: Code coverage remains at or above 95% after the refactor.
- **SC-005**: Dry-run output for all command types before and after the refactor is
  identical — verified by comparing test snapshots against the pre-refactor baseline.

## Assumptions

- `FileWriter`, `TemplateRenderer`, and `pyproject_writer` continue to exist as lower-level
  utilities; `ModuleBuilder` wraps them rather than replacing them.
- The `ProjectContext` and `ModuleContext` Pydantic models are sufficient to carry all state
  needed by factory implementations without modification.
- The primary refactor scope where multi-type dispatch provides the most value is
  `generate_entry_point.py` and `generate_driven_adapter.py`; `generate_model.py`,
  `generate_use_case.py`, `generate_helper.py`, and `delete_module.py` are in scope for
  consistency but represent simpler single-path cases.
- `ModuleBuilder` is a composition wrapper over existing utilities, not a ground-up rewrite
  of infrastructure.
- Feature 014 (`tests-in-src`) is complete before this refactor begins; the `src/tests/`
  layout is the established baseline.
- Existing test helpers and fixtures for command testing remain usable after the refactor;
  no wholesale replacement of test infrastructure is required.
