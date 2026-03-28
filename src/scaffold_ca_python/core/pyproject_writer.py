"""pyproject_writer: inject dependencies into [project.dependencies] in pyproject.toml."""

from __future__ import annotations

import tomllib
from pathlib import Path

import tomli_w


def _name_prefix(package: str) -> str:
    """Extract the bare package name, stripping version specifier and extras.

    Examples::

        "fastapi>=0.100"        -> "fastapi"
        "uvicorn[standard]>=0.20" -> "uvicorn"
        "a2a-sdk>=0.1"          -> "a2a-sdk"
    """
    name = package.split(">=")[0].split("==")[0].split("<")[0].split("!=")[0]
    name = name.split("[")[0]
    return name.strip().lower()


def _missing(existing: list[str], packages: list[str]) -> list[str]:
    """Return packages not already present in *existing* (by name prefix)."""
    existing_names = {_name_prefix(d) for d in existing}
    return [p for p in packages if _name_prefix(p) not in existing_names]


def inject_dependencies(project_root: Path, packages: list[str]) -> list[str]:
    """Add *packages* to ``[project.dependencies]`` in ``pyproject.toml``.

    Idempotent: a package whose bare name is already present is skipped.
    Does not reformat unrelated sections.

    Parameters
    ----------
    project_root:
        Directory containing ``pyproject.toml``.
    packages:
        Packages to inject, e.g. ``["fastapi>=0.100", "uvicorn[standard]>=0.20"]``.

    Returns
    -------
    list[str]
        The packages that were actually added (empty when all were already present).

    Raises
    ------
    FileNotFoundError
        If ``pyproject.toml`` does not exist in *project_root*.
    tomllib.TOMLDecodeError
        If ``pyproject.toml`` is malformed.
    """
    pyproject = project_root / "pyproject.toml"
    with pyproject.open("rb") as fh:
        data = tomllib.load(fh)

    deps: list[str] = data.setdefault("project", {}).setdefault("dependencies", [])
    to_add = _missing(deps, packages)
    if not to_add:
        return []

    deps.extend(to_add)

    with pyproject.open("wb") as fh:
        tomli_w.dump(data, fh)

    return to_add


def dry_run_inject(project_root: Path, packages: list[str]) -> list[str]:
    """Return packages that *would* be added without writing to disk.

    Parameters
    ----------
    project_root:
        Directory containing ``pyproject.toml``.
    packages:
        Packages to check.

    Returns
    -------
    list[str]
        The packages that would be added if :func:`inject_dependencies` were called.

    Raises
    ------
    FileNotFoundError
        If ``pyproject.toml`` does not exist in *project_root*.
    tomllib.TOMLDecodeError
        If ``pyproject.toml`` is malformed.
    """
    pyproject = project_root / "pyproject.toml"
    with pyproject.open("rb") as fh:
        data = tomllib.load(fh)

    deps: list[str] = data.get("project", {}).get("dependencies", [])
    return _missing(deps, packages)
