"""Tests for EntryPointAgent factory (T016)."""

from __future__ import annotations

from pathlib import Path

from scaffold_ca_python.core.module_builder import ModuleBuilder
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer


def _project_ctx() -> ProjectContext:
    return ProjectContext(name="ms-demo")


def _module_ctx(project: ProjectContext, subtype: str = "agent") -> ModuleContext:
    return ModuleContext(name="agent", layer=Layer.ENTRY_POINTS, project=project, subtype=subtype)


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


def test_agent_files_queued_in_dry_run(tmp_path: Path) -> None:
    """T016: Verify EntryPointAgent.build() queues expected files."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=True)

    from scaffold_ca_python.factory.entry_points.ep_agent import EntryPointAgent

    factory = EntryPointAgent()
    factory.build(builder)

    preview = builder.persist()

    # Verify all agent files are queued:
    # - src: __init__.py, agent.py, card.py
    # - tests: test_agent.py

    src_dir = tmp_path / "src" / "ms_demo" / "infrastructure" / "entry_points" / "agent"
    test_dir = tmp_path / "src" / "tests" / "infrastructure" / "entry_points" / "agent"

    expected_files = [
        src_dir / "__init__.py",
        src_dir / "agent.py",
        src_dir / "card.py",
        test_dir / "test_agent.py",
    ]

    for expected in expected_files:
        assert expected in preview, f"Expected {expected.relative_to(tmp_path)} in preview"


def test_agent_dependencies_injected(tmp_path: Path) -> None:
    """T016: Verify EntryPointAgent adds a2a-sdk dependency."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=False)

    from scaffold_ca_python.factory.entry_points.ep_agent import EntryPointAgent

    factory = EntryPointAgent()
    factory.build(builder)

    _ = builder.persist()
    pyproject = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")

    # Verify a2a-sdk dep is present
    assert "a2a-sdk>=0.1" in pyproject, "Expected a2a-sdk>=0.1 in pyproject.toml"


def test_agent_main_py_overwritten(tmp_path: Path) -> None:
    """T016: Verify EntryPointAgent marks main.py for overwrite."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=True)

    # Create main.py to simulate existing state
    main_py = tmp_path / "src" / "ms_demo" / "main.py"
    main_py.parent.mkdir(parents=True, exist_ok=True)
    main_py.write_text("# placeholder\n", encoding="utf-8")

    from scaffold_ca_python.factory.entry_points.ep_agent import EntryPointAgent

    factory = EntryPointAgent()
    factory.build(builder)

    preview = builder.persist()

    # Verify main.py overwrite is in preview
    assert main_py in preview, f"Expected {main_py.relative_to(tmp_path)} in preview"


def test_agent_kafka_flag_handling(tmp_path: Path) -> None:
    """T016: Verify EntryPointAgent handles kafka flag in params."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=True)
    builder.add_param("enable_kafka", True)

    from scaffold_ca_python.factory.entry_points.ep_agent import EntryPointAgent

    factory = EntryPointAgent()
    factory.build(builder)

    _ = builder.persist()

    # Verify flag was preserved (it should be available for template rendering)
    assert builder.get_param("enable_kafka") is True
