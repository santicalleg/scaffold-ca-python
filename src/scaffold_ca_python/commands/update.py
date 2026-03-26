"""scaffold update — refresh boilerplate structural files."""
from __future__ import annotations

import hashlib
import importlib.metadata
import shutil
import subprocess
import sys
from pathlib import Path

import typer

from scaffold_ca_python.cli import app
from scaffold_ca_python.commands._output import info, verbose, error
from scaffold_ca_python.core.project import find_project_root, ProjectMarker, NoProjectError
from scaffold_ca_python.core.renderer import TemplateRenderer

# Boilerplate files safe to re-render (template_path, dest_relative_to_project_root)
# These are structural files that do not contain user logic.
_BOILERPLATE: list[tuple[str, str]] = [
    ("project/deployment/Dockerfile.j2", "deployment/Dockerfile"),
    ("project/deployment/github_actions.yml.j2", "deployment/github_actions.yml"),
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@app.command("update")
def update(
    skip_git_check: bool = typer.Option(
        False, "--skip-git-check", help="Skip git staging check."
    ),
) -> None:
    """Refresh boilerplate structural files without overwriting user code."""
    try:
        root = find_project_root()
    except NoProjectError as exc:
        error(str(exc))
        sys.exit(1)

    marker = ProjectMarker.load(root)

    # --- Git check ---
    if not skip_git_check:
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
            )
            if result.stdout.strip():
                info(
                    "Warning: You have unstaged changes. "
                    "It is recommended to commit your work before running 'scaffold update'. "
                    "Use --skip-git-check to suppress this warning."
                )
        except (FileNotFoundError, subprocess.TimeoutExpired):
            verbose("git not available — skipping git status check")

    # --- Determine tool version ---
    try:
        tool_version = importlib.metadata.version("scaffold-ca-python")
    except importlib.metadata.PackageNotFoundError:
        tool_version = "dev"

    context = {
        "project_name": marker.name,
        "package": marker.base_package,
        "mode": marker.mode,
        "tool_version": tool_version,
    }

    renderer = TemplateRenderer()
    updated: list[str] = []
    backed_up: list[str] = []

    for tmpl_path, dest_rel in _BOILERPLATE:
        dest = root / dest_rel
        if not dest.exists():
            # File doesn't exist yet — just render it
            renderer.render_to_file(tmpl_path, dest, context, force=True)
            verbose(f"  created {dest_rel}")
            updated.append(dest_rel)
            continue

        # Compare SHA-256 of current file vs freshly rendered content
        rendered_content = renderer.render_string(tmpl_path, context)
        current_hash = _sha256(dest)
        rendered_hash = hashlib.sha256(rendered_content.encode("utf-8")).hexdigest()

        if current_hash == rendered_hash:
            verbose(f"  unchanged {dest_rel}")
            continue

        # File was modified — back it up before overwriting
        bak_path = dest.with_suffix(dest.suffix + ".bak")
        shutil.copy2(dest, bak_path)
        verbose(f"  backed up {dest_rel} → {bak_path.name}")
        backed_up.append(str(bak_path.relative_to(root)))

        dest.write_text(rendered_content, encoding="utf-8")
        verbose(f"  updated {dest_rel}")
        updated.append(dest_rel)

    # Update tool_version in marker
    marker.tool_version = tool_version
    marker.save(root)

    if updated:
        info(f"✓ Updated {len(updated)} boilerplate file(s):")
        for f in updated:
            info(f"    {f}")
        if backed_up:
            info("  Backups created:")
            for b in backed_up:
                info(f"    {b} (manually merge your customisations if needed)")
    else:
        info("✓ All boilerplate files are already up to date.")
