"""GeneratedFile, CreateFile, DeleteFile, InsertAfter, and FileOperation union."""

from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel


class GeneratedFile(BaseModel):
    path: Path
    content: str
    template_name: str
    is_test: bool = False
    overwrite: bool = False


class CreateFile(BaseModel):
    kind: Literal["create"] = "create"
    file: GeneratedFile


class DeleteFile(BaseModel):
    kind: Literal["delete"] = "delete"
    path: Path


class InsertAfter(BaseModel):
    """Insert *content* into an existing file immediately after *anchor*.

    The *anchor* string is searched literally (first occurrence).  The content
    is inserted on a new line directly after the line that contains the anchor.

    Raises
    ------
    FileNotFoundError
        When *path* does not exist on disk (real mode only).
    ValueError
        When *anchor* is not found in the file (real mode only).
    """

    kind: Literal["insert_after"] = "insert_after"
    path: Path
    anchor: str
    content: str


FileOperation = Annotated[CreateFile | DeleteFile | InsertAfter, "FileOperation"]
