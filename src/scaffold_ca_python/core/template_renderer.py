"""template_renderer: Jinja2 rendering via importlib.resources (T024)."""

from __future__ import annotations

import importlib.resources
from typing import Any

from jinja2 import BaseLoader, Environment, TemplateNotFound
from pydantic import BaseModel

from scaffold_ca_python.core.name_utils import ScaffoldError


class _ResourceLoader(BaseLoader):
    """Jinja2 loader backed by ``importlib.resources.files()``."""

    _PACKAGE = "scaffold_ca_python.templates"

    def get_source(
        self,
        environment: Environment,
        template: str,
    ) -> tuple[str, str | None, Any]:
        try:
            ref = importlib.resources.files(self._PACKAGE).joinpath(template)
            source = ref.read_text(encoding="utf-8")
            return source, str(ref), None
        except (FileNotFoundError, TypeError) as exc:
            raise TemplateNotFound(template) from exc


class TemplateRenderer:
    """Load and render Jinja2 templates from the ``scaffold_ca_python.templates`` package.

    Usage::

        renderer = TemplateRenderer()

        # Render a packaged template
        output = renderer.render("domain_model.py.j2", module_ctx)

        # Render an inline template string (useful for testing / simple cases)
        output = renderer.render_string("class {{ class_name }}:", ctx_dict)
    """

    def __init__(self) -> None:
        self._env = Environment(
            loader=_ResourceLoader(),
            autoescape=False,
            keep_trailing_newline=True,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def render(self, template_name: str, context: BaseModel | dict[str, Any]) -> str:
        """Render *template_name* with the fields from *context*.

        *context* may be a Pydantic ``BaseModel`` (``model_dump()`` is called
        automatically) or a plain ``dict``.

        Raises
        ------
        ScaffoldError
            When the template is not found in the package.
        """
        ctx_dict = self._to_dict(context)
        try:
            tmpl = self._env.get_template(template_name)
        except TemplateNotFound as exc:
            raise ScaffoldError(
                f"Template {template_name!r} not found in scaffold_ca_python.templates. "
                "Hint: ensure the template file exists in the package."
            ) from exc
        return tmpl.render(**ctx_dict)

    def render_string(self, source: str, context: BaseModel | dict[str, Any]) -> str:
        """Render an inline *source* string with *context*.

        Primarily useful for tests and one-off generation.
        """
        ctx_dict = self._to_dict(context)
        tmpl = self._env.from_string(source)
        return tmpl.render(**ctx_dict)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_dict(context: BaseModel | dict[str, Any]) -> dict[str, Any]:
        """Convert a Pydantic model or plain dict to a render context dict."""
        if isinstance(context, dict):
            return context
        # Pydantic v2 BaseModel
        if hasattr(context, "model_dump"):
            return context.model_dump()
        # Fallback: try __dict__
        return dict(vars(context))
