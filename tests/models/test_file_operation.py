"""Tests for GeneratedFile, CreateFile, DeleteFile, FileOperation union (T011)."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from scaffold_ca_python.models.file_operation import CreateFile, DeleteFile, FileOperation, GeneratedFile


# ---------------------------------------------------------------------------
# GeneratedFile
# ---------------------------------------------------------------------------

def test_generated_file_fields() -> None:
    gf = GeneratedFile(
        path=Path("/tmp/project/domain/model/order.py"),
        content="class Order: pass",
        template_name="model/model.py.jinja2",
    )
    assert gf.path == Path("/tmp/project/domain/model/order.py")
    assert gf.content == "class Order: pass"
    assert gf.template_name == "model/model.py.jinja2"
    assert gf.is_test is False


def test_generated_file_is_test_flag() -> None:
    gf = GeneratedFile(
        path=Path("/tmp/tests/domain/model/test_order.py"),
        content="def test_order(): ...",
        template_name="model/test_model.py.jinja2",
        is_test=True,
    )
    assert gf.is_test is True


def test_generated_file_requires_path() -> None:
    with pytest.raises(ValidationError):
        GeneratedFile(content="x", template_name="t.jinja2")  # type: ignore[call-arg]


# ---------------------------------------------------------------------------
# CreateFile
# ---------------------------------------------------------------------------

def test_create_file_kind_discriminator() -> None:
    gf = GeneratedFile(
        path=Path("/tmp/x.py"),
        content="pass",
        template_name="tmpl.jinja2",
    )
    op = CreateFile(file=gf)
    assert op.kind == "create"


def test_create_file_has_file_field() -> None:
    gf = GeneratedFile(path=Path("/tmp/x.py"), content="", template_name="t.jinja2")
    op = CreateFile(file=gf)
    assert op.file is gf


# ---------------------------------------------------------------------------
# DeleteFile
# ---------------------------------------------------------------------------

def test_delete_file_kind_discriminator() -> None:
    op = DeleteFile(path=Path("/tmp/x.py"))
    assert op.kind == "delete"


def test_delete_file_has_path_field() -> None:
    p = Path("/tmp/x.py")
    op = DeleteFile(path=p)
    assert op.path == p


# ---------------------------------------------------------------------------
# FileOperation union
# ---------------------------------------------------------------------------

def test_file_operation_is_union() -> None:
    gf = GeneratedFile(path=Path("/tmp/x.py"), content="", template_name="t.jinja2")
    create: FileOperation = CreateFile(file=gf)
    delete: FileOperation = DeleteFile(path=Path("/tmp/x.py"))
    assert create.kind == "create"
    assert delete.kind == "delete"


def test_file_operation_kind_distinguishes_types() -> None:
    gf = GeneratedFile(path=Path("/tmp/x.py"), content="", template_name="t.jinja2")
    ops: list[FileOperation] = [
        CreateFile(file=gf),
        DeleteFile(path=Path("/tmp/y.py")),
    ]
    kinds = [op.kind for op in ops]
    assert kinds == ["create", "delete"]
