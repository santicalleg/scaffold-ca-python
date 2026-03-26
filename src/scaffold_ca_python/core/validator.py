"""AST-level static import analysis for `scaffold validate`."""
from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Violation:
    file: Path
    import_stmt: str
    offending_layer: str
    rule: str


# Layer paths relative to the project package root.
# Ordered longest-first so find_layer() matches the most specific prefix.
ALL_LAYERS: list[str] = [
    "domain/model/gateways",
    "domain/model",
    "domain/usecase",
    "infrastructure/driven_adapters",
    "infrastructure/entry_points",
    "infrastructure/helpers",
    "app",
    "deployment",
]

# Which layers each layer is ALLOWED to import from.
# Key: layer path; Value: list of permitted source layers.
LAYER_RULES: dict[str, list[str]] = {
    "domain/model/gateways":          [],
    "domain/model":                   [],
    "domain/usecase":                 ["domain/model", "domain/model/gateways"],
    "infrastructure/driven_adapters": ["domain/model", "domain/model/gateways"],
    "infrastructure/entry_points":    ["domain/model", "domain/model/gateways", "domain/usecase"],
    "infrastructure/helpers":         [],
    "app":                            ALL_LAYERS,   # composition root — may import anything
    "deployment":                     [],
}


def find_layer(file: Path, package_root: Path) -> str | None:
    """Return the layer path for *file* relative to *package_root*, or None."""
    try:
        rel = file.relative_to(package_root).as_posix()
    except ValueError:
        return None
    for layer in ALL_LAYERS:
        if rel.startswith(layer + "/") or rel == layer:
            return layer
    return None


def extract_imports(file: Path) -> list[str]:
    """Return all imported module names from a Python source file."""
    try:
        source = file.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(file))
    except (SyntaxError, OSError):
        return []

    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.append(alias.name)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
    return names


def _layer_of_import(module: str, package: str) -> str | None:
    """Return the layer path if *module* belongs to *package*, else None."""
    pkg_prefix = package + "."
    if module == package:
        return None  # top-level package import — not a layer violation
    if not module.startswith(pkg_prefix):
        return None
    rest = module[len(pkg_prefix):]
    for layer in ALL_LAYERS:
        layer_mod = layer.replace("/", ".")
        if rest == layer_mod or rest.startswith(layer_mod + "."):
            return layer
    return None


def validate_project(project_root: Path) -> list[Violation]:
    """Walk *project_root* and return all cross-layer dependency violations.

    Raises ValueError if no .scaffold-ca.json is found (use find_project_root first).
    """
    from scaffold_ca_python.core.project import ProjectMarker

    marker = ProjectMarker.load(project_root)
    package = marker.base_package
    package_root = project_root / package

    violations: list[Violation] = []

    for py_file in sorted(package_root.rglob("*.py")):
        if "__pycache__" in py_file.parts:
            continue

        layer = find_layer(py_file, package_root)
        if layer is None:
            continue

        allowed = LAYER_RULES.get(layer, list(ALL_LAYERS))
        for imp in extract_imports(py_file):
            imp_layer = _layer_of_import(imp, package)
            if imp_layer is None or imp_layer == layer:
                continue
            if imp_layer not in allowed:
                violations.append(Violation(
                    file=py_file,
                    import_stmt=imp,
                    offending_layer=imp_layer,
                    rule=(
                        f"Layer '{layer}' must not import from layer '{imp_layer}'. "
                        f"Allowed imports: {allowed if allowed else 'none'}"
                    ),
                ))

    return violations
