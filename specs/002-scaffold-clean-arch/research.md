# Research: Python Clean Architecture Scaffold

**Branch**: `002-scaffold-clean-arch` | **Date**: 2026-03-25

---

## 1. CLI Framework — Typer

**Decision**: Use the existing `typer` dependency (`≥ 0.16`).

**Rationale**:
- Already installed in `pyproject.toml`; zero new dependency cost.
- Provides nested subcommand groups natively (`app.add_typer(generate_app, name="generate")`), which maps cleanly to `scaffold new`, `scaffold generate model`, `scaffold generate use-case`, etc.
- Type-annotated signatures give free `--help` documentation, validation, and shell completion.
- `typer.Exit(code=1)` enables clean non-zero exit on validation errors without raising exceptions to the user.

**Alternatives considered**:
- Click (lower-level, more boilerplate, no type annotations natively).
- argparse (stdlib, very verbose for nested commands).

---

## 2. Terminal Output — Rich

**Decision**: Use the existing `rich` dependency (`≥ 14.1`).

**Rationale**:
- Already installed; provides coloured status messages (✅ green for success, ❌ red for errors, ⚠️ yellow for warnings), file-tree rendering, and tables for `scaffold list`.
- Respects `NO_COLOR` and `TERM=dumb` automatically (important for CI environments).
- `--quiet` flag: disable Rich console output, redirect to stderr only.
- `--verbose` flag: use `Console(stderr=True)` for debug traces alongside stdout output.

**Alternatives considered**:
- Plain `print()` — insufficient for UX goals (SC-006).

---

## 3. Template Engine — Jinja2

**Decision**: Add `jinja2` as a runtime dependency.

**Rationale**:
- De-facto standard for Python code generation; supports variable substitution, whitespace control, conditional blocks, and loops needed for adapter stubs.
- Templates are shipped as package data files under `src/scaffold_ca_python/templates/` — included in the wheel via `tool.hatch.build.include` in `pyproject.toml`.
- `Environment(loader=PackageLoader("scaffold_ca_python", "templates"), keep_trailing_newline=True, autoescape=False)` — autoescape off since we generate Python code, not HTML.
- Templates are `.py.jinja2` files (e.g., `use_case/use_case.py.jinja2`) to preserve Python syntax highlighting in editors.

**Alternatives considered**:
- `string.Template` (stdlib) — too limited; no conditionals or loops.
- Mako — heavier, less familiar community.
- Inline f-strings — not scalable for 18+ component types.

---

## 4. Project Marker — `.scaffold-ca.json`

**Decision**: Plain JSON file at project root, managed via `json` stdlib module.

**Schema** (resolved from spec FR-020):
```json
{
  "scaffold_version": "1.0.0",
  "name": "my_project",
  "package": "my_project",
  "mode": "sync",
  "created_at": "2026-03-25T10:00:00Z",
  "components": [
    {
      "type": "use_case",
      "name": "ProcessOrder",
      "layer": "domain/usecase",
      "files": ["domain/usecase/process_order_use_case.py", "tests/unit/usecase/test_process_order_use_case.py"]
    }
  ]
}
```

**Rationale**:
- Human-readable, version-controllable, no extra dependency.
- JSON stdlib is always available.
- Detection heuristic for `scaffold generate/validate/delete/update`: walk up the directory tree from `cwd` until `.scaffold-ca.json` is found or filesystem root is reached.

**Alternatives considered**:
- TOML (`tomllib`, stdlib in 3.11+) — write support requires `tomli-w` extra dep; JSON is simpler for read+write.
- SQLite — overkill for a flat component registry.

---

## 5. AST-Level Import Validator

**Decision**: Use Python stdlib `ast` module for static import analysis in `scaffold validate`.

**Rationale**:
- `ast.parse()` + `ast.walk()` extracts all `import` and `from ... import` statements without executing code.
- Layer membership determined by file path relative to project root (e.g., any file under `domain/model/` is in the `model` layer).
- Cross-layer violation check: for each import in a file, resolve the imported module to a layer; check against the allowed dependency matrix.
- Out of scope for v1: circular import detection within the same layer.
- Exits with code 1 and prints the violating file + rule on failure (testable via SC-005).

**Alternatives considered**:
- `pylint` / `flake8` plugins — external tools, require installation in the generated project.
- `importlib` runtime tracing — requires executing the code, violates offline/safe constraint.
- `py-import-cycles` — extra dependency for in-scope detection.

---

## 6. Name Normalization

**Decision**: Implement a `core/naming.py` module with two functions:

```python
def to_snake_case(name: str) -> str: ...   # PascalCase / camelCase / kebab-case → snake_case
def to_pascal_case(name: str) -> str: ...  # snake_case → PascalCase
```

**Rules**:
- PascalCase input (`ProcessOrder`) → snake `process_order`, class `ProcessOrder`.
- camelCase (`processOrder`) → snake `process_order`, class `ProcessOrder`.
- kebab-case (`process-order`) → snake `process_order`, class `ProcessOrder`.
- Already-snake (`process_order`) → unchanged.
- Python reserved keywords → rejected with `FR-015` error before any file write.
- Names > 100 characters → rejected with error (edge case from spec).

**Alternatives considered**:
- `inflection` library — extra dep for simple transformations.

---

## 7. Sync vs Async Project Mode

**Decision**: `scaffold new --async` flag switches the project mode. Templates branch via Jinja2 `{% if async_mode %}` conditionals.

**Rationale**:
- Async mode generates `async def` methods and `asyncio`-aware entry point stubs.
- Sync mode generates plain `def` methods.
- Mode is stored in `.scaffold-ca.json` and respected by all subsequent `generate` commands (new component stubs inherit the project's mode).
- Async-specific driven adapter types (e.g., `kafka-sender`, `sqs-sender`) are available in both modes but annotated accordingly.

---

## 8. Packaging — Templates as Package Data

**Decision**: Templates shipped inside the wheel via `hatchling` include directive.

```toml
[tool.hatch.build.targets.wheel]
include = [
  "src/scaffold_ca_python/",
]

[tool.hatch.build.targets.sdist]
include = [
  "src/scaffold_ca_python/",
]
```

The template directory is accessed via `importlib.resources.files("scaffold_ca_python") / "templates"` (Python 3.9+ API, confirmed available in 3.13+).

**Alternatives considered**:
- Shipping templates as a separate data package — unnecessary complexity for v1.
- `pkg_resources` — deprecated.

---

## 9. `scaffold update` — Boilerplate Detection Strategy

**Decision**: A file is considered "boilerplate" if its path appears in the `files` list of a `__boilerplate__` sentinel component in `.scaffold-ca.json` (populated by `scaffold new`). Files in `domain/` and `infrastructure/` that were registered as component stubs (not boilerplate) are never touched by `update`.

**Conflict resolution** (from spec FR-013 clarification):
1. Compute SHA-256 of the current file vs. the template-rendered version.
2. If they differ → file was manually edited → write `.bak` backup → overwrite → report.
3. If they match → silently overwrite (no user change to preserve).

**Alternatives considered**:
- Git diff to detect modifications — requires Git to be available; fragile in CI.
- Timestamp comparison — unreliable across clones and checkouts.

---

## 10. `scaffold validate` — Dependency Matrix

```
model       → (no imports allowed from other layers)
usecase     → model only
driven_adapters → domain (model + usecase allowed), helpers
entry_points    → domain (model + usecase allowed), helpers
helpers         → domain (model + usecase allowed)
app             → any layer (composition root)
```

Detection heuristic: map absolute import paths to layers by matching against the package root. Relative imports are resolved relative to the current file's layer.

---

## Resolved NEEDS CLARIFICATION Items

All five clarifications were resolved in `/speckit.clarify`:

| Topic | Resolution |
|---|---|
| Package namespace | Flat Python: last `--package` segment = top-level dir |
| Marker file format | `.scaffold-ca.json` (JSON, stdlib) |
| CLI verbosity | Human-readable default; `--quiet` / `--verbose` on all commands |
| `update` conflict handling | SHA-256 diff → `.bak` backup before overwrite |
| `validate` scope | Cross-layer directional violations only; intra-layer circular imports out of scope v1 |
