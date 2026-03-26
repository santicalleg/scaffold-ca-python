"""Jinja2 template renderer using importlib.resources."""
from __future__ import annotations

import importlib.resources
from pathlib import Path

from jinja2 import Environment, BaseLoader, TemplateNotFound


class _ResourceLoader(BaseLoader):
    """Load Jinja2 templates from the scaffold_ca_python.templates package."""

    _PACKAGE = "scaffold_ca_python.templates"

    def get_source(
        self, environment: Environment, template: str  # noqa: ARG002
    ) -> tuple[str, str | None, object]:
        # template is a relative path like "project/app/main.py.j2"
        parts = template.replace("\\", "/").split("/")
        package = self._PACKAGE
        # Navigate sub-packages for all but the last segment
        for part in parts[:-1]:
            package = f"{package}.{part}"
        filename = parts[-1]
        try:
            ref = importlib.resources.files(package).joinpath(filename)
            source = ref.read_text(encoding="utf-8")
        except (FileNotFoundError, TypeError, ModuleNotFoundError) as exc:
            raise TemplateNotFound(template) from exc
        return source, str(ref), lambda: True


class TemplateRenderer:
    """Render Jinja2 templates shipped as package data to destination files."""

    def __init__(self) -> None:
        self._env = Environment(
            loader=_ResourceLoader(),
            keep_trailing_newline=True,
            autoescape=False,
        )

    def render_string(self, template_path: str, context: dict) -> str:
        """Render *template_path* with *context* and return the result string."""
        tmpl = self._env.get_template(template_path)
        return tmpl.render(**context)

    def render_to_file(
        self,
        template_path: str,
        dest: Path,
        context: dict,
        force: bool = False,
    ) -> bool:
        """Render *template_path* to *dest*.

        Returns True if the file was written, False if it was skipped.
        Raises FileExistsError if *dest* exists and *force* is False.
        """
        if dest.exists() and not force:
            raise FileExistsError(
                f"File already exists: {dest}. Use --force to overwrite."
            )
        content = self.render_string(template_path, context)
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
        return True

    def render_string_template(self, source: str, context: dict) -> str:
        """Render an inline Jinja2 *source* string with *context*."""
        tmpl = self._env.from_string(source)
        return tmpl.render(**context)
