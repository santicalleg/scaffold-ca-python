"""StructureValidator: AST-based Clean Architecture import checker (T059)."""

from __future__ import annotations

import ast
from pathlib import Path

from scaffold_ca_python.core.name_utils import ScaffoldError
from scaffold_ca_python.models.layer import FORBIDDEN_IMPORTS, Layer
from scaffold_ca_python.models.violation import ValidationReport, Violation

# ---------------------------------------------------------------------------
# Path → Layer mapping (filesystem directory names use underscores)
# ---------------------------------------------------------------------------

_PATH_SEGMENTS_TO_LAYER: list[tuple[tuple[str, ...], Layer]] = [
    (("domain", "model"), Layer.DOMAIN_MODEL),
    (("domain", "usecase"), Layer.DOMAIN_USECASE),
    (("infrastructure", "entry_points"), Layer.ENTRY_POINTS),
    (("infrastructure", "driven_adapters"), Layer.DRIVEN_ADAPTERS),
    (("infrastructure", "helpers"), Layer.HELPERS),
    (("application",), Layer.APPLICATION),
]


def _layer_from_path_parts(parts: tuple[str, ...]) -> Layer | None:
    """Return the Layer for *parts* (relative to the package root), or None."""
    for segments, layer in _PATH_SEGMENTS_TO_LAYER:
        n = len(segments)
        if len(parts) >= n and parts[:n] == segments:
            return layer
    return None


def _layer_from_module(module: str, python_package: str) -> Layer | None:
    """Return the Layer that *module* belongs to, or None if not project-internal."""
    parts = tuple(module.split("."))
    if not parts or parts[0] != python_package:
        return None
    return _layer_from_path_parts(parts[1:])


def _make_hint(source: Layer, target: Layer) -> str:
    if source in (Layer.DOMAIN_MODEL, Layer.DOMAIN_USECASE):
        return (
            f"Define a port interface in {source} and inject the adapter. "
            f"Do not import directly from {target}."
        )
    return (
        f"{source} must not import from {target}. "
        "Pass dependencies via constructor injection instead."
    )


# ---------------------------------------------------------------------------
# Validator
# ---------------------------------------------------------------------------


class StructureValidator:
    """Walks ``src/`` and reports Clean Architecture import violations."""

    def validate(self, project_root: Path) -> ValidationReport:
        """Scan all ``.py`` files under ``src/`` and return a ``ValidationReport``.

        Args:
            project_root: Root of the scaffolded project (contains ``pyproject.toml``).

        Returns:
            A :class:`~scaffold_ca_python.models.violation.ValidationReport`.

        Raises:
            ScaffoldError: If ``src/`` does not exist under *project_root*.
        """
        src = project_root / "src"
        if not src.exists():
            raise ScaffoldError("Could not locate src/ under project root.")

        py_files = sorted(src.rglob("*.py"))
        violations: list[Violation] = []
        files_scanned = 0

        for py_file in py_files:
            # Determine source layer from the file path: skip files outside known layers.
            try:
                rel = py_file.relative_to(src)
            except ValueError:
                continue

            parts = rel.parts
            # parts[0] = python_package, parts[1:] = layer path
            if len(parts) < 2:
                continue

            python_package = parts[0]
            source_layer = _layer_from_path_parts(parts[1:])
            if source_layer is None:
                continue  # file outside any registered layer directory

            files_scanned += 1
            forbidden = FORBIDDEN_IMPORTS.get(source_layer, [])

            try:
                content = py_file.read_text(encoding="utf-8")
                tree = ast.parse(content, filename=str(py_file))
            except SyntaxError:
                # Non-fatal — warn and continue scanning other files.
                import warnings
                warnings.warn(f"could not parse '{py_file}' — skipping", stacklevel=2)
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    target = _layer_from_module(node.module, python_package)
                    if target is not None and target in forbidden:
                        names = ", ".join(a.name for a in node.names)
                        violations.append(Violation(
                            source_file=py_file,
                            line_number=node.lineno,
                            import_statement=f"from {node.module} import {names}",
                            source_layer=source_layer,
                            target_layer=target,
                            resolution_hint=_make_hint(source_layer, target),
                        ))

                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        target = _layer_from_module(alias.name, python_package)
                        if target is not None and target in forbidden:
                            violations.append(Violation(
                                source_file=py_file,
                                line_number=node.lineno,
                                import_statement=f"import {alias.name}",
                                source_layer=source_layer,
                                target_layer=target,
                                resolution_hint=_make_hint(source_layer, target),
                            ))

        return ValidationReport(
            project_root=project_root,
            files_scanned=files_scanned,
            violations=violations,
        )
