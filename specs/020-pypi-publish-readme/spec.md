# Feature Specification: PyPI Publishing & README Documentation

**Feature Branch**: `020-pypi-publish-readme`
**Created**: 2026-04-20
**Status**: Draft
**Input**: User description: "I want to publish the project to pypi.org package manager. The project must contains the requirements to publish the package. Update the README file to set a brief description about the project, how install it, how execute it with examples, what technologies are used, current features, how contributing and License."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Install the tool from PyPI (Priority: P1)

A developer discovers `scaffold-ca-python` on PyPI or via a colleague recommendation and wants to install it with a single command into any Python environment.

**Why this priority**: Without a working PyPI distribution, none of the other stories are possible. This is the entry gate to all end-user adoption.

**Independent Test**: Run `pip install scaffold-ca-python` (or `uv add scaffold-ca-python`) in a clean virtual environment, then verify `scaffold --help` responds correctly.

**Acceptance Scenarios**:

1. **Given** a clean Python ≥3.13 environment, **When** the user runs `pip install scaffold-ca-python`, **Then** the package installs without errors and the `scaffold` command is available on the PATH.
2. **Given** the package is installed, **When** the user runs `scaffold --help`, **Then** a help message listing all available commands is printed.
3. **Given** PyPI lists the package, **When** the user visits `https://pypi.org/project/scaffold-ca-python/`, **Then** the project name, description, version, and README are displayed correctly.

---

### User Story 2 - Understand the tool from the README (Priority: P2)

A developer visits the project's GitHub page or PyPI page and reads the README to decide whether to use the tool and how to get started quickly.

**Why this priority**: A clear README is the primary discovery and onboarding surface. It unblocks adoption once the package is installable.

**Independent Test**: A person with no prior knowledge of the project reads only the README and can successfully install and run their first `scaffold ca` command within 5 minutes.

**Acceptance Scenarios**:

1. **Given** the README is open, **When** the developer reads the "What is this?" section, **Then** they understand in ≤3 sentences what the tool does, who it is for, and what architectural pattern it follows.
2. **Given** the README is open, **When** the developer reads the "Installation" section, **Then** they find copy-pasteable commands for both `pip` and `uv` installation methods.
3. **Given** the README is open, **When** the developer reads the "Commands & Examples" section, **Then** they see at least one working command example for all 10 CLI commands (`ca`, `gm`, `guc`, `gda`, `gep`, `gh`, `gpipe`, `vs`, `dm`, `up`).
4. **Given** the README is open, **When** the developer reads the "Technologies" section, **Then** they find the key frameworks and tools listed with a one-line role or description each.
5. **Given** the README is open, **When** the developer reads the "Contributing" section, **Then** they find steps to fork, set up the dev environment, run tests, and submit a pull request.
6. **Given** the README is open, **When** the developer reads the "License" section, **Then** they find the SPDX license identifier and a link to the full license file.

---

### User Story 3 - Maintainer publishes a new release to PyPI (Priority: P3)

A maintainer tags a new version and wants the CI/CD or a manual command to build and publish the distribution to PyPI with minimal friction.

**Why this priority**: Ongoing maintenance and versioning is important but can be done manually until a CI workflow is set up; installability (P1) takes precedence.

**Independent Test**: Running `uv build && uv publish` from the project root (with credentials configured) successfully uploads the wheel and sdist to PyPI (or TestPyPI), and the new version appears on the index page.

**Acceptance Scenarios**:

1. **Given** `pyproject.toml` has all required PyPI metadata fields populated, **When** the maintainer runs `uv build`, **Then** both a `.whl` and a `.tar.gz` artifact are produced in `dist/` without errors.
2. **Given** built artifacts exist in `dist/`, **When** the maintainer runs `uv publish` with valid credentials, **Then** the package is accepted by PyPI and becomes installable.
3. **Given** the project uses `uv-dynamic-versioning`, **When** a git tag `vX.Y.Z` is pushed, **Then** the built artifacts carry the correct version derived from that tag.

---

### Edge Cases

- What happens when the package name `scaffold-ca-python` is already taken on PyPI? → The name must be verified as available or a unique alternative chosen before first publish.
- What happens when `uv build` is run without a valid git tag? → `uv-dynamic-versioning` falls back to a dev version (e.g., `0.0.0.dev0`); this is acceptable for test builds but should be documented.
- What happens when `README.md` contains relative image links? → Relative links render on GitHub but break on PyPI; only standard Markdown with absolute URLs should be used.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: `pyproject.toml` MUST declare all mandatory PyPI metadata: `name`, `version` (dynamic), `description`, `readme`, `license`, `authors`, `requires-python`, `keywords`, `classifiers`, and `urls` (Homepage, Repository, Issues).
- **FR-002**: The build system MUST produce a wheel (`*.whl`) and a source distribution (`*.tar.gz`) via `uv build`.
- **FR-003**: The `scaffold_ca_python/templates/` directory MUST be included in the wheel so the installed package can render templates.
- **FR-004**: `pyproject.toml` MUST specify `license` as an SPDX identifier (e.g., `MIT`) and the `LICENSE` file MUST exist at the project root.
- **FR-005**: The `README.md` MUST contain the following sections: project description, installation instructions (pip + uv), usage examples for all 10 CLI commands, technologies used, current features list, contributing guide, and license notice.
- **FR-006**: README MUST use standard Markdown without relative image links so it renders correctly on PyPI.
- **FR-007**: `pyproject.toml` MUST list `classifiers` appropriate for a CLI developer tool targeting Python ≥3.13.
- **FR-008**: The existing `uv-dynamic-versioning` setup MUST remain unchanged; version is derived from git tags using PEP 440 format.

### Key Entities

- **pyproject.toml**: The single source of truth for package metadata, build system, dependencies, and tooling configuration.
- **README.md**: The project's primary documentation surface, rendered on both GitHub and PyPI.
- **LICENSE**: The full license text file required by PyPI and most open-source norms.
- **dist/**: The output directory holding build artifacts (`*.whl`, `*.tar.gz`) created by `uv build`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `uv build` completes in under 30 seconds and produces both wheel and sdist artifacts with zero warnings.
- **SC-002**: The installed `scaffold` command works correctly in a clean virtual environment after `pip install scaffold-ca-python`.
- **SC-003**: The README renders without broken links or formatting errors on both GitHub and the PyPI project page.
- **SC-004**: A developer with no prior knowledge of the project can complete their first project scaffold (`scaffold ca --name my-app`) within 5 minutes of reading the README.
- **SC-005**: All required PyPI metadata fields are present; package upload is accepted by PyPI without validation errors.

## Assumptions

- The package name `scaffold-ca-python` is available on PyPI (or the maintainer will confirm/adjust before first publish).
- The project is licensed under MIT; if a different license applies, the maintainer will update the SPDX identifier.
- `uv publish` is used for publishing (not `twine`), consistent with the project's existing `uv` toolchain.
- A `LICENSE` file will be created if it does not already exist.
- Mobile / internationalization support is out of scope for the README (English only).
- CI/CD automation for publishing (GitHub Actions workflow) is out of scope for this feature; manual `uv build && uv publish` is sufficient.

