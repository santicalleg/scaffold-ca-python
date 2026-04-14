"""Tests for DrivenAdapterSecrets factory (T026)."""

from __future__ import annotations

from pathlib import Path

from scaffold_ca_python.core.module_builder import ModuleBuilder
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer


def _project_ctx() -> ProjectContext:
    return ProjectContext(name="MsDemo")


def _module_ctx(project: ProjectContext) -> ModuleContext:
    return ModuleContext(name="Secrets", layer=Layer.DRIVEN_ADAPTERS, project=project)


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


def test_secrets_files_queued_in_dry_run(tmp_path: Path) -> None:
    """T026: Verify DrivenAdapterSecrets.build() queues expected files."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=True)

    from scaffold_ca_python.factory.driven_adapters.da_secrets import DrivenAdapterSecrets

    factory = DrivenAdapterSecrets()
    factory.build(builder)

    preview = builder.persist()

    # Verify all secrets files are queued:
    # - src: __init__.py, secrets_adapter.py
    # - tests: test_secrets_adapter.py

    src_dir = tmp_path / "src" / "ms_demo" / "infrastructure" / "driven_adapters" / "secrets"
    test_dir = tmp_path / "src" / "tests" / "infrastructure" / "driven_adapters" / "secrets"

    expected_files = [
        src_dir / "__init__.py",
        src_dir / "secrets_adapter.py",
        test_dir / "test_secrets_adapter.py",
    ]

    for expected in expected_files:
        assert expected in preview, f"Expected {expected.relative_to(tmp_path)} in preview"


def test_secrets_dependencies_injected(tmp_path: Path) -> None:
    """T026: Verify DrivenAdapterSecrets adds boto3 dependency."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=False)

    from scaffold_ca_python.factory.driven_adapters.da_secrets import DrivenAdapterSecrets

    factory = DrivenAdapterSecrets()
    factory.build(builder)

    _ = builder.persist()
    pyproject = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")

    # Verify boto3 dep is present
    assert "boto3>=1.34" in pyproject, "Expected boto3>=1.34 in pyproject.toml"
