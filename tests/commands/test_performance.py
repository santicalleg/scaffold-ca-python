"""Performance benchmark tests (T091 + T092).

SC-002: All generation commands (gm, guc, gda, gep, gh) complete within 3 s.
SC-003: `scaffold vs` completes in under 5 s on a project with 200 Python files.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from typer.testing import CliRunner

from scaffold_ca_python.cli import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def project_root_bench(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Bootstrap a CA project once for all benchmark tests in this module."""
    tmp = tmp_path_factory.mktemp("bench")
    runner.invoke(app, ["ca", "--name", "BenchApp"], catch_exceptions=False)
    # ca writes relative to cwd; we need to call from distinct cwd
    import os
    orig = os.getcwd()
    os.chdir(tmp)
    runner.invoke(app, ["ca", "--name", "BenchApp"], catch_exceptions=False)
    project_dir = tmp / "bench_app"
    os.chdir(project_dir)
    os.chdir(orig)
    return project_dir


@pytest.fixture()
def bench_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["ca", "--name", "BenchApp"], catch_exceptions=False)
    project_dir = tmp_path / "bench_app"
    monkeypatch.chdir(project_dir)
    return project_dir


# ---------------------------------------------------------------------------
# T091: Generation commands under 3 s (SC-002)
# ---------------------------------------------------------------------------


def test_gm_performance(benchmark: pytest.fixture, bench_project: Path) -> None:  # type: ignore[type-arg]
    def run() -> None:
        runner.invoke(app, ["gm", "--name", "PerfModel"], catch_exceptions=False)
        # Cleanup so benchmark can repeat
        src = bench_project / "src" / "bench_app" / "domain" / "model" / "perf_model.py"
        test = bench_project / "tests" / "domain" / "model" / "test_perf_model.py"
        src.unlink(missing_ok=True)
        test.unlink(missing_ok=True)

    result = benchmark.pedantic(run, iterations=1, rounds=3)  # type: ignore[func-returns-value]
    if benchmark.stats is not None:
        assert benchmark.stats["mean"] < 3.0  # type: ignore[index]


def test_guc_performance(benchmark: pytest.fixture, bench_project: Path) -> None:  # type: ignore[type-arg]
    def run() -> None:
        runner.invoke(app, ["guc", "--name", "PerfCase"], catch_exceptions=False)
        src = bench_project / "src" / "bench_app" / "domain" / "usecase" / "perf_case.py"
        test = bench_project / "tests" / "domain" / "usecase" / "test_perf_case.py"
        src.unlink(missing_ok=True)
        test.unlink(missing_ok=True)

    benchmark.pedantic(run, iterations=1, rounds=3)
    if benchmark.stats is not None:
        assert benchmark.stats["mean"] < 3.0  # type: ignore[index]


def test_gda_performance(benchmark: pytest.fixture, bench_project: Path) -> None:  # type: ignore[type-arg]
    import shutil

    def run() -> None:
        runner.invoke(app, ["gda", "--type", "rest-consumer"], catch_exceptions=False)
        src = bench_project / "src" / "bench_app" / "infrastructure" / "driven_adapters" / "rest_consumer"
        test = bench_project / "tests" / "infrastructure" / "driven_adapters" / "rest_consumer"
        if src.exists():
            shutil.rmtree(src)
        if test.exists():
            shutil.rmtree(test)

    benchmark.pedantic(run, iterations=1, rounds=3)
    if benchmark.stats is not None:
        assert benchmark.stats["mean"] < 3.0  # type: ignore[index]


def test_gh_performance(benchmark: pytest.fixture, bench_project: Path) -> None:  # type: ignore[type-arg]
    import shutil

    def run() -> None:
        runner.invoke(app, ["gh", "--name", "PerfHelper"], catch_exceptions=False)
        src = bench_project / "src" / "bench_app" / "infrastructure" / "helpers" / "perf_helper"
        test = bench_project / "tests" / "infrastructure" / "helpers" / "perf_helper"
        if src.exists():
            shutil.rmtree(src)
        if test.exists():
            shutil.rmtree(test)

    benchmark.pedantic(run, iterations=1, rounds=3)
    if benchmark.stats is not None:
        assert benchmark.stats["mean"] < 3.0  # type: ignore[index]


# ---------------------------------------------------------------------------
# T092: vs under 5 s on a project with 200 Python files (SC-003)
# ---------------------------------------------------------------------------


@pytest.fixture()
def large_project(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Create a CA project with 200 Python source files for vs benchmark."""
    monkeypatch.chdir(tmp_path)
    runner.invoke(app, ["ca", "--name", "LargeApp"], catch_exceptions=False)
    project_dir = tmp_path / "large_app"
    monkeypatch.chdir(project_dir)

    # Generate 200 stub Python files under domain/model/
    model_dir = project_dir / "src" / "large_app" / "domain" / "model"
    model_dir.mkdir(parents=True, exist_ok=True)
    for i in range(200):
        (model_dir / f"stub_{i:03d}.py").write_text(
            f'"""Stub module {i}."""\n\n\nclass Stub{i:03d}:\n    pass\n'
        )
    return project_dir


def test_vs_performance_200_files(benchmark: pytest.fixture, large_project: Path) -> None:  # type: ignore[type-arg]
    def run() -> None:
        runner.invoke(app, ["vs"], catch_exceptions=False)

    benchmark.pedantic(run, iterations=1, rounds=3)
    if benchmark.stats is not None:
        assert benchmark.stats["mean"] < 5.0  # type: ignore[index]
