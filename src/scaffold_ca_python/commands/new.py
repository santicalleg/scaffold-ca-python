"""scaffold new — generate a new Clean Architecture project."""
from __future__ import annotations

import importlib.metadata
import sys
from pathlib import Path

import typer

from scaffold_ca_python.cli import app
from scaffold_ca_python.commands._output import info, verbose, error
from scaffold_ca_python.core.naming import validate_name, extract_package_root
from scaffold_ca_python.core.project import ProjectMarker
from scaffold_ca_python.core.renderer import TemplateRenderer


@app.command("new")
def new(
    name: str = typer.Option(..., "--name", "-n", help="Project name."),
    package: str = typer.Option("", "--package", "-p", help="Base package (dot-separated). Last segment used as top-level Python package dir. Defaults to project name."),
    async_mode: bool = typer.Option(False, "--async", help="Generate async-mode stubs."),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing project directory."),
) -> None:
    """Generate a new Clean Architecture Python project."""
    # --- Validate & normalise name ---
    try:
        snake_name, was_normalised = validate_name(name)
    except ValueError as exc:
        error(str(exc))
        sys.exit(1)
    if was_normalised:
        info(f"Project name normalised: '{name}' → '{snake_name}'")

    # --- Determine package root ---
    if package:
        try:
            pkg_root = extract_package_root(package)
        except ValueError as exc:
            error(str(exc))
            sys.exit(1)
        verbose(f"Package '{package}' → using '{pkg_root}' as top-level package dir")
    else:
        pkg_root = snake_name

    # --- Check target directory ---
    target = Path.cwd() / snake_name
    if target.exists() and not force:
        error(
            f"Directory '{target}' already exists. "
            "Use --force to overwrite."
        )
        sys.exit(1)

    # --- Determine tool version ---
    try:
        tool_version = importlib.metadata.version("scaffold-ca-python")
    except importlib.metadata.PackageNotFoundError:
        tool_version = "dev"

    mode = "async" if async_mode else "sync"
    context = {
        "project_name": snake_name,
        "package": pkg_root,
        "mode": mode,
        "tool_version": tool_version,
    }

    renderer = TemplateRenderer()

    # --- Render project skeleton ---
    # Map of (template_path, destination_relative_to_target)
    templates: list[tuple[str, str]] = [
        # Package root __init__.py
        ("project/__init__.py.j2", f"{pkg_root}/__init__.py"),
        # Domain layers
        ("project/domain/model/__init__.py.j2", f"{pkg_root}/domain/model/__init__.py"),
        ("project/domain/model/gateways/__init__.py.j2", f"{pkg_root}/domain/model/gateways/__init__.py"),
        ("project/domain/usecase/__init__.py.j2", f"{pkg_root}/domain/usecase/__init__.py"),
        # Infrastructure layers
        ("project/infrastructure/driven_adapters/__init__.py.j2", f"{pkg_root}/infrastructure/driven_adapters/__init__.py"),
        ("project/infrastructure/entry_points/__init__.py.j2", f"{pkg_root}/infrastructure/entry_points/__init__.py"),
        ("project/infrastructure/helpers/__init__.py.j2", f"{pkg_root}/infrastructure/helpers/__init__.py"),
        # App layer
        ("project/app/__init__.py.j2", f"{pkg_root}/app/__init__.py"),
        ("project/app/main.py.j2", f"{pkg_root}/app/main.py"),
        # Deployment
        ("project/deployment/Dockerfile.j2", "deployment/Dockerfile"),
        ("project/deployment/github_actions.yml.j2", "deployment/github_actions.yml"),
        # Project root files
        ("project/pyproject.toml.j2", "pyproject.toml"),
        ("project/README.md.j2", "README.md"),
        # Tests
        ("project/tests/__init__.py.j2", "tests/__init__.py"),
        ("project/tests/test_smoke.py.j2", "tests/test_smoke.py"),
        ("project/tests/test_architecture.py.j2", "tests/test_architecture.py"),
    ]

    info(f"Generating project '{snake_name}' (package: {pkg_root}, mode: {mode}) …")

    for tmpl_path, dest_rel in templates:
        dest = target / dest_rel
        try:
            renderer.render_to_file(tmpl_path, dest, context, force=force)
            verbose(f"  created {dest_rel}")
        except FileExistsError as exc:
            error(str(exc))
            sys.exit(1)

    # --- Write .scaffold-ca.json ---
    marker = ProjectMarker(
        name=snake_name,
        base_package=pkg_root,
        mode=mode,
        tool_version=tool_version,
        components=[],
    )
    marker.save(target)
    verbose("  created .scaffold-ca.json")

    info(f"✓ Project '{snake_name}' created at {target}")
    info("  Next steps:")
    info(f"    cd {snake_name}")
    info("    pip install -e '.[dev]'")
    info("    pytest")
