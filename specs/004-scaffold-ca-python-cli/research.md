# Research: scaffold-ca-python CLI

**Phase**: 0 — Pre-design research  
**Feature**: `004-scaffold-ca-python-cli`  
**Date**: 2026-03-26

---

## R-01 — Typer Command Alias Strategy

**Decision**: Register every command twice — once with its full name and once with its short alias — each delegating to a shared implementation function.

**Rationale**: Typer's `@app.command(name=...)` accepts only a single string name. There is no native alias mechanism. The cleanest approach is to define the full implementation as a plain function and register two thin `@app.command(...)` wrappers that call it. This keeps logic DRY while exposing both names identically in `--help`.

**Pattern**:
```python
def _generate_project_impl(name: str, package: str) -> None: ...

@app.command("generate-project", help="Scaffold a CA project.")
def generate_project(name: str, package: str) -> None:
    """Scaffold a complete Clean Architecture Python project."""
    _generate_project_impl(name, package)

@app.command("ca", hidden=True, help="Alias for generate-project.")
def ca(name: str, package: str) -> None:
    _generate_project_impl(name, package)
```

**Alternatives considered**: Shell-level entry point aliases (rejected — requires setup.py entrypoints, not portable); Typer `add_typer` trick (rejected — no alias support either).

---

## R-02 — Typer App Structure

**Decision**: Flat `typer.Typer()` app with all commands registered at the top level (no nested sub-apps). Each command group lives in its own module under `commands/` but registers into the single global `app`.

**Rationale**: scaffold-ca-python has 11 commands — too few to warrant layered sub-commands (which would change the UX from `scaffold-ca-python gm --name X` to `scaffold-ca-python generate gm --name X`). A flat structure with clear module separation preserves the reference plugin's direct command UX. Each `commands/*.py` module exposes a `register(app)` function to keep `cli.py` clean.

---

## R-03 — Boolean Flag Naming (`--dry-run`)

**Decision**: Declare as `Annotated[bool, typer.Option("--dry-run/--no-dry-run")] = False`. Typer auto-converts underscores to hyphens, so `dry_run` becomes `--dry-run` automatically.

**Rationale**: Explicit `"--dry-run/--no-dry-run"` syntax provides both positive and negative forms in `--help` output, improving discoverability. No gotchas with hyphen/underscore conversion beyond this.

---

## R-04 — Non-Zero Exit Codes

**Decision**: Raise `raise typer.Exit(code=1)` for all non-zero exits. Do not use `sys.exit()`.

**Rationale**: Typer intercepts `typer.Exit` cleanly, printing no traceback. `sys.exit()` also works but bypasses any Typer cleanup. `typer.Abort()` is reserved for interactive prompts. Convention: code `0` = success, code `1` = user error or violation found, code `2` = tool/internal error.

---

## R-05 — Template Loading (installed vs. development)

**Decision**: Use `importlib.resources.files("scaffold_ca_python.templates")` as the primary template loader, with `pathlib` relative-path fallback for development mode.

**Rationale**: `importlib.resources.files()` (Python 3.9+, standard in 3.13) correctly resolves package data both after `pip install` (from wheel) and during development (from source tree), as long as `templates/` is declared as package data in `pyproject.toml` via `[tool.hatch.build.targets.wheel] packages = ["src/scaffold_ca_python"]`. `pkg_resources` is deprecated. Raw `pathlib` paths break post-install.

**pyproject.toml addition required**:
```toml
[tool.hatch.build.targets.wheel]
packages = ["src/scaffold_ca_python"]
```
Templates directory must contain `__init__.py` (empty) or be declared as a package data glob.

---

## R-06 — Jinja2 Atomic Rendering

**Decision**: Render all templates to a `tempfile.TemporaryDirectory`, validate, then `os.replace()` each into its final location. Roll back (delete temp dir) on any error.

**Rationale**: `os.replace()` is atomic on POSIX (macOS, Linux) within the same filesystem. Writing to a temp dir on the same volume as the target directory ensures same-filesystem renames. The approach guarantees no partial writes reach the project directory.

**Pattern**:
```python
with tempfile.TemporaryDirectory() as tmpdir:
    staged: list[tuple[Path, Path]] = []  # (temp_path, target_path)
    for path, content in rendered_files.items():
        tmp = Path(tmpdir) / path.name
        tmp.write_text(content, encoding="utf-8")
        staged.append((tmp, path))
    # All renders succeeded — commit
    for tmp, target in staged:
        target.parent.mkdir(parents=True, exist_ok=True)
        os.replace(tmp, target)
```

---

## R-07 — Pydantic as Jinja2 Rendering Context

**Decision**: Call `context_model.model_dump()` to convert the Pydantic context to a dict before passing to `Template.render(**ctx_dict)`.

**Rationale**: Pydantic v2 `model_dump()` produces a stable, nested dict. Jinja2 `render()` accepts `**kwargs`; spreading the dict makes every field directly addressable as `{{ name }}` in templates without namespace prefix. Computed properties (e.g., `snake_case`, `pascal_case`) should be added as Pydantic `@computed_field` or as Jinja2 environment filters.

---

## R-08 — AST-Based Import Analysis

**Decision**: Use `ast.parse()` on each `.py` file, walk `ast.Import` and `ast.ImportFrom` nodes, and check whether the module path prefix matches a forbidden outer-layer package.

**Pattern**:
```python
import ast

def extract_imports(source: str) -> list[str]:
    tree = ast.parse(source)
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules
```

**Out-of-scope edge cases** (documented, not implemented):
- Dynamic imports: `importlib.import_module(variable)` — cannot resolve statically
- `__import__()` calls — not caught by Import/ImportFrom nodes
- Conditional imports inside `if TYPE_CHECKING:` blocks — treated as violations if they cross layers (conservative)

**Rationale**: The `ast` module is part of the stdlib, has no dependencies, and is safe (does not execute code). These trade-offs are acceptable for a linting-style tool.

---

## R-09 — Dependency Update (`up` command)

**Decision**: Shell out to `uv lock --upgrade && uv sync` via `subprocess.run()` with argument list (never `shell=True`).

**Rationale**: `uv` has no Python API. `subprocess.run(["uv", "lock", "--upgrade"], check=True, cwd=project_root)` is the idiomatic pattern. Arguments passed as a list prevent shell injection. `check=True` raises `CalledProcessError` on non-zero exit, which the command handler catches and re-surfaces as a user-friendly Rich error.

---

## R-10 — Project Root Detection

**Decision**: Walk up from `cwd` looking for a `pyproject.toml` that contains a `[tool.scaffold-ca-python]` section. If not found, fall back to detecting the canonical CA directory layout (`domain/`, `infrastructure/`, `application/`). Fail with a clear error if neither is found.

**Rationale**: Using `pyproject.toml` as the root marker is standard in the Python ecosystem (pip, pytest, ruff, mypy all do this). The `[tool.scaffold-ca-python]` section acts as a project fingerprint so the tool does not inadvertently operate on unrelated Python projects.

---

## R-11 — `--name` Input Validation Boundary

**Decision**: Strict allowlist — `--name` MUST match `^[A-Za-z][A-Za-z0-9_]*$`. Validation runs at CLI parse time via a Typer callback; any non-matching input is rejected before any file I/O begins.

**Rationale**: Restricting to valid Python identifier characters eliminates path-traversal attacks (`../`, null bytes, absolute paths). The CLI converts the validated name to snake_case for filenames and PascalCase for class names, informing the user of any normalisation applied. Hyphens in external type strings (`rest-consumer`, `rest-client`) are valid because they are enumerated constants, not user-supplied names.

---

## Summary of NEEDS CLARIFICATION items

All items resolved. No open unknowns remain before Phase 1 design.
