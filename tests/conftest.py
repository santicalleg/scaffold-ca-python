"""Pytest configuration and shared fixtures."""

import re


def strip_ansi(text: str) -> str:
    """Remove ANSI color codes from text.

    GitHub Actions may render CLI output with ANSI color codes even in
    non-interactive environments, which can interfere with string matching.
    This function removes them for consistent test assertions.
    """
    ansi_escape = re.compile(r"\x1b\[[0-9;]*m")
    return ansi_escape.sub("", text)
