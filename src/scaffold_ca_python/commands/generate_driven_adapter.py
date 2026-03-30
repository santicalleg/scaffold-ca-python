"""generate_driven_adapter: scaffold a driven adapter and test stub (T048)."""

from __future__ import annotations

import importlib.resources
import tomllib
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.tree import Tree

from scaffold_ca_python.core.file_writer import FileWriter
from scaffold_ca_python.core.name_utils import ScaffoldError, to_snake_case, validate_name
from scaffold_ca_python.core.project_detector import find_project_root
from scaffold_ca_python.core.pyproject_writer import dry_run_inject, inject_dependencies
from scaffold_ca_python.core.template_renderer import TemplateRenderer
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.file_operation import CreateFile, FileOperation, GeneratedFile
from scaffold_ca_python.models.layer import Layer

console = Console()
renderer = TemplateRenderer()
writer = FileWriter()

_ALLOWED_TYPES = ("rest-consumer", "secrets", "generic")

_DEP_MAP: dict[str, list[str]] = {
    "rest-consumer": ["httpx>=0.27"],
    "secrets": ["boto3>=1.34"],
    "generic": [],
}


def _generate_driven_adapter_impl(type_: str, name: str | None, dry_run: bool) -> None:  # noqa: ANN001
    # --- Validate type ---
    if type_ not in _ALLOWED_TYPES:
        console.print(
            f"[red]Error:[/red] Unknown type '{type_}'. "
            f"Allowed: {', '.join(_ALLOWED_TYPES)}."
        )
        raise typer.Exit(code=1) from None

    # --- Validate name requirement for generic ---
    if type_ == "generic" and not name:
        console.print(
            "[red]Error:[/red] --name is required when --type is generic."
        )
        raise typer.Exit(code=1) from None

    # --- Validate name if provided ---
    if name:
        try:
            validate_name(name)
        except ScaffoldError as exc:
            console.print(f"[red]Error:[/red] {exc}")
            raise typer.Exit(code=1) from None

    # --- Locate project root ---
    try:
        project_root = find_project_root()
    except ScaffoldError:
        console.print(
            "[red]Error:[/red] No scaffold-ca-python project found. Run 'scaffold ca' first."
        )
        raise typer.Exit(code=1) from None

    project_ctx = _load_project_context(project_root)

    # --- Determine subdir name and module context ---
    if type_ == "rest-consumer":
        subdir = "rest_consumer"
        module_ctx = ModuleContext(name="RestConsumer", layer=Layer.DRIVEN_ADAPTERS, project=project_ctx)
    elif type_ == "secrets":
        subdir = "secrets"
        module_ctx = ModuleContext(name="Secrets", layer=Layer.DRIVEN_ADAPTERS, project=project_ctx)
    else:  # generic
        assert name is not None  # validated above
        subdir = to_snake_case(name)
        module_ctx = ModuleContext(name=name, layer=Layer.DRIVEN_ADAPTERS, project=project_ctx)

    pkg = project_ctx.python_package
    src_dir = project_root / "src" / pkg / "infrastructure" / "driven_adapters" / subdir
    test_dir = project_root / "tests" / "infrastructure" / "driven_adapters" / subdir

    # --- Duplicate guard ---
    if src_dir.exists():
        console.print(
            f"[red]Error:[/red] Directory '{src_dir.relative_to(project_root)}/' already exists.\n"
            "[dim]Hint:[/dim] Choose a different name or remove the existing directory first."
        )
        raise typer.Exit(code=1) from None

    ctx_dict = module_ctx.model_dump()
    operations = _build_operations(type_, subdir, src_dir, test_dir, ctx_dict)

    deps = _DEP_MAP.get(type_, [])

    if dry_run:
        preview = writer.execute(operations, dry_run=True)
        tree = Tree(f"[bold]{subdir}[/bold] (dry run)")
        for p in sorted(preview):
            tree.add(str(p.relative_to(project_root)))
        console.print(tree)
        if deps:
            would_add = dry_run_inject(project_root, deps)
            if would_add:
                console.print(
                    f"[dim]Would add to [project.dependencies]: {', '.join(would_add)}[/dim]"
                )
        return

    created = writer.execute(operations, dry_run=False)
    console.print(
        f"[green]✓[/green] Driven adapter [bold]{subdir}[/bold] created. "
        f"Created {len(created)} file(s)."
    )

    # --- Inject dependencies ------------------------------------------------
    if deps:
        added = inject_dependencies(project_root, deps)
        if added:
            console.print(
                f"[green]✓[/green] Added {', '.join(added)} to [project.dependencies]."
            )


def _build_operations(
    type_: str,
    subdir: str,
    src_dir: Path,
    test_dir: Path,
    ctx_dict: dict[str, object],
) -> list[FileOperation]:
    """Return the list of CreateFile operations for the given adapter type."""
    if type_ == "rest-consumer":
        return [
            CreateFile(file=GeneratedFile(
                path=src_dir / "__init__.py",
                content=renderer.render_string(
                    _tmpl("driven_adapter/rest_consumer/__init__.py.jinja2"), ctx_dict
                ),
                template_name="driven_adapter/rest_consumer/__init__.py.jinja2",
            )),
            CreateFile(file=GeneratedFile(
                path=src_dir / "rest_consumer.py",
                content=renderer.render_string(
                    _tmpl("driven_adapter/rest_consumer/rest_consumer.py.jinja2"), ctx_dict
                ),
                template_name="driven_adapter/rest_consumer/rest_consumer.py.jinja2",
            )),
            CreateFile(file=GeneratedFile(
                path=test_dir / "test_rest_consumer.py",
                content=renderer.render_string(
                    _tmpl("driven_adapter/rest_consumer/test_rest_consumer.py.jinja2"), ctx_dict
                ),
                template_name="driven_adapter/rest_consumer/test_rest_consumer.py.jinja2",
                is_test=True,
            )),
        ]
    if type_ == "secrets":
        return [
            CreateFile(file=GeneratedFile(
                path=src_dir / "__init__.py",
                content=renderer.render_string(
                    _tmpl("driven_adapter/secrets/__init__.py.jinja2"), ctx_dict
                ),
                template_name="driven_adapter/secrets/__init__.py.jinja2",
            )),
            CreateFile(file=GeneratedFile(
                path=src_dir / "secrets_adapter.py",
                content=renderer.render_string(
                    _tmpl("driven_adapter/secrets/secrets_adapter.py.jinja2"), ctx_dict
                ),
                template_name="driven_adapter/secrets/secrets_adapter.py.jinja2",
            )),
            CreateFile(file=GeneratedFile(
                path=test_dir / "test_secrets_adapter.py",
                content=renderer.render_string(
                    _tmpl("driven_adapter/secrets/test_secrets_adapter.py.jinja2"), ctx_dict
                ),
                template_name="driven_adapter/secrets/test_secrets_adapter.py.jinja2",
                is_test=True,
            )),
        ]
    # generic
    return [
        CreateFile(file=GeneratedFile(
            path=src_dir / "__init__.py",
            content=renderer.render_string(
                _tmpl("driven_adapter/generic/__init__.py.jinja2"), ctx_dict
            ),
            template_name="driven_adapter/generic/__init__.py.jinja2",
        )),
        CreateFile(file=GeneratedFile(
            path=src_dir / f"{subdir}_adapter.py",
            content=renderer.render_string(
                _tmpl("driven_adapter/generic/adapter.py.jinja2"), ctx_dict
            ),
            template_name="driven_adapter/generic/adapter.py.jinja2",
        )),
        CreateFile(file=GeneratedFile(
            path=test_dir / f"test_{subdir}_adapter.py",
            content=renderer.render_string(
                _tmpl("driven_adapter/generic/test_adapter.py.jinja2"), ctx_dict
            ),
            template_name="driven_adapter/generic/test_adapter.py.jinja2",
            is_test=True,
        )),
    ]


def register(app: typer.Typer) -> None:
    """Register gda / generate-driven-adapter commands onto *app*."""

    @app.command(
        "generate-driven-adapter",
        help="Scaffold a driven adapter and test stub.",
        epilog="Examples: scaffold gda --type rest-consumer | scaffold gda --type generic --name MyAdapter",
    )
    def generate_driven_adapter(
        type_: Annotated[
            str,
            typer.Option(
                "--type",
                help="Adapter type: rest-consumer, secrets, generic.",
                rich_help_panel="Required",
            ),
        ],
        name: Annotated[
            str | None,
            typer.Option(
                "--name",
                help="Adapter name (required for --type generic).",
                rich_help_panel="Options",
            ),
        ] = None,
        dry_run: Annotated[
            bool,
            typer.Option(
                "--dry-run/--no-dry-run",
                help="Preview without writing.",
                rich_help_panel="Options",
                show_default=True,
            ),
        ] = False,
    ) -> None:
        """Scaffold a driven adapter inside infrastructure/driven_adapters/."""
        _generate_driven_adapter_impl(type_, name, dry_run)

    @app.command("gda", hidden=True, help="Alias for generate-driven-adapter.")
    def gda(
        type_: Annotated[str, typer.Option("--type", help="Adapter type: rest-consumer, secrets, generic.")],
        name: Annotated[str | None, typer.Option("--name", help="Adapter name (required for generic).")] = None,
        dry_run: Annotated[bool, typer.Option("--dry-run/--no-dry-run")] = False,
    ) -> None:
        """Alias for generate-driven-adapter."""
        _generate_driven_adapter_impl(type_, name, dry_run)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _load_project_context(root: Path) -> ProjectContext:
    pyproject = root / "pyproject.toml"
    with pyproject.open("rb") as fh:
        data = tomllib.load(fh)
    section = data.get("tool", {}).get("scaffold-ca-python", {})
    return ProjectContext(
        name=section.get("name", root.name),
    )


def _tmpl(name: str) -> str:
    ref = importlib.resources.files("scaffold_ca_python.templates").joinpath(name)
    return ref.read_text(encoding="utf-8")
