"""pyproject_writer: inject dependencies into [project.dependencies] in pyproject.toml."""

from __future__ import annotations

import tomllib
from pathlib import Path

import tomli_w

from scaffold_ca_python.models.context import ProjectContext


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


def update_project_scripts(project_root: Path, pkg: ProjectContext, entry_fn: str = "start_server") -> bool:
    """Rewrite ``[project.scripts]`` so the CLI entry calls *entry_fn*.

    Sets ``<pkg> = "<pkg>.server:<entry_fn>"`` in ``pyproject.toml``.
    Idempotent: returns ``False`` immediately when the entry already has the
    correct value, leaving the file unchanged.

    Parameters
    ----------
    project_root:
        Directory containing ``pyproject.toml``.
    pkg:
        The Python package name (e.g. ``"my_app"``).
    entry_fn:
        The function name in ``server.py`` to use as the entry point
        (default ``"start_server"``).  Pass ``"main"`` for MCP projects.

    Returns
    -------
    bool
        ``True`` if the file was written, ``False`` if it was already correct.
    """
    pyproject = project_root / "pyproject.toml"
    with pyproject.open("rb") as fh:
        data = tomllib.load(fh)

    new_value = f"{pkg.python_package}.server:{entry_fn}"
    scripts: dict[str, str] = data.setdefault("project", {}).setdefault("scripts", {})
    if scripts.get(pkg.python_package_script) == new_value:
        return False

    scripts[pkg.python_package_script] = new_value
    with pyproject.open("wb") as fh:
        tomli_w.dump(data, fh)
    return True


def dry_run_scripts_update(project_root: Path, pkg: ProjectContext, entry_fn: str = "start_server") -> bool:
    """Return whether ``update_project_scripts`` *would* write to disk.

    Read-only: never modifies ``pyproject.toml``.

    Parameters
    ----------
    project_root:
        Directory containing ``pyproject.toml``.
    pkg:
        The Python package name (e.g. ``"my_app"``).
    entry_fn:
        The function name in ``server.py`` to use as the entry point
        (default ``"start_server"``).  Pass ``"main"`` for MCP projects.

    Returns
    -------
    bool
        ``True`` if the current entry differs from ``<pkg>.server:<entry_fn>``,
        ``False`` if no change would be needed.
    """
    pyproject = project_root / "pyproject.toml"
    with pyproject.open("rb") as fh:
        data = tomllib.load(fh)

    new_value = f"{pkg.python_package}.server:{entry_fn}"
    scripts: dict[str, str] = data.get("project", {}).get("scripts", {})
    return scripts.get(pkg.python_package_script) != new_value
