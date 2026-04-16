"""Tests for ModuleBuilder foundational behavior (T010)."""

from __future__ import annotations

from pathlib import Path

from scaffold_ca_python.core.module_builder import ModuleBuilder
from scaffold_ca_python.models.context import ModuleContext, ProjectContext
from scaffold_ca_python.models.layer import Layer


class _StubRenderer:
    def __init__(self) -> None:
        self.calls: list[tuple[str, object]] = []

    def render(self, template_name: str, context: object) -> str:
        self.calls.append((template_name, context))
        return "# rendered"


class _FilesystemReadingFactory:
    def __init__(self, probe: Path) -> None:
        self._probe = probe

    def build(self, builder: ModuleBuilder) -> None:
        # The call below must execute even when builder.dry_run is True.
        builder.add_param("probe_exists", self._probe.exists())


def _project_ctx() -> ProjectContext:
    return ProjectContext(name="ms-demo")


def _module_ctx(project: ProjectContext) -> ModuleContext:
    return ModuleContext(name="health", layer=Layer.ENTRY_POINTS, project=project)


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


def test_add_file_and_dry_run_returns_preview_without_writing(tmp_path: Path) -> None:
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, module_ctx=_module_ctx(project), dry_run=True)

    target = tmp_path / "src" / "ms_demo" / "domain" / "model" / "health.py"
    builder.add_file(target, "class Health: pass\n", template_name="model.py.jinja2")

    preview = builder.persist()

    assert target in preview
    assert not target.exists()


def test_delete_file_operation_is_included_in_preview(tmp_path: Path) -> None:
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, dry_run=True)

    target = tmp_path / "obsolete.py"
    builder.delete_file(target)

    preview = builder.persist()

    assert target in preview


def test_add_dependency_and_real_persist_injects_dependency(tmp_path: Path) -> None:
    _write_minimal_pyproject(tmp_path)
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, dry_run=False)

    builder.add_dependency("httpx>=0.27")

    _ = builder.persist()
    pyproject = (tmp_path / "pyproject.toml").read_text(encoding="utf-8")

    assert "httpx>=0.27" in pyproject


def test_add_param_and_get_param_round_trip(tmp_path: Path) -> None:
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, dry_run=True)

    builder.add_param("k", "v")

    assert builder.get_param("k") == "v"
    assert builder.get_param("missing", "default") == "default"


def test_render_delegates_to_template_renderer(tmp_path: Path) -> None:
    project = _project_ctx()
    stub = _StubRenderer()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, dry_run=True, template_renderer=stub)  # type: ignore[arg-type]

    out = builder.render("x.jinja2", {"a": 1})

    assert out == "# rendered"
    assert stub.calls == [("x.jinja2", {"a": 1})]


def test_persist_real_writes_file(tmp_path: Path) -> None:
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, dry_run=False)

    target = tmp_path / "a.py"
    builder.add_file(target, "# ok\n", template_name="a.jinja2")

    written = builder.persist()

    assert target in written
    assert target.read_text(encoding="utf-8") == "# ok\n"


def test_filesystem_read_in_factory_runs_during_dry_run(tmp_path: Path) -> None:
    project = _project_ctx()
    builder = ModuleBuilder(project_root=tmp_path, project_ctx=project, dry_run=True)

    probe = tmp_path / "probe.flag"
    probe.write_text("x", encoding="utf-8")

    factory = _FilesystemReadingFactory(probe)
    factory.build(builder)
    _ = builder.persist()

    assert builder.get_param("probe_exists") is True
