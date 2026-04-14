"""Tests for ModelFactory (T032)."""

from __future__ import annotations

from pathlib import Path

from scaffold_ca_python.core.module_builder import ModuleBuilder
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer


def _project_ctx() -> ProjectContext:
    return ProjectContext(name="MsDemo")


def _module_ctx(project: ProjectContext) -> ModuleContext:
    return ModuleContext(name="Order", layer=Layer.DOMAIN_MODEL, project=project)


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


def test_model_files_queued_in_dry_run(tmp_path: Path) -> None:
    """T032: Verify ModelFactory.build() queues expected files."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=True)

    from scaffold_ca_python.factory.simple.model_factory import ModelFactory

    factory = ModelFactory()
    factory.build(builder)

    preview = builder.persist()

    # Verify all model files are queued:
    # - src: order.py
    # - tests: test_order.py

    src_dir = tmp_path / "src" / "ms_demo" / "domain" / "model"
    test_dir = tmp_path / "src" / "tests" / "domain" / "model"

    expected_files = [
        src_dir / "order.py",
        test_dir / "test_order.py",
    ]

    for expected in expected_files:
        assert expected in preview, f"Expected {expected.relative_to(tmp_path)} in preview"


def test_model_no_dependencies_injected(tmp_path: Path) -> None:
    """T032: Verify ModelFactory does not add dependencies."""
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=False)

    from scaffold_ca_python.factory.simple.model_factory import ModelFactory

    factory = ModelFactory()
    factory.build(builder)

    _ = builder.persist()
    pyproject = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")

    # Verify no dependencies added (models use only pydantic which is already a dep)
    # Pyproject should only contain the original content
    assert "boto3" not in pyproject, "Unexpected boto3 in pyproject.toml"
    assert "httpx" not in pyproject, "Unexpected httpx in pyproject.toml"
