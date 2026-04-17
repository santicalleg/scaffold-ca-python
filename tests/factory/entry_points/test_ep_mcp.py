"""Tests for EntryPointMcp factory (T018 / T008 019-restructure)."""

from __future__ import annotations

from pathlib import Path

import pytest

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


def _make_builder(tmp_path: Path, *, dry_run: bool = True) -> ModuleBuilder:
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    return ModuleBuilder(
        project_root=tmp_path,
        project_ctx=project,
        module_ctx=_module_ctx(project),
        dry_run=dry_run,
    )


def test_mcp_files_queued_in_dry_run(tmp_path: Path) -> None:
    """T008: tools.py present; no server.py inside mcp_server/."""
    builder = _make_builder(tmp_path)

    from scaffold_ca_python.factory.entry_points.ep_mcp import EntryPointMcp

    EntryPointMcp().build(builder)
    preview = builder.persist()

    src_dir = tmp_path / "src" / "ms_demo" / "infrastructure" / "entry_points" / "mcp_server"
    test_dir = tmp_path / "src" / "tests" / "infrastructure" / "entry_points" / "mcp_server"

    assert src_dir / "__init__.py" in preview
    assert src_dir / "tools.py" in preview
    assert test_dir / "test_tools.py" in preview

    # Old monolithic server.py must NOT be generated inside mcp_server/
    assert src_dir / "server.py" not in preview


def test_mcp_with_resources_queues_resources_file(tmp_path: Path) -> None:
    """T008: --with-resources adds resources.py and test_resources.py."""
    builder = _make_builder(tmp_path)
    builder.add_param("with_resources", True)

    from scaffold_ca_python.factory.entry_points.ep_mcp import EntryPointMcp

    EntryPointMcp().build(builder)
    preview = builder.persist()

    src_dir = tmp_path / "src" / "ms_demo" / "infrastructure" / "entry_points" / "mcp_server"
    test_dir = tmp_path / "src" / "tests" / "infrastructure" / "entry_points" / "mcp_server"

    assert src_dir / "resources.py" in preview
    assert test_dir / "test_resources.py" in preview


def test_mcp_without_resources_does_not_queue_resources_file(tmp_path: Path) -> None:
    """T008: without --with-resources no resources.py is generated."""
    builder = _make_builder(tmp_path)

    from scaffold_ca_python.factory.entry_points.ep_mcp import EntryPointMcp

    EntryPointMcp().build(builder)
    preview = builder.persist()

    src_dir = tmp_path / "src" / "ms_demo" / "infrastructure" / "entry_points" / "mcp_server"
    assert src_dir / "resources.py" not in preview


def test_mcp_with_prompts_queues_prompts_file(tmp_path: Path) -> None:
    """T008: --with-prompts adds prompts.py and test_prompts.py."""
    builder = _make_builder(tmp_path)
    builder.add_param("with_prompts", True)

    from scaffold_ca_python.factory.entry_points.ep_mcp import EntryPointMcp

    EntryPointMcp().build(builder)
    preview = builder.persist()

    src_dir = tmp_path / "src" / "ms_demo" / "infrastructure" / "entry_points" / "mcp_server"
    test_dir = tmp_path / "src" / "tests" / "infrastructure" / "entry_points" / "mcp_server"

    assert src_dir / "prompts.py" in preview
    assert test_dir / "test_prompts.py" in preview


def test_mcp_without_prompts_does_not_queue_prompts_file(tmp_path: Path) -> None:
    """T008: without --with-prompts no prompts.py is generated."""
    builder = _make_builder(tmp_path)

    from scaffold_ca_python.factory.entry_points.ep_mcp import EntryPointMcp

    EntryPointMcp().build(builder)
    preview = builder.persist()

    src_dir = tmp_path / "src" / "ms_demo" / "infrastructure" / "entry_points" / "mcp_server"
    assert src_dir / "prompts.py" not in preview


def test_mcp_dependencies_injected(tmp_path: Path) -> None:
    """T008 (H3): all five required deps are present after a live run."""
    builder = _make_builder(tmp_path, dry_run=False)

    # Simulate the config.py that `scaffold ca` would have created first.
    config_py = tmp_path / "src" / "ms_demo" / "application" / "config" / "config.py"
    config_py.parent.mkdir(parents=True, exist_ok=True)
    config_py.write_text(
        '"""Application settings."""\nclass Settings:\n    LOG_LEVEL: str = "INFO"\n',
        encoding="utf-8",
    )

    from scaffold_ca_python.factory.entry_points.ep_mcp import EntryPointMcp

    EntryPointMcp().build(builder)
    builder.persist()

    pyproject = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")
    expected_deps = ["mcp>=1.0", "uvicorn[standard]>=0.20", "starlette>=0.40", "dependency-injector>=4.49.0", "pydantic-settings>=2.13.1"]
    for dep in expected_deps:
        assert dep in pyproject, f"Missing dep: {dep}"


def test_mcp_scripts_entry_fn_param_is_main(tmp_path: Path) -> None:
    """T008: factory must set scripts_entry_fn='main' on builder."""
    builder = _make_builder(tmp_path)

    from scaffold_ca_python.factory.entry_points.ep_mcp import EntryPointMcp

    EntryPointMcp().build(builder)

    assert builder.get_param("scripts_entry_fn") == "main"


def test_mcp_main_py_overwritten(tmp_path: Path) -> None:
    """Phase 4 / T022: server.py at package root replaces main.py.

    This test is intentionally placed here to fail until T024+T025 (Phase 4)
    add server.py generation to ep_mcp.py.  It documents the expected
    Phase 4 behaviour so the red/green boundary is explicit.
    """
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(
        project_root=tmp_path,
        project_ctx=project,
        module_ctx=_module_ctx(project),
        dry_run=True,
    )

    main_py = tmp_path / "src" / "ms_demo" / "main.py"
    main_py.parent.mkdir(parents=True, exist_ok=True)
    main_py.write_text("# placeholder\n", encoding="utf-8")

    from scaffold_ca_python.factory.entry_points.ep_mcp import EntryPointMcp

    EntryPointMcp().build(builder)
    preview = builder.persist()

    # server.py at package root must be queued (implemented in T025 / Phase 4)
    server_py = tmp_path / "src" / "ms_demo" / "server.py"
    assert server_py in preview, f"Expected {server_py.relative_to(tmp_path)} in preview"


# ---------------------------------------------------------------------------
# Phase 5 / T028 — application/app.py composition root
# ---------------------------------------------------------------------------


def test_mcp_queues_app_py(tmp_path: Path) -> None:
    """T028: application/app.py must be in the dry-run preview."""
    builder = _make_builder(tmp_path)

    from scaffold_ca_python.factory.entry_points.ep_mcp import EntryPointMcp

    EntryPointMcp().build(builder)
    preview = builder.persist()

    app_py = tmp_path / "src" / "ms_demo" / "application" / "app.py"
    assert app_py in preview, f"Expected {app_py.relative_to(tmp_path)} in preview"


def test_mcp_app_py_not_overwritten(tmp_path: Path) -> None:
    """T028: existing application/app.py raises FileExistsError (no-overwrite guard)."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()

    # Pre-create config.py (created by `scaffold ca` in real usage).
    config_py = tmp_path / "src" / "ms_demo" / "application" / "config" / "config.py"
    config_py.parent.mkdir(parents=True, exist_ok=True)
    config_py.write_text('class Settings:\n    LOG_LEVEL: str = "INFO"\n', encoding="utf-8")

    # Pre-create app.py with sentinel content
    app_py = tmp_path / "src" / "ms_demo" / "application" / "app.py"
    app_py.parent.mkdir(parents=True, exist_ok=True)
    app_py.write_text("# SENTINEL — do not overwrite\n", encoding="utf-8")

    builder = ModuleBuilder(
        project_root=tmp_path,
        project_ctx=project,
        module_ctx=_module_ctx(project),
        dry_run=False,
    )

    from scaffold_ca_python.factory.entry_points.ep_mcp import EntryPointMcp

    EntryPointMcp().build(builder)
    with pytest.raises(FileExistsError):
        builder.persist()

