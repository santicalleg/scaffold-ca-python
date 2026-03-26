"""Project marker read/write for .scaffold-ca.json."""
from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Literal

MARKER_FILE = ".scaffold-ca.json"


class NoProjectError(Exception):
    """Raised when no .scaffold-ca.json marker file can be found."""


@dataclass
class ComponentRecord:
    type: str  # e.g. "model", "use-case", "driven-adapter", "entry-point", "helper"
    name: str  # snake_case name
    layer: str  # e.g. "domain/model", "infrastructure/driven_adapters"
    generated_files: list[str] = field(default_factory=list)


@dataclass
class ProjectMarker:
    name: str
    base_package: str
    mode: Literal["sync", "async"]
    tool_version: str
    components: list[ComponentRecord] = field(default_factory=list)

    # ---------- persistence ----------

    @classmethod
    def load(cls, root: Path) -> "ProjectMarker":
        marker_path = root / MARKER_FILE
        try:
            data = json.loads(marker_path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise NoProjectError(
                f"No {MARKER_FILE} found at {root}. "
                "Run 'scaffold new' first to initialise a project."
            ) from exc
        components = [ComponentRecord(**c) for c in data.get("components", [])]
        return cls(
            name=data["name"],
            base_package=data["base_package"],
            mode=data["mode"],
            tool_version=data["tool_version"],
            components=components,
        )

    def save(self, root: Path) -> None:
        marker_path = root / MARKER_FILE
        data = {
            "name": self.name,
            "base_package": self.base_package,
            "mode": self.mode,
            "tool_version": self.tool_version,
            "components": [asdict(c) for c in self.components],
        }
        marker_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )

    # ---------- component registry ----------

    def register_component(self, record: ComponentRecord) -> None:
        """Add or replace a component record (matched by type + name)."""
        self.components = [
            c for c in self.components
            if not (c.type == record.type and c.name == record.name)
        ]
        self.components.append(record)

    def deregister_component(self, name: str) -> ComponentRecord | None:
        """Remove and return the component with *name* (case-insensitive snake match).

        Returns None if not found.
        """
        for i, c in enumerate(self.components):
            if c.name.lower() == name.lower():
                return self.components.pop(i)
        return None

    def find_component(self, name: str) -> ComponentRecord | None:
        for c in self.components:
            if c.name.lower() == name.lower():
                return c
        return None


def find_project_root(start: Path | None = None) -> Path:
    """Walk up the directory tree from *start* (default: cwd) to find the project root.

    Raises NoProjectError if no .scaffold-ca.json is found.
    """
    current = (start or Path.cwd()).resolve()
    for directory in [current, *current.parents]:
        if (directory / MARKER_FILE).exists():
            return directory
    raise NoProjectError(
        f"No {MARKER_FILE} found in {current} or any parent directory. "
        "Run 'scaffold new' first to initialise a project, or navigate into a "
        "scaffolded project directory before running this command."
    )
