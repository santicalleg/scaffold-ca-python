"""Violation and ValidationReport Pydantic v2 models (T016)."""

from pathlib import Path

from pydantic import BaseModel

from scaffold_ca_python.models.layer import Layer


class Violation(BaseModel):
    source_file: Path
    line_number: int
    import_statement: str
    source_layer: Layer
    target_layer: Layer
    resolution_hint: str


class ValidationReport(BaseModel):
    project_root: Path
    files_scanned: int
    violations: list[Violation]

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0
