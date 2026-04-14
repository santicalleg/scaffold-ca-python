"""Tests for EntryPointRestApi factory (T014)."""

from __future__ import annotations

from pathlib import Path

from scaffold_ca_python.core.module_builder import ModuleBuilder
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer


def _project_ctx() -> ProjectContext:
    return ProjectContext(name="MsDemo")


def _module_ctx(project: ProjectContext, subtype: str = "restapi") -> ModuleContext:
    return ModuleContext(name="api_v1", layer=Layer.ENTRY_POINTS, project=project, subtype=subtype)


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


def test_restapi_files_queued_in_dry_run(tmp_path: Path) -> None:
    """T014: Verify EntryPointRestApi.build() queues expected files."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=True)

    from scaffold_ca_python.factory.entry_points.ep_restapi import EntryPointRestApi

    factory = EntryPointRestApi()
    factory.build(builder)

    preview = builder.persist()

    # Verify all restapi files are queued:
    # - src: app.py, __init__.py, rest_controller.py, exception_handler.py, server.py
    # - tests: test_rest_controller.py, test_server.py, test_exception_handler.py, test_app.py

    src_dir = tmp_path / "src" / "ms_demo" / "infrastructure" / "entry_points" / "api" / "v1"
    app_py = tmp_path / "src" / "ms_demo" / "application" / "app.py"
    server_py = tmp_path / "src" / "ms_demo" / "server.py"

    # resolve_tests_root defaults to src/tests when tests/ doesn't exist
    test_dir = tmp_path / "src" / "tests" / "infrastructure" / "entry_points" / "api" / "v1"
    test_app_py = tmp_path / "src" / "tests" / "application" / "test_app.py"

    expected_files = [
        app_py,
        src_dir / "__init__.py",
        src_dir / "rest_controller.py",
        src_dir / "exception_handler.py",
        server_py,
        test_dir / "test_rest_controller.py",
        test_dir / "test_server.py",
        test_dir / "test_exception_handler.py",
        test_app_py,
    ]

    for expected in expected_files:
        assert expected in preview, f"Expected {expected.relative_to(tmp_path)} in preview"


def test_restapi_dependencies_injected(tmp_path: Path) -> None:
    """T014: Verify EntryPointRestApi adds fastapi dependencies."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=False)

    from scaffold_ca_python.factory.entry_points.ep_restapi import EntryPointRestApi

    factory = EntryPointRestApi()
    factory.build(builder)

    _ = builder.persist()
    pyproject = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")

    # Verify fastapi deps are present
    expected_deps = [
        "fastapi[standard]>=0.135.2",
        "uvicorn[standard]>=0.20",
        "dependency-injector>=4.49.0",
        "pydantic-settings>=2.13.1",
    ]
    for dep in expected_deps:
        assert dep in pyproject, f"Expected {dep} in pyproject.toml"


def test_restapi_main_py_deleted(tmp_path: Path) -> None:
    """T014: Verify EntryPointRestApi deletes main.py."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=True)

    # Create main.py to simulate existing state
    main_py = tmp_path / "src" / "ms_demo" / "main.py"
    main_py.parent.mkdir(parents=True, exist_ok=True)
    main_py.write_text("# placeholder\n", encoding="utf-8")

    from scaffold_ca_python.factory.entry_points.ep_restapi import EntryPointRestApi

    factory = EntryPointRestApi()
    factory.build(builder)

    preview = builder.persist()

    # Verify main.py deletion is in preview
    assert main_py in preview, f"Expected {main_py.relative_to(tmp_path)} deletion in preview"


def test_restapi_scripts_param_set(tmp_path: Path) -> None:
    """T014: Verify EntryPointRestApi sets scripts param."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=True)

    from scaffold_ca_python.factory.entry_points.ep_restapi import EntryPointRestApi

    factory = EntryPointRestApi()
    factory.build(builder)

    _ = builder.persist()

    # Verify scripts param is set
    scripts_param = builder.get_param("scripts_entry")
    assert scripts_param is True, "Expected scripts_entry param to be True"
