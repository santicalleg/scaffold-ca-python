"""Tests for EntryPointGeneric factory (T020)."""

from __future__ import annotations

from pathlib import Path

from scaffold_ca_python.core.module_builder import ModuleBuilder
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer


def _project_ctx() -> ProjectContext:
    return ProjectContext(name="ms-demo")


def _module_ctx(project: ProjectContext, subtype: str = "generic") -> ModuleContext:
    return ModuleContext(name="generic", layer=Layer.ENTRY_POINTS, project=project, subtype=subtype)


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


def test_generic_files_queued_in_dry_run(tmp_path: Path) -> None:
    """T020: Verify EntryPointGeneric.build() queues expected files."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=True)

    from scaffold_ca_python.factory.entry_points.ep_generic import EntryPointGeneric

    factory = EntryPointGeneric()
    factory.build(builder)

    preview = builder.persist()

    # Verify all generic files are queued:
    # - src: __init__.py, entry_point.py (from handler.py template)
    # - tests: test_entry_point.py (from test_handler.py template)

    src_dir = tmp_path / "src" / "ms_demo" / "infrastructure" / "entry_points" / "generic"
    test_dir = tmp_path / "src" / "tests" / "infrastructure" / "entry_points" / "generic"

    expected_files = [
        src_dir / "__init__.py",
        src_dir / "entry_point.py",
        test_dir / "test_entry_point.py",
    ]

    for expected in expected_files:
        assert expected in preview, f"Expected {expected.relative_to(tmp_path)} in preview"


def test_generic_no_dependencies_injected(tmp_path: Path) -> None:
    """T020: Verify EntryPointGeneric does not add dependencies."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=False)

    from scaffold_ca_python.factory.entry_points.ep_generic import EntryPointGeneric

    factory = EntryPointGeneric()
    factory.build(builder)

    _ = builder.persist()
    pyproject = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")

    # Should only have the original dependencies list unchanged
    assert "dependencies = []" in pyproject, "Expected no new dependencies"


def test_generic_main_py_overwritten(tmp_path: Path) -> None:
    """T020: Verify EntryPointGeneric overwrites main.py."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=True)

    # Create main.py to simulate existing state
    main_py = tmp_path / "src" / "ms_demo" / "main.py"
    main_py.parent.mkdir(parents=True, exist_ok=True)
    main_py.write_text("# placeholder\n", encoding="utf-8")

    from scaffold_ca_python.factory.entry_points.ep_generic import EntryPointGeneric

    factory = EntryPointGeneric()
    factory.build(builder)

    preview = builder.persist()

    # Verify main.py overwrite is in preview
    assert main_py in preview, f"Expected {main_py.relative_to(tmp_path)} in preview"
