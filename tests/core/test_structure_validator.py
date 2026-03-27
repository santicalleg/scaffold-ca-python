"""Unit tests for StructureValidator (T057)."""

from __future__ import annotations

from pathlib import Path

import pytest

from scaffold_ca_python.core.structure_validator import StructureValidator
from scaffold_ca_python.models.layer import Layer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Clean project — no violations
# ---------------------------------------------------------------------------


def test_clean_project_returns_empty_violations(tmp_path: Path) -> None:
    src = tmp_path / "src" / "my_app"
    _write(src / "domain" / "model" / "__init__.py", "")
    _write(src / "domain" / "model" / "order.py", "from dataclasses import dataclass\n")

    report = StructureValidator().validate(tmp_path)

    assert report.passed
    assert report.violations == []


def test_files_scanned_counts_known_layer_files(tmp_path: Path) -> None:
    src = tmp_path / "src" / "my_app"
    _write(src / "domain" / "model" / "__init__.py", "")
    _write(src / "domain" / "model" / "order.py", "")
    _write(src / "domain" / "usecase" / "__init__.py", "")
    _write(src / "domain" / "usecase" / "create_order.py", "")

    report = StructureValidator().validate(tmp_path)

    assert report.files_scanned == 4


def test_usecase_importing_domain_model_is_allowed(tmp_path: Path) -> None:
    src = tmp_path / "src" / "my_app"
    _write(src / "domain" / "model" / "__init__.py", "")
    _write(src / "domain" / "usecase" / "__init__.py", "")
    _write(
        src / "domain" / "usecase" / "create_order.py",
        "from my_app.domain.model.order import Order\n",
    )

    report = StructureValidator().validate(tmp_path)

    assert report.passed


def test_intra_layer_import_is_allowed(tmp_path: Path) -> None:
    src = tmp_path / "src" / "my_app"
    _write(src / "domain" / "model" / "__init__.py", "")
    _write(src / "domain" / "model" / "base.py", "")
    _write(
        src / "domain" / "model" / "order.py",
        "from my_app.domain.model.base import Base\n",
    )

    report = StructureValidator().validate(tmp_path)

    assert report.passed


# ---------------------------------------------------------------------------
# Violations — domain/model importing outward
# ---------------------------------------------------------------------------


def test_domain_model_importing_driven_adapter_is_violation(tmp_path: Path) -> None:
    src = tmp_path / "src" / "my_app"
    _write(src / "domain" / "model" / "__init__.py", "")
    _write(
        src / "domain" / "model" / "order.py",
        "from my_app.infrastructure.driven_adapters.rest_consumer import Client\n",
    )

    report = StructureValidator().validate(tmp_path)

    assert not report.passed
    assert len(report.violations) == 1
    v = report.violations[0]
    assert v.source_layer == Layer.DOMAIN_MODEL
    assert v.target_layer == Layer.DRIVEN_ADAPTERS
    assert v.line_number == 1
    assert "driven_adapters" in v.import_statement


def test_violation_contains_source_file_path(tmp_path: Path) -> None:
    src = tmp_path / "src" / "my_app"
    order_file = src / "domain" / "model" / "order.py"
    _write(order_file, "from my_app.infrastructure.entry_points.restapi import main\n")

    report = StructureValidator().validate(tmp_path)

    assert not report.passed
    assert report.violations[0].source_file == order_file


def test_violation_contains_resolution_hint(tmp_path: Path) -> None:
    src = tmp_path / "src" / "my_app"
    _write(
        src / "domain" / "model" / "order.py",
        "from my_app.infrastructure.helpers.logging import Logger\n",
    )

    report = StructureValidator().validate(tmp_path)

    assert report.violations[0].resolution_hint != ""


def test_domain_model_importing_application_is_violation(tmp_path: Path) -> None:
    src = tmp_path / "src" / "my_app"
    _write(src / "domain" / "model" / "__init__.py", "")
    _write(
        src / "domain" / "model" / "order.py",
        "from my_app.application import config\n",
    )

    report = StructureValidator().validate(tmp_path)

    assert not report.passed
    assert report.violations[0].target_layer == Layer.APPLICATION


def test_domain_usecase_importing_infrastructure_is_violation(tmp_path: Path) -> None:
    src = tmp_path / "src" / "my_app"
    _write(src / "domain" / "usecase" / "__init__.py", "")
    _write(
        src / "domain" / "usecase" / "create_order.py",
        "from my_app.infrastructure.driven_adapters.rest_consumer import Client\n",
    )

    report = StructureValidator().validate(tmp_path)

    assert not report.passed
    assert report.violations[0].source_layer == Layer.DOMAIN_USECASE
    assert report.violations[0].target_layer == Layer.DRIVEN_ADAPTERS


def test_multiple_violations_collected(tmp_path: Path) -> None:
    src = tmp_path / "src" / "my_app"
    _write(
        src / "domain" / "model" / "order.py",
        (
            "from my_app.infrastructure.driven_adapters.rest_consumer import Client\n"
            "from my_app.infrastructure.helpers.logging import Logger\n"
        ),
    )

    report = StructureValidator().validate(tmp_path)

    assert len(report.violations) == 2


# ---------------------------------------------------------------------------
# ast.Import (bare import) form
# ---------------------------------------------------------------------------


def test_bare_import_form_detected(tmp_path: Path) -> None:
    src = tmp_path / "src" / "my_app"
    _write(
        src / "domain" / "model" / "order.py",
        "import my_app.infrastructure.driven_adapters.rest_consumer\n",
    )

    report = StructureValidator().validate(tmp_path)

    assert not report.passed
    assert "import my_app.infrastructure.driven_adapters" in report.violations[0].import_statement


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


def test_no_src_raises_scaffold_error(tmp_path: Path) -> None:
    from scaffold_ca_python.core.name_utils import ScaffoldError

    with pytest.raises(ScaffoldError, match="src/"):
        StructureValidator().validate(tmp_path)


def test_files_outside_known_layers_are_skipped(tmp_path: Path) -> None:
    src = tmp_path / "src" / "my_app"
    # A file at the package root — not inside any layer directory
    _write(src / "conftest.py", "from my_app.infrastructure.driven_adapters.x import Y\n")
    _write(src / "domain" / "model" / "__init__.py", "")

    report = StructureValidator().validate(tmp_path)

    # The conftest.py at root level has no layer, so no violation should be raised
    assert report.passed


def test_malformed_file_is_skipped(tmp_path: Path) -> None:
    src = tmp_path / "src" / "my_app"
    _write(src / "domain" / "model" / "bad.py", "def broken(\n")

    report = StructureValidator().validate(tmp_path)

    # malformed file should be skipped — no crash, violations list is empty
    assert report.violations == []
