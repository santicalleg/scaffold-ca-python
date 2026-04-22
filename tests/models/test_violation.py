"""Tests for Violation and ValidationReport models (T012)."""

from pathlib import Path

from scaffold_ca_python.models.layer import Layer
from scaffold_ca_python.models.violation import ValidationReport, Violation


def _make_violation() -> Violation:
    return Violation(
        source_file=Path("/tmp/project/domain/model/order.py"),
        line_number=3,
        import_statement="from infrastructure.driven_adapters.rest import RestClient",
        source_layer=Layer.DOMAIN_MODEL,
        target_layer=Layer.DRIVEN_ADAPTERS,
        resolution_hint="Remove infrastructure imports from domain/model/. Move this logic to a use case or adapter.",
    )


# ---------------------------------------------------------------------------
# Violation
# ---------------------------------------------------------------------------


def test_violation_fields_populated() -> None:
    v = _make_violation()
    assert v.source_file == Path("/tmp/project/domain/model/order.py")
    assert v.line_number == 3
    assert v.import_statement.startswith("from infrastructure")
    assert v.source_layer == Layer.DOMAIN_MODEL
    assert v.target_layer == Layer.DRIVEN_ADAPTERS
    assert len(v.resolution_hint) > 0


def test_violation_line_number_is_one_based() -> None:
    v = _make_violation()
    assert v.line_number >= 1


# ---------------------------------------------------------------------------
# ValidationReport
# ---------------------------------------------------------------------------


def test_validation_report_passed_when_no_violations() -> None:
    report = ValidationReport(
        project_root=Path("/tmp/project"),
        files_scanned=10,
        violations=[],
    )
    assert report.passed is True


def test_validation_report_fails_when_violations_exist() -> None:
    report = ValidationReport(
        project_root=Path("/tmp/project"),
        files_scanned=10,
        violations=[_make_violation()],
    )
    assert report.passed is False


def test_validation_report_files_scanned_counter() -> None:
    report = ValidationReport(
        project_root=Path("/tmp/project"),
        files_scanned=42,
        violations=[],
    )
    assert report.files_scanned == 42


def test_validation_report_violations_list_length() -> None:
    violations = [_make_violation(), _make_violation()]
    report = ValidationReport(
        project_root=Path("/tmp/project"),
        files_scanned=5,
        violations=violations,
    )
    assert len(report.violations) == 2
    assert report.passed is False


def test_validation_report_zero_files_scanned_passes() -> None:
    report = ValidationReport(
        project_root=Path("/tmp/empty"),
        files_scanned=0,
        violations=[],
    )
    assert report.passed is True
