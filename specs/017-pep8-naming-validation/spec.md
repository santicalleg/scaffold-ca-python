# Feature Specification: PEP 8 / PEP 423 Naming Validation

**Feature Branch**: `017-pep8-naming-validation`  
**Created**: 2026-04-15  
**Status**: Draft  
**Input**: User description: "According to python rules like PEP8 and PEP 423 (packaging): (1) validate --name input to accept only kebab-case or snake_case; (2) validate generated module files are snake_case; (3) validate generated classes are CamelCase/PascalCase."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Reject invalid project name at input (Priority: P1)

A developer runs any scaffold command with a `--name` value that is written in CamelCase or PascalCase (e.g., `MyProject`, `MyOrderService`). They expect the tool to immediately reject the input with a clear error message that tells them to use `kebab-case` or `snake_case` instead.

**Why this priority**: This is the most visible user-facing change. Failing fast with an actionable error message prevents silent generation of non-compliant artifacts.

**Independent Test**: Can be fully tested by running `scaffold ca --name MyProject` and verifying the command exits with a non-zero code and prints a message containing `kebab-case` or `snake_case`.

**Acceptance Scenarios**:

1. **Given** a developer runs `scaffold ca --name MyProject`, **When** the command validates the input, **Then** it exits with code 1 and prints a message indicating `kebab-case` or `snake_case` is required.
2. **Given** a developer runs `scaffold ca --name my-project` (kebab-case), **When** the command validates the input, **Then** it proceeds successfully and creates the project scaffold.
3. **Given** a developer runs `scaffold ca --name my_project` (snake_case), **When** the command validates the input, **Then** it proceeds successfully and creates the project scaffold.
4. **Given** a developer runs any other scaffold command (e.g., `scaffold gm --name MyModel`), **When** the command validates the input, **Then** the same kebab-case / snake_case rule is enforced.
5. **Given** a developer runs `scaffold ca --name My-Project` (mixed case with hyphen), **When** the command validates the input, **Then** it exits with code 1 with a clear hint.

---

### User Story 2 - Generated module files always use snake_case (Priority: P2)

A developer uses any scaffold command that creates `.py` module files. They expect every generated file name to follow `snake_case` naming (all lowercase, words separated by underscores), as required by PEP 8 and PEP 423.

**Why this priority**: Ensures downstream packaging and import consistency. A wrongly named file would break Python imports silently.

**Independent Test**: Can be fully tested by running `scaffold ca --name my-project` and verifying that all generated `.py` files under the output directory have names matching `[a-z][a-z0-9_]*\.py`.

**Acceptance Scenarios**:

1. **Given** a developer provides `--name my-project` (kebab-case), **When** the scaffold generates files, **Then** all `.py` module files are named using `snake_case` (e.g., `my_project.py`, `entry_point.py`).
2. **Given** a developer provides `--name my_order`, **When** files are generated, **Then** no file name contains uppercase letters or hyphens.
3. **Given** any scaffold command generates a file, **When** the file name is inspected, **Then** it matches the pattern `[a-z][a-z0-9_]*\.py`.

---

### User Story 3 - Generated class definitions always use PascalCase (Priority: P3)

A developer uses any scaffold command that generates Python class definitions. They expect every generated class to be named in PascalCase (also known as UpperCamelCase), as required by PEP 8 for class names.

**Why this priority**: Class naming is a code style guarantee. Incorrect class names would require manual correction by developers using the generated code.

**Independent Test**: Can be fully tested by scaffolding a project or module and inspecting the generated `.py` files for `class` keyword occurrences — each must have a PascalCase name.

**Acceptance Scenarios**:

1. **Given** a developer provides `--name my-project` (kebab-case), **When** class definitions are generated, **Then** all classes are named in PascalCase (e.g., `class MyProject:`, `class EntryPoint:`, `class DrivenAdapter:`).
2. **Given** a developer provides `--name order_service`, **When** a model or use case is scaffolded, **Then** the generated class is named `OrderService`, not `order_service` or `orderService`.
3. **Given** any scaffold command generates a class definition, **When** the source file is inspected, **Then** no class name starts with a lowercase letter.

---

### Edge Cases

- What happens when the user provides `--name a` (single character)? → Single-character `snake_case` identifiers are valid; the tool should accept them.
- What happens when `--name` contains only digits or special characters (e.g., `123`, `my@project`)? → The tool must reject with a clear error message.
- What happens when kebab-case includes consecutive hyphens (e.g., `my--project`)? → Reject with a clear error message about valid kebab-case format.
- What happens when a name starts or ends with a hyphen or underscore (e.g., `-myproject`, `myproject_`)? → Reject with an error message.
- How does the system handle names that are purely numeric after stripping separators (e.g., `1-2-3`)? → Reject; names must start with a letter.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The tool MUST reject any `--name` value that is not `kebab-case` or `snake_case`, exiting with code 1 and printing an actionable error message that states the accepted formats.
- **FR-002**: The error message for an invalid `--name` MUST explicitly mention both `kebab-case` and `snake_case` as the accepted formats.
- **FR-003**: The tool MUST accept `kebab-case` names (lowercase letters, digits, hyphens; starting with a letter) as valid `--name` input across all scaffold commands.
- **FR-004**: The tool MUST accept `snake_case` names (lowercase letters, digits, underscores; starting with a letter) as valid `--name` input across all scaffold commands.
- **FR-005**: The tool MUST reject names written in CamelCase or PascalCase (i.e., names containing uppercase letters) as invalid `--name` input.
- **FR-006**: All `.py` module files generated by any scaffold command MUST have file names that follow `snake_case` (all lowercase, words separated by underscores, matching `[a-z][a-z0-9_]*\.py`).
- **FR-007**: When a `kebab-case` name is provided as input, the scaffold MUST convert it to `snake_case` internally before using it as a Python module name or package directory.
- **FR-008**: All Python class definitions generated by any scaffold command MUST use `PascalCase` names (first letter of each word capitalised, no underscores or hyphens).
- **FR-009**: The `--name` validation MUST apply consistently to all scaffold commands that accept a `--name` argument (`ca`, `gm`, `guc`, `gh`, `gda`, `gep`, `dm`).
- **FR-010**: The naming rules MUST be enforced regardless of whether `--dry-run` is active.

### Key Entities

- **Name Input**: The raw string supplied by the user via `--name`. Can be `kebab-case` or `snake_case`; anything else is invalid.
- **Module Name**: The `snake_case` Python identifier derived from the name input, used for `.py` file names and package directories.
- **Class Name**: The `PascalCase` Python identifier derived from the module name, used for `class` definitions in generated source files.
- **Validation Rule**: A rule that checks a string against a naming convention and either passes it or raises an error with a descriptive message.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of `--name` inputs that do not conform to `kebab-case` or `snake_case` result in exit code 1 with a message referencing the accepted formats.
- **SC-002**: 100% of `.py` files generated by the scaffold tool have file names matching `[a-z][a-z0-9_]*\.py`.
- **SC-003**: 100% of `class` definitions in generated files have names matching `[A-Z][a-zA-Z0-9]*` (PascalCase).
- **SC-004**: All existing automated tests continue to pass after implementing validation, ensuring no regression for currently valid `--name` inputs.
- **SC-005**: Validation rules are covered by dedicated unit tests for each accepted and rejected name pattern (target: at least 10 distinct test cases across valid and invalid inputs).

## Assumptions

- Validation applies to all scaffold commands that accept a `--name` argument; no command is exempted.
- `kebab-case` input (e.g., `my-project`) is automatically and silently normalised to `snake_case` (e.g., `my_project`) for internal use as a Python identifier — no warning is shown for this conversion because both formats are explicitly accepted.
- Single-word names with no separators (e.g., `project`, `model`) are valid as long as they are all lowercase.
- The feature does not change the generated file tree structure, only the naming enforcement.
- Names that are already valid `snake_case` and were previously accepted by the existing `validate_name` regex will continue to be accepted without any change in behaviour.
- `PascalCase` enforcement for generated classes relies on the existing `to_pascal_case` utility; this feature adds validation/tests to guarantee that utility is always called correctly before writing class names.
