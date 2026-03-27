"""GeneratedFile, CreateFile, DeleteFile, and FileOperation union (T015)."""

from pathlib import Path
from typing import Annotated, Literal

from pydantic import BaseModel


class GeneratedFile(BaseModel):
    path: Path
    content: str
    template_name: str
    is_test: bool = False


class CreateFile(BaseModel):
    kind: Literal["create"] = "create"
    file: GeneratedFile


class DeleteFile(BaseModel):
    kind: Literal["delete"] = "delete"
    path: Path


FileOperation = Annotated[CreateFile | DeleteFile, "FileOperation"]
