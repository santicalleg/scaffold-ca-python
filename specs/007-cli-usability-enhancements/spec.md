# Feature Specification: CLI Usability Enhancements

**Feature Branch**: `007-cli-usability-enhancements`  
**Created**: 2026-03-30  
**Status**: Draft  
**Input**: User description: "Build a set of CLI usability enhancements for scaffold-ca-python"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Rename `generate-project` to `clean-architecture` (Priority: P1)

A developer who has just installed the tool runs `scaffold-ca-python clean-architecture --name my-app` and gets a scaffolded project, exactly as before. The old `generate-project` command no longer exists; trying to invoke it exits with a non-zero code and a clear message pointing to `clean-architecture`. The short alias `ca` still works without change.

**Why this priority**: The command name `generate-project` does not match the tool's purpose — scaffolding Clean Architecture projects. Renaming it to `clean-architecture` dramatically improves discoverability and brand consistency without affecting existing workflows (the `ca` alias is preserved). This is a breaking change that must land first so all downstream work builds on the correct name.

**Independent Test**: Can be fully tested by running `scaffold-ca-python clean-architecture --name demo` and confirming a project is created, then running `scaffold-ca-python generate-project` and confirming exit code is non-zero with a hint message.

**Acceptance Scenarios**:

1. **Given** the CLI is installed, **When** the user runs `scaffold-ca-python clean-architecture --name demo`, **Then** a project directory `demo/` is created with the standard Clean Architecture layout and the command exits 0.
2. **Given** the CLI is installed, **When** the user runs `scaffold-ca-python ca --name demo`, **Then** behaviour is identical to `clean-architecture` (same output, same exit code).
3. **Given** the CLI is installed, **When** the user runs `scaffold-ca-python generate-project --name demo`, **Then** the command exits with a non-zero code and prints a message that mentions `clean-architecture`.
4. **Given** the user runs `scaffold-ca-python --help`, **Then** `clean-architecture` (with alias `ca`) appears in the command list and `generate-project` does not appear.
5. **Given** the user runs `scaffold-ca-python ca --help`, **Then** the help output is byte-for-byte identical to `scaffold-ca-python clean-architecture --help`.

---

### User Story 2 - Contextual per-command help with types table and Examples epilog (Priority: P2)

A developer runs `scaffold-ca-python gep --help` and immediately sees a table listing every valid `--type` value with a one-line description. They also see an Examples section at the bottom of the help output showing concrete invocations. The same quality of help is available for `gda` and `gpipe`.

**Why this priority**: Users currently have to consult external documentation or trial-and-error to discover valid `--type` values and required option combinations. Rich inline help reduces friction and support overhead without requiring any code-generation changes.

**Independent Test**: Can be fully tested by running each of `gep --help`, `gda --help`, and `gpipe --help` and verifying all types and examples appear in the output.

**Acceptance Scenarios**:

1. **Given** the user runs `scaffold-ca-python gep --help`, **Then** the output lists `restapi`, `agent`, `mcp`, and `generic` with a one-line description for each, and shows a runnable Examples section.
2. **Given** the user runs `scaffold-ca-python gep --help`, **Then** options `--enable-kafka` and `--enable-mcp-client` are documented as applicable only when `--type agent` is used.
3. **Given** the user runs `scaffold-ca-python gda --help`, **Then** the output lists `rest-consumer`, `secrets`, and `generic` with a description for each, and includes an Examples section noting that `--name` is required when `--type generic` is used.
4. **Given** the user runs `scaffold-ca-python gpipe --help`, **Then** `--provider` is shown as required and its accepted values (`github`, `azure`) are each described.
5. **Given** the user runs `scaffold-ca-python ca --help` and `scaffold-ca-python clean-architecture --help`, **Then** both outputs are identical.

---

### User Story 3 - Default to help when invoked with no arguments (Priority: P3)

A developer types `scaffold-ca-python` with no arguments and sees the full help output; the process exits 0. Similarly, typing `scaffold-ca-python gm` (or any subcommand) with no arguments shows that subcommand's help and exits 0, rather than printing a raw error about missing options.

**Why this priority**: New users who type the bare command name expect guidance, not an error. Showing help on no-args is a quality-of-life improvement that makes the tool feel polished and lowers the learning curve.

**Independent Test**: Can be fully tested by invoking `scaffold-ca-python` with no arguments and checking that the exit code is 0 and help text is present; then doing the same for each subcommand.

**Acceptance Scenarios**:

1. **Given** the user runs `scaffold-ca-python` with no arguments, **Then** the root help is printed and the process exits 0.
2. **Given** the root help is printed, **Then** `clean-architecture` appears with its `ca` alias visible in the command description.
3. **Given** the user runs `scaffold-ca-python gm` with no arguments (omitting `--name`), **Then** `gm` help is printed and the process exits 0.
4. **Given** the user runs `scaffold-ca-python gep` with no arguments (omitting `--type`), **Then** `gep` help is printed and the process exits 0.
5. **Given** any subcommand is run with no arguments, **Then** the output always contains the required option names (e.g., `--name`, `--type`) so the user knows what to supply next.

---

### Edge Cases

- What happens when a shell script or CI pipeline pipes `scaffold-ca-python --help` to grep? Help output must remain stable (consistent wording and option names) so piped consumers are not broken by cosmetic rewording.
- What happens if a user passes `--type` with an invalid value? The existing validation and error message must be preserved; no-args-help must not interfere with explicit invocation errors.
- What happens if both `--enable-kafka` and `--enable-mcp-client` are passed with `--type restapi`? Existing behaviour (error or ignore) is preserved; the help text just documents the agent-only restriction.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The CLI MUST expose a `clean-architecture` command that accepts `--name` and all other options previously accepted by `generate-project`, with identical behaviour.
- **FR-002**: The CLI MUST remove `generate-project` as a valid command; invoking it MUST exit non-zero and print a message directing the user to `clean-architecture`.
- **FR-003**: The `ca` alias MUST remain mapped to `clean-architecture` and behave identically to invoking `clean-architecture` directly.
- **FR-004**: The `--help` output for `clean-architecture` and `ca` MUST be identical (same text, same options, same Examples).
- **FR-005**: The `gep --help` output MUST include a table (or equivalent structured list) showing each valid `--type` value (`restapi`, `agent`, `mcp`, `generic`) with a one-line description.
- **FR-006**: The `gep --help` output MUST document `--enable-kafka` and `--enable-mcp-client` as applicable only when `--type agent` is used.
- **FR-007**: The `gep --help` output MUST include an Examples epilog section with at least two runnable command examples.
- **FR-008**: The `gda --help` output MUST include a table showing each valid `--type` value (`rest-consumer`, `secrets`, `generic`) with a one-line description, and MUST state that `--name` is required when `--type generic` is used.
- **FR-009**: The `gda --help` output MUST include an Examples epilog section.
- **FR-010**: The `gpipe --help` output MUST mark `--provider` as required and enumerate its valid values (`github`, `azure`) with descriptions.
- **FR-011**: The `gpipe --help` output MUST include an Examples epilog section.
- **FR-012**: Running the root command (`scaffold-ca-python`) with no arguments MUST print the root help and exit 0.
- **FR-013**: The root help output MUST display `clean-architecture` with its `ca` alias visible in the command description (e.g., `"Scaffold a new CA project. Alias: ca"`).
- **FR-014**: Running any subcommand (`gm`, `gep`, `gda`, `guc`, `dm`, `gh`, `gpipe`, `vs`, `up`) with no arguments MUST print that subcommand's help and exit 0.
- **FR-015**: The help output of all commands MUST remain stable in wording and option names so that piped or scripted consumers are not broken.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All valid `--type` values for `gep`, `gda`, and `gpipe` are discoverable from `--help` alone, without consulting external documentation.
- **SC-002**: Running the root command or any subcommand with no arguments produces an exit code of 0 and prints help text.
- **SC-003**: Invoking `scaffold-ca-python generate-project` exits with a non-zero code and contains the string `clean-architecture` in its output.
- **SC-004**: The output of `scaffold-ca-python ca --help` is byte-for-byte identical to `scaffold-ca-python clean-architecture --help`.
- **SC-005**: All 405 existing tests continue to pass after the changes (no regressions).
- **SC-006**: Running `scaffold-ca-python gm` with no arguments exits 0 and the output contains `--name`.

## Assumptions

- The `ca` alias is the only short alias in active use; all other command short names (`gep`, `gda`, `gpipe`, `gm`, `guc`, `gdm`, `ghelper`, `vs`, `up`) are already descriptive short aliases and are not renamed by this feature.
- The tool is run from a terminal by developers; terminal width of at least 80 characters is assumed for table formatting.
- No external scripts or CI pipelines depend on `generate-project` by that name (the alias `ca` is the established stable short form).
- The Examples epilog sections are plain text appended to the built-in `--help` output; they do not require a documentation-generation pipeline.
- Stable help output (SC-005 / FR-015) means option names and core wording do not change; minor whitespace or layout adjustments are acceptable.
