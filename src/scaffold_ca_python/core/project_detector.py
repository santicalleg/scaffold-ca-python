"""project_detector: locate the Clean Architecture project root (T022)."""

from __future__ import annotations

import tomllib
from collections.abc import Iterator
from pathlib import Path

from scaffold_ca_python.core.name_utils import ScaffoldError

_CA_MARKERS: frozenset[str] = frozenset({"domain", "infrastructure", "application"})
_SCAFFOLD_SECTION = "scaffold-ca-python"


def find_project_root(cwd: Path | None = None) -> Path:
    """Walk upward from *cwd* to locate the project root.

    Strategy (R-10):
    1. Look for a ``pyproject.toml`` that contains ``[tool.scaffold-ca-python]``.
    2. If not found, fall back to a directory whose children include the three
       canonical CA layout directories (``domain/``, ``infrastructure/``,
       ``application/``).

    Raises
    ------
    ScaffoldError
        When neither strategy finds a suitable root before reaching the
        filesystem boundary.
    """
    current = (cwd or Path.cwd()).resolve()

    # --- Strategy 1: pyproject.toml with [tool.scaffold-ca-python] ----------
    candidate: Path | None = None
    for directory in _iter_parents(current):
        pyproject = directory / "pyproject.toml"
        if pyproject.is_file():
            try:
                with pyproject.open("rb") as fh:
                    data = tomllib.load(fh)
                if _SCAFFOLD_SECTION in data.get("tool", {}):
                    candidate = directory
                    break
            except Exception:  # malformed TOML — skip silently
                pass

    if candidate is not None:
        return candidate

    # --- Strategy 2: canonical CA directory layout --------------------------
    for directory in _iter_parents(current):
        children = {p.name for p in directory.iterdir() if p.is_dir()}
        if _CA_MARKERS.issubset(children):
            return directory

    raise ScaffoldError(
        "Could not find a scaffold-ca-python project root. "
        "Ensure you are inside a project directory or run 'scaffold generate-project' first. "
        "Hint: a valid project root has either [tool.scaffold-ca-python] in pyproject.toml "
        "or the canonical CA directory layout (domain/, infrastructure/, application/)."
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _iter_parents(start: Path) -> Iterator[Path]:
    """Yield *start* and each parent up to (and including) the filesystem root."""
    current = start
    while True:
        yield current
        parent = current.parent
        if parent == current:
            break
        current = parent
