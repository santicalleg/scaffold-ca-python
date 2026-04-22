# Research: CLI Factory + Builder Architecture Refactor

**Feature**: 015-factory-builder-refactor  
**Date**: 2026-04-14  
**Status**: Complete — no NEEDS CLARIFICATION items remain

---

## Decision 1: Factory contract — Protocol vs ABC

**Decision**: Use `typing.Protocol` (structural subtyping) for the `ModuleFactory` contract.

**Rationale**: All existing infrastructure in this project is Python 3.13 + strict mypy.  
`typing.Protocol` provides duck-typed structural subtyping without requiring `super().__init__()` 
calls or multiple-inheritance boilerplate. Factory classes are pure behaviour, making 
a structural contract more natural than a nominal one. An ABC would force every factory to 
inherit from a base class, creating a harder coupling that the spec explicitly wants to avoid.  
`@runtime_checkable` on the Protocol enables `isinstance` guards for the registry if needed.

**Alternatives considered**:
- `abc.ABC` with `@abstractmethod` — would work but creates nominal coupling and requires 
  importing `abc` in every factory file, leaking a non-domain concern.
- Plain duck-typing (no formal contract) — rejected because mypy strict mode requires an 
  explicit type for the factory callable stored in the registry.

---

## Decision 2: ModuleBuilder — new class vs thin wrapper over FileWriter

**Decision**: `ModuleBuilder` is a new class in `src/scaffold_ca_python/core/module_builder.py` 
that holds references to `FileWriter`, `TemplateRenderer`, and the `pyproject_writer` functions 
as internal collaborators. Existing lower-level utilities are **not** modified.

**Rationale**: The spec's "Assumption" section explicitly states the builder wraps rather than 
replaces existing utilities. The lower-level classes (`FileWriter`, `TemplateRenderer`) have their 
own tests, good coverage, and stable interfaces. Wrapping them preserves that test coverage 
while hiding them from factory code. This also keeps the change set minimal: only one new file 
added to `core/`, no edits to existing `core/` files.

**Alternatives considered**:
- Merging `FileWriter` into `ModuleBuilder` — rejected; more destructive, would require updating 
  all existing tests that directly instantiate `FileWriter`.
- Passing the lower-level collaborators as constructor arguments to `ModuleBuilder` —  
  chosen as the actual implementation approach for testability (allows injecting mocks).

---

## Decision 3: Type registry storage location

**Decision**: Each command module gets its own `_REGISTRY: dict[str, type[ModuleFactory]]` 
constant defined at module level, directly below (or replacing) the existing `_ALLOWED_TYPES` 
tuple.

**Rationale**: Keeping the registry adjacent to the command that owns it avoids creating a 
global module-registry indirection that would be harder to navigate. The registry IS the 
`_ALLOWED_TYPES` tuple — it extends it with factory class references. This satisfies 
FR-006 (single location per command) without adding a new module.

**Alternatives considered**:
- Central `factory/registry.py` with all registries — rejected; creates cross-command coupling 
  and means reading two files to understand one command's type set.
- Lazy-registration decorator pattern (each factory self-registers) — rejected; too clever, 
  would make the type set invisible without running the import.

---

## Decision 4: Factory file location — flat vs per-command subdirectory

**Decision**: Factory implementations live under a new `src/scaffold_ca_python/factory/` 
sub-package, organized by command group:
```
factory/
├── __init__.py
├── entry_points/
│   ├── __init__.py
│   ├── ep_restapi.py
│   ├── ep_agent.py
│   ├── ep_mcp.py
│   └── ep_generic.py
└── driven_adapters/
    ├── __init__.py
    ├── da_rest_consumer.py
    ├── da_secrets.py
    └── da_generic.py
```
Single-type commands (`gm`, `guc`, `gh`) mirror the pattern with a single factory each 
under `factory/simple/`.

**Rationale**: Mirrors the Java reference layout (`factory/entrypoints/`, `factory/adapters/`).  
A sub-package per command group makes it easy to scan available types and supports the SC-002 
requirement (one file = one type). Flat layout was rejected because it would produce 
10+ files in a single directory with no grouping signal.

**Alternatives considered**:
- `commands/factories/` (co-locate with commands) — requires navigating into `commands/` to 
  add a factory; feels wrong because factories are not CLI concerns.
- `core/factories/` — rejected; `core/` is for infrastructure utilities, not domain dispatch.

---

## Decision 5: `ModuleBuilder.persist()` return type in dry-run mode

**Decision**: `persist()` always returns `list[Path]`. In dry-run mode it returns the paths that 
would be written (delegated to `FileWriter.execute(dry_run=True)`). In real mode it returns 
the paths that were written. This matches the existing `FileWriter.execute()` contract exactly.

**Rationale**: Uniform return type means callers use one code path for both modes. 
The existing dry-run display logic (building a `rich.Tree` from paths) remains unchanged — 
it already consumes `list[Path]`. Changing the return type (e.g., returning a structured dict 
in dry-run) would require updating all display code and break the existing abstraction.

**Alternatives considered**:
- `persist()` returns `None` in real mode, `list[dict]` in dry-run — rejected; 
  inconsistent return type complicates typing.
- Two separate methods (`persist()` / `dry_run_preview()`) — plausible but adds surface area; 
  the `dry_run` flag is already established project convention.

---

## Decision 6: Exclusivity guard placement post-refactor

**Decision**: The entry-point exclusivity guard (restapi ↔ mcp/agent conflict check) stays 
in the command module (`generate_entry_point.py`), not in individual factory classes.

**Rationale**: The guard is a cross-type concern: adding `restapi` must check for `mcp` AND 
`agent`, and vice versa. It cannot live purely in one factory because it needs to know about 
the others. Placing it in the command module (which already has project-root context) keeps 
it in one place. Placing copies in each factory would be duplication and violate FR-011's 
"preserved" intent.

**Alternatives considered**:
- Dedicated `validate_entry_point_compatibility(type_, project_root)` function in `core/` — 
  valid, but adds a function for a concern that is already cleanly in the command module.
- Pre-condition method on `ModuleBuilder` — rejected; builder should not know about 
  entry-point-specific constraints.

---

## Decision 7: Commands with single dispatch paths (gm, guc, gh, gpipe, dm)

**Decision**: `generate_model`, `generate_use_case`, `generate_helper`, and `delete_module` 
are refactored to use `ModuleBuilder` (satisfying FR-007) and have a single-entry registry, 
but their logic path is not meaningfully changed. `generate_pipeline` and `validate_structure` 
are **out of scope** — they have no module-type dispatch and no `FileWriter`/deps pattern to 
migrate.

**Rationale**: `gpipe` generates pipeline YAML using a different file path pattern and has no 
dependency injection. `vs` is purely analytical. Forcing them through the Factory + Builder 
pattern would be over-engineering with no benefit. The spec acknowledges these as 
"simpler single-path cases" and scopes `generate_pipeline` and `validate_structure` out.

**Alternatives considered**:
- Migrate all commands uniformly — rejected as over-engineering per spec non-goals.
