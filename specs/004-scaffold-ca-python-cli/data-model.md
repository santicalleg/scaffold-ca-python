# Data Model: scaffold-ca-python CLI

**Phase**: 1 — Design  
**Feature**: `004-scaffold-ca-python-cli`  
**Date**: 2026-03-26

---

## Overview

These are the **internal entities** of the CLI tool itself — not the domain models of generated projects. They describe the data structures the tool uses to orchestrate code generation, structural validation, and file I/O.

---

## Entities

### `ProjectContext`

The rendering context passed to every Jinja2 template when generating a new project or any module within it. Created once per `ca` invocation and persisted (as a `[tool.scaffold-ca-python]` section in `pyproject.toml`) so subsequent commands can read it.

```python
class ProjectContext(BaseModel):
    name: str                  # PascalCase project name, e.g. "MyProject"
    package: str               # Dot-notation package identifier, e.g. "com.example"
    python_package: str        # Snake-case import root, e.g. "my_project"
    created_at: datetime       # ISO 8601 timestamp of project creation
```

**Constraints**:
- `name` must match `^[A-Za-z][A-Za-z0-9_]*$` after normalisation.
- `python_package` is derived from `name` by lowercasing and replacing non-alnum with `_`.
- Persisted under `[tool.scaffold-ca-python]` in the generated project's `pyproject.toml`.

---

### `ModuleContext`

The rendering context for any single module generated inside an existing project (`gm`, `guc`, `gda`, `gep`, `gh`). Passed to the relevant Jinja2 templates for that module type.

```python
class ModuleContext(BaseModel):
    name: str                  # User-supplied name, validated and normalised
    class_name: str            # PascalCase class name, derived from name
    module_name: str           # snake_case file name (no .py), derived from name
    layer: Layer               # The layer where this module lives
    subtype: str | None        # For typed commands: "rest-consumer", "mcp", etc.
    project: ProjectContext    # Parent project context
```

---

### `Layer`

An enumeration of the six structural positions in a generated Clean Architecture project.

```python
class Layer(str, Enum):
    DOMAIN_MODEL    = "domain/model"
    DOMAIN_USECASE  = "domain/usecase"
    ENTRY_POINTS    = "infrastructure/entry-points"
    DRIVEN_ADAPTERS = "infrastructure/driven-adapters"
    HELPERS         = "infrastructure/helpers"
    APPLICATION     = "application"
```

**Dependency order (inner → outer)**:
```
DOMAIN_MODEL → DOMAIN_USECASE → ENTRY_POINTS / DRIVEN_ADAPTERS / HELPERS → APPLICATION
```

A `Violation` is raised when a module in an inner layer imports from any module in an outer layer.

---

### `GeneratedFile`

Represents a single file that the tool intends to create or delete, used by both the rendering pipeline and the dry-run preview.

```python
class GeneratedFile(BaseModel):
    path: Path                 # Absolute path on disk
    content: str               # Rendered file content (empty string for directories)
    is_test: bool = False      # True if this is a test mirror file
    template_name: str         # The Jinja2 template that produced this file
```

**Used by**: `FileWriter`, dry-run formatter, rollback manifest.

---

### `FileOperation`

A union type representing the intent to create or delete a file. Used by `FileWriter` to stage operations before committing.

```python
class CreateFile(BaseModel):
    kind: Literal["create"] = "create"
    file: GeneratedFile

class DeleteFile(BaseModel):
    kind: Literal["delete"] = "delete"
    path: Path

FileOperation = CreateFile | DeleteFile
```

---

### `Violation`

Produced by the `StructureValidator` when it finds a dependency-rule breach. Reported by the `vs` command.

```python
class Violation(BaseModel):
    source_file: Path          # The file containing the offending import
    line_number: int           # 1-based line number of the import statement
    import_statement: str      # The raw import string, e.g. "from infrastructure.driven_adapters..."
    source_layer: Layer        # The layer the importing module belongs to
    target_layer: Layer        # The (outer) layer being incorrectly imported
    resolution_hint: str       # Human-readable fix suggestion
```

---

### `ValidationReport`

The aggregate result returned by `StructureValidator.validate()` and consumed by the `vs` command for Rich output and exit code determination.

```python
class ValidationReport(BaseModel):
    project_root: Path
    files_scanned: int
    violations: list[Violation]

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0
```

---

### `TemplateDescriptor`

Metadata about a Jinja2 template file used by the `TemplateRenderer` to locate and render templates.

```python
class TemplateDescriptor(BaseModel):
    name: str                  # Template file name relative to templates/, e.g. "domain/model.py.jinja2"
    output_path_template: str  # Jinja2 expression producing the output path, e.g. "domain/model/{{ module_name }}.py"
    is_test: bool = False      # True if this template produces a test file
```

---

## Internal Component Relationships

```
CLI command (cli.py / commands/)
    │
    ├── ProjectDetector          ← finds project root, loads ProjectContext
    ├── TemplateRenderer         ← loads TemplateDescriptor, renders GeneratedFile list
    ├── FileWriter               ← stages FileOperation list, commits or dry-runs
    │       └── uses tempdir + os.replace() for atomicity
    └── StructureValidator       ← walks .py files, produces ValidationReport
            └── uses ast.parse() on each file
```

---

## State Persistence

The tool persists minimal state in the generated project's `pyproject.toml` under `[tool.scaffold-ca-python]`. This is the only cross-invocation state.

```toml
[tool.scaffold-ca-python]
name = "MyProject"
package = "com.example"
python_package = "my_project"
created_at = "2026-03-26T10:00:00Z"
```

No database, no lock files, no separate config files.
