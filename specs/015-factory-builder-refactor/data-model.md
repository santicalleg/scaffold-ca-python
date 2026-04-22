# Data Model: CLI Factory + Builder Architecture Refactor

**Feature**: 015-factory-builder-refactor  
**Date**: 2026-04-14

---

## Entities

### ModuleFactory (Protocol)

**File**: `src/scaffold_ca_python/factory/__init__.py`

The structural contract for a type-specific module generator.

| Field / Method | Type | Description |
|---|---|---|
| `build(builder)` | `(ModuleBuilder) -> None` | Populate the builder with all files, dependencies, and parameters for this module type. Must not call `persist()`; that is the command's responsibility. |

**Validation**:
- All implementing classes must be `@runtime_checkable` compatible.
- Method signature is fixed; no additional parameters.

**State transitions**: None — this is a pure behaviour contract.

---

### ModuleBuilder

**File**: `src/scaffold_ca_python/core/module_builder.py`

Central orchestrator. Accumulates operations on behalf of factory classes and commits them atomically.

| Field | Type | Description |
|---|---|---|
| `project_root` | `Path` | Absolute path to the scaffold project root |
| `project_ctx` | `ProjectContext` | Resolved project context (name, package) |
| `module_ctx` | `ModuleContext \| None` | Resolved module context (name, layer, subtype) — None for project-level commands |
| `dry_run` | `bool` | When True, `persist()` skips disk writes |
| `_operations` | `list[FileOperation]` (private) | Accumulated file create/delete operations |
| `_dependencies` | `list[str]` (private) | Accumulated package specs to inject |
| `_params` | `dict[str, object]` (private) | Arbitrary key-value context available to factories |

**Public methods**:

| Method | Signature | Description |
|---|---|---|
| `add_file` | `(path: Path, content: str, *, template_name: str, is_test: bool = False, overwrite: bool = False) -> None` | Queue a `CreateFile` operation |
| `delete_file` | `(path: Path) -> None` | Queue a `DeleteFile` operation |
| `render` | `(template_name: str, context: BaseModel \| dict) -> str` | Render a Jinja2 template via `TemplateRenderer` |
| `add_dependency` | `(package: str) -> None` | Append a package spec to the dependency list |
| `add_param` | `(key: str, value: object) -> None` | Store an arbitrary key/value for factory use |
| `get_param` | `(key: str, default: object = None) -> object` | Retrieve a stored param |
| `persist` | `() -> list[Path]` | Commit all operations; if `dry_run=True`, no disk writes; returns affected paths |

> **Note on FR-003 "reading project properties"**: This requirement is satisfied by the
> `project_ctx: ProjectContext` and `module_ctx: ModuleContext` already available on the
> builder at construction time. Factories read project state (package name, project root,
> module layer, subtype) through these objects — no separate `read_file` or `get_property`
> method is needed. Factories that need to inspect the filesystem directly (e.g., checking
> whether a directory exists before queuing a file operation) call `pathlib.Path` methods
> on paths derived from `builder.project_root`; such reads are **not** suppressed in
> dry-run mode (only `persist()` skips writes).

**Validation rules**:
- `project_root` must be an existing directory at construction time.
- `persist()` is atomic: if any file write fails, no partial state is left on disk 
  (delegated to `FileWriter`'s staging behaviour).
- After `persist()` is called, the builder's internal state is considered consumed.

**Internal collaborators** (not exposed to factories):
- `FileWriter` — executes `_operations`
- `TemplateRenderer` — performs Jinja2 rendering in `render()`
- `pyproject_writer.inject_dependencies` / `dry_run_inject` — applies `_dependencies`

---

### Type Registry

**Location**: Top-level constant in each refactored command module.

| Field | Type | Description |
|---|---|---|
| `_REGISTRY` | `dict[str, type[ModuleFactory]]` | Maps type string → factory class for the owning command |

**Validation rules**:
- Registry keys must match the existing `_ALLOWED_TYPES` values exactly (no renames).
- An unrecognised key lookup raises a clear error listing valid keys.

**Example** (conceptual, in `generate_entry_point.py`):
```
_REGISTRY = {
    "restapi": EntryPointRestApi,
    "agent":   EntryPointAgent,
    "mcp":     EntryPointMcp,
    "generic": EntryPointGeneric,
}
```

---

### Concrete Factory Classes

**Location**: `src/scaffold_ca_python/factory/`

#### Entry-point factories (`factory/entry_points/`)

| Class | Type key | File |
|---|---|---|
| `EntryPointRestApi` | `restapi` | `ep_restapi.py` |
| `EntryPointAgent` | `agent` | `ep_agent.py` |
| `EntryPointMcp` | `mcp` | `ep_mcp.py` |
| `EntryPointGeneric` | `generic` | `ep_generic.py` |

Each class:
- Implements `ModuleFactory`
- Has one public method `build(builder: ModuleBuilder) -> None`
- May have private helper methods
- Imports only: `ModuleBuilder`, `ModuleFactory`, `ModuleContext`, `ProjectContext`, `Path`

#### Driven-adapter factories (`factory/driven_adapters/`)

| Class | Type key | File |
|---|---|---|
| `DrivenAdapterRestConsumer` | `rest-consumer` | `da_rest_consumer.py` |
| `DrivenAdapterSecrets` | `secrets` | `da_secrets.py` |
| `DrivenAdapterGeneric` | `generic` | `da_generic.py` |

#### Simple command factories (`factory/simple/`)

| Class | Command | File |
|---|---|---|
| `ModelFactory` | `gm` | `model_factory.py` |
| `UseCaseFactory` | `guc` | `use_case_factory.py` |
| `HelperFactory` | `gh` | `helper_factory.py` |
| `DeleteModuleFactory` | `dm` | `delete_module_factory.py` |

---

## Existing Entities (unchanged)

| Entity | Location | Notes |
|---|---|---|
| `ProjectContext` | `models/context.py` | Unchanged — passed to `ModuleBuilder` constructor |
| `ModuleContext` | `models/context.py` | Unchanged — passed to `ModuleBuilder` constructor |
| `FileOperation` | `models/file_operation.py` | Unchanged — internal to `ModuleBuilder` |
| `CreateFile` | `models/file_operation.py` | Unchanged |
| `DeleteFile` | `models/file_operation.py` | Unchanged |
| `GeneratedFile` | `models/file_operation.py` | Unchanged |
| `Layer` | `models/layer.py` | Unchanged |
| `FileWriter` | `core/file_writer.py` | Unchanged — internal collaborator of `ModuleBuilder` |
| `TemplateRenderer` | `core/template_renderer.py` | Unchanged — internal collaborator of `ModuleBuilder` |
| `pyproject_writer` | `core/pyproject_writer.py` | Unchanged — functions called by `ModuleBuilder` |

---

## File Layout Summary

```
src/scaffold_ca_python/
├── core/
│   ├── module_builder.py          # NEW — ModuleBuilder class
│   └── ... (unchanged)
├── factory/
│   ├── __init__.py                # NEW — ModuleFactory Protocol
│   ├── entry_points/
│   │   ├── __init__.py
│   │   ├── ep_restapi.py          # NEW
│   │   ├── ep_agent.py            # NEW
│   │   ├── ep_mcp.py              # NEW
│   │   └── ep_generic.py          # NEW
│   ├── driven_adapters/
│   │   ├── __init__.py
│   │   ├── da_rest_consumer.py    # NEW
│   │   ├── da_secrets.py          # NEW
│   │   └── da_generic.py          # NEW
│   └── simple/
│       ├── __init__.py
│       ├── model_factory.py        # NEW
│       ├── use_case_factory.py     # NEW
│       ├── helper_factory.py       # NEW
│       └── delete_module_factory.py # NEW
├── commands/
│   ├── generate_entry_point.py    # MODIFIED — thin + registry
│   ├── generate_driven_adapter.py # MODIFIED — thin + registry
│   ├── generate_model.py          # MODIFIED — uses ModuleBuilder
│   ├── generate_use_case.py       # MODIFIED — uses ModuleBuilder
│   ├── generate_helper.py         # MODIFIED — uses ModuleBuilder
│   └── delete_module.py           # MODIFIED — uses ModuleBuilder
└── ... (unchanged)
```
