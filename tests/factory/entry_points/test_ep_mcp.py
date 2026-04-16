"""Tests for EntryPointMcp factory (T018)."""

from __future__ import annotations

from pathlib import Path

from scaffold_ca_python.core.module_builder import ModuleBuilder
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer


def _project_ctx() -> ProjectContext:
    return ProjectContext(name="ms-demo")


def _module_ctx(project: ProjectContext, subtype: str = "mcp") -> ModuleContext:
    return ModuleContext(name="mcp_server", layer=Layer.ENTRY_POINTS, project=project, subtype=subtype)


def _write_minimal_pyproject(root: Path) -> None:
    (root / "pyproject.toml").write_text(
        """
[project]
name = "demo"
version = "0.1.0"
dependencies = []
""".strip()
        + "\n",
        encoding="utf-8",
    )


def test_mcp_files_queued_in_dry_run(tmp_path: Path) -> None:
    """T018: Verify EntryPointMcp.build() queues expected files."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=True)

    from scaffold_ca_python.factory.entry_points.ep_mcp import EntryPointMcp

    factory = EntryPointMcp()
    factory.build(builder)

    preview = builder.persist()

    # Verify all mcp files are queued:
    # - src: __init__.py, server.py
    # - tests: test_server.py

    src_dir = tmp_path / "src" / "ms_demo" / "infrastructure" / "entry_points" / "mcp_server"
    test_dir = tmp_path / "src" / "tests" / "infrastructure" / "entry_points" / "mcp_server"

    expected_files = [
        src_dir / "__init__.py",
        src_dir / "server.py",
        test_dir / "test_server.py",
    ]

    for expected in expected_files:
        assert expected in preview, f"Expected {expected.relative_to(tmp_path)} in preview"


def test_mcp_dependencies_injected(tmp_path: Path) -> None:
    """T018: Verify EntryPointMcp adds mcp dependency."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=False)

    from scaffold_ca_python.factory.entry_points.ep_mcp import EntryPointMcp

    factory = EntryPointMcp()
    factory.build(builder)

    _ = builder.persist()
    pyproject = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")

    # Verify mcp dep is present
    assert "mcp>=1.0" in pyproject, "Expected mcp>=1.0 in pyproject.toml"


def test_mcp_main_py_overwritten(tmp_path: Path) -> None:
    """T018: Verify EntryPointMcp overwrites main.py."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=True)

    # Create main.py to simulate existing state
    main_py = tmp_path / "src" / "ms_demo" / "main.py"
    main_py.parent.mkdir(parents=True, exist_ok=True)
    main_py.write_text("# placeholder\n", encoding="utf-8")

    from scaffold_ca_python.factory.entry_points.ep_mcp import EntryPointMcp

    factory = EntryPointMcp()
    factory.build(builder)

    preview = builder.persist()

    # Verify main.py overwrite is in preview
    assert main_py in preview, f"Expected {main_py.relative_to(tmp_path)} in preview"
