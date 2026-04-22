# Developer Quickstart: CLI Factory + Builder Architecture Refactor

**Feature**: 015-factory-builder-refactor  
**Audience**: Contributors adding a new module type or working on the refactored command layer

---

## How to add a new module type (after this feature lands)

To add, say, a new entry-point type `grpc` to `scaffold gep`:

### 1. Create the factory file

```
src/scaffold_ca_python/factory/entry_points/ep_grpc.py
```

```python
from scaffold_ca_python.core.module_builder import ModuleBuilder
from scaffold_ca_python.factory import ModuleFactory


class EntryPointGrpc(ModuleFactory):
    def build(self, builder: ModuleBuilder) -> None:
        ctx = builder.module_ctx
        assert ctx is not None

        content = builder.render("entry_point/grpc/servicer.py.jinja2", ctx)
        builder.add_file(
            builder.project_root / "src" / ... / "servicer.py",
            content,
            template_name="entry_point/grpc/servicer.py.jinja2",
        )
        builder.add_dependency("grpcio>=1.60")
```

### 2. Register it

In `src/scaffold_ca_python/commands/generate_entry_point.py`, add one line:

```python
from scaffold_ca_python.factory.entry_points.ep_grpc import EntryPointGrpc

_REGISTRY: dict[str, type[ModuleFactory]] = {
    "restapi": EntryPointRestApi,
    "agent":   EntryPointAgent,
    "mcp":     EntryPointMcp,
    "generic": EntryPointGeneric,
    "grpc":    EntryPointGrpc,   # ← one line
}
```

That is the complete change. No other files need modification.

---

## How to run tests after a change

```bash
# Run all tests with coverage
uv run pytest

# Run just the command tests to check for regressions
uv run pytest tests/commands/ -q --no-cov

# Run only factory-layer tests
uv run pytest tests/factory/ -q --no-cov

# Lint + format check
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/

# Type check
uv run mypy src/
```

---

## How ModuleBuilder is used in a command (typical flow)

```python
# 1. Resolve project context (unchanged — same as before)
project_root = find_project_root()
project_ctx  = _load_project_context(project_root)
module_ctx   = ModuleContext(name=name, layer=Layer.ENTRY_POINTS, project=project_ctx)

# 2. Look up factory from registry
factory_class = _REGISTRY.get(type_)
if factory_class is None:
    # error: unknown type, list valid types from _REGISTRY.keys()

# 3. Construct builder
builder = ModuleBuilder(
    project_root=project_root,
    project_ctx=project_ctx,
    module_ctx=module_ctx,
    dry_run=dry_run,
)

# 4. Run factory
factory_class().build(builder)

# 5. Persist (writes files + deps, or previews if dry_run)
builder.persist()
```

---

## File layout under `factory/`

```
src/scaffold_ca_python/factory/
├── __init__.py                  ← ModuleFactory Protocol lives here
├── entry_points/
│   ├── ep_restapi.py
│   ├── ep_agent.py
│   ├── ep_mcp.py
│   └── ep_generic.py
├── driven_adapters/
│   ├── da_rest_consumer.py
│   ├── da_secrets.py
│   └── da_generic.py
└── simple/
    ├── model_factory.py
    ├── use_case_factory.py
    ├── helper_factory.py
    └── delete_module_factory.py
```

---

## What NOT to import in factory files

Factory files must not import these — call `builder` methods instead:

| Forbidden direct import | Use instead |
|---|---|
| `FileWriter` | `builder.add_file(...)` |
| `TemplateRenderer` | `builder.render(...)` |
| `inject_dependencies` / `dry_run_inject` | `builder.add_dependency(...)` |
| `pyproject_writer` (module) | `builder.add_dependency(...)` |

---

## Verifying the architectural constraint automatically

A `mypy` check + import linter rule will enforce FR-007. If a factory file imports 
any forbidden symbol, ruff's `I` (isort/import) rules combined with a custom 
`noqa` discipline will surface the violation. The constitution notes `ruff` as sole 
linter; no additional tooling is added.
