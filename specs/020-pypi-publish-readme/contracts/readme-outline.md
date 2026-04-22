# Contract: README Structure

**Feature**: `020-pypi-publish-readme`
**File**: `README.md` at repository root
**Renders on**: GitHub project page, PyPI project page (`https://pypi.org/project/scaffold-ca-python/`)

---

## Rendering Constraints

- Format: CommonMark / GitHub Flavored Markdown
- No relative image or link paths (PyPI cannot resolve them)
- Any badges must use absolute Shields.io URLs
- Code blocks must use fenced syntax with a language identifier (`bash`, `python`, `toml`)
- No raw HTML (PyPI strips most attributes; keep it pure Markdown)

---

## Required Sections (in order)

### Section 1 — Title & Badges

```markdown
# scaffold-ca-python

[![PyPI version](https://img.shields.io/pypi/v/scaffold-ca-python.svg)](https://pypi.org/project/scaffold-ca-python/)
[![Python](https://img.shields.io/pypi/pyversions/scaffold-ca-python.svg)](https://pypi.org/project/scaffold-ca-python/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
```

- H1 heading with the exact package name
- Three badges: PyPI version, Python versions, License
- All badge URLs must be absolute

---

### Section 2 — What is this?

```markdown
## What is this?
```

**Contract**:
- 2–4 sentences maximum
- Must mention: Clean Architecture, Python projects, CLI tool, code scaffolding
- Must NOT mention implementation details (framework names like Typer) — keep it user-facing

**Acceptance check**: A developer unfamiliar with Clean Architecture should understand the purpose after reading this section.

---

### Section 3 — Installation

```markdown
## Installation
```

**Contract**:
- Must show `pip` install command in a fenced `bash` block
- Must show `uv add` install command in a fenced `bash` block
- Must mention Python ≥3.13 requirement
- Must NOT show source install instructions (not the purpose of this feature)

**Required content**:
```bash
pip install scaffold-ca-python
```
```bash
uv add scaffold-ca-python
```

---

### Section 4 — Quick Start

```markdown
## Quick Start
```

**Contract**:
- Linear, numbered walkthrough (3–5 steps)
- Steps: install → create project → add a model → verify structure
- Each step has a fenced `bash` code block
- No prose-only steps — every step must have a runnable command

---

### Section 5 — Commands & Examples

```markdown
## Commands & Examples
```

**Contract**:
- One `###` sub-section per command (10 total; order matches CLI help output)
- Each sub-section contains:
  1. One-line description (plain text)
  2. A fenced `bash` block with the most common invocation
  3. Optional: a second example showing `--dry-run` or a type variant
- Must not reproduce entire `--help` output — only the essential usage

**Required sub-sections**:

| Sub-heading | Command alias |
|-------------|--------------|
| `### scaffold ca` | `clean-architecture` |
| `### scaffold gm` | `generate-model` |
| `### scaffold guc` | `generate-use-case` |
| `### scaffold gda` | `generate-driven-adapter` |
| `### scaffold gep` | `generate-entry-point` |
| `### scaffold gh` | `generate-helper` |
| `### scaffold gpipe` | `generate-pipeline` |
| `### scaffold vs` | `validate-structure` |
| `### scaffold dm` | `delete-module` |
| `### scaffold up` | `update-project` |

---

### Section 6 — Technologies

```markdown
## Technologies
```

**Contract**:
- Markdown table with columns: Tool/Library | Version | Role
- Must include all entries from `data-model.md` Technologies table
- Version column uses `≥X.Y` format or `latest` for tooling (not pinned to patch versions)

---

### Section 7 — Current Features

```markdown
## Current Features
```

**Contract**:
- Bullet list; one bullet per implemented capability
- Must cover at minimum: all 10 CLI commands, `--dry-run` support, Jinja2 templates, Pydantic v2 validation, Rich output, mypy strict + ruff linting, 80%+ test coverage gate
- Language: present tense ("Generates…", "Validates…", "Supports…")

---

### Section 8 — Contributing

```markdown
## Contributing
```

**Contract**:
- Numbered step list
- Steps must include:
  1. Fork the repository
  2. Clone the fork: `git clone …`
  3. Set up dev environment: `uv sync` (or `uv sync --dev`)
  4. Create a feature branch
  5. Run tests: `uv run pytest`
  6. Check linting: `uv run ruff check src tests`
  7. Check types: `uv run mypy src`
  8. Open a pull request

---

### Section 9 — License

```markdown
## License
```

**Contract**:
- Single sentence with SPDX identifier: "This project is licensed under the **MIT License**."
- Link to `LICENSE` file using the absolute GitHub raw URL OR a relative markdown link (GitHub renders it; PyPI will tolerate a relative link for the LICENSE file since it is a single anchor, not an image)
- No copy of the license text inline
