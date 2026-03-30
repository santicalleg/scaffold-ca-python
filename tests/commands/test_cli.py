"""Tests for root CLI app behaviour (T005, T017)."""

from typer.testing import CliRunner

from scaffold_ca_python.cli import app

runner = CliRunner()


# ---------------------------------------------------------------------------
# US1: root --help listing (T005)
# ---------------------------------------------------------------------------

def test_root_help_shows_clean_architecture() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "clean-architecture" in result.output


def test_root_help_does_not_show_generate_project() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "generate-project" not in result.output


def test_root_help_alias_visible_in_description() -> None:
    """FR-013: clean-architecture description must mention the ca alias."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "ca" in result.output
