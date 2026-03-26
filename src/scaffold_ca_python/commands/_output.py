"""Shared output utilities for scaffold-ca-python commands."""
from __future__ import annotations


def _mode():
    from scaffold_ca_python.cli import get_output_mode, OutputMode  # noqa: PLC0415
    return get_output_mode(), OutputMode


def info(msg: str) -> None:
    """Print informational message (suppressed in quiet mode)."""
    mode, OutputMode = _mode()
    if mode != OutputMode.quiet:
        print(msg)


def verbose(msg: str) -> None:
    """Print debug message (only in verbose mode)."""
    mode, OutputMode = _mode()
    if mode == OutputMode.verbose:
        print(f"[verbose] {msg}")


def error(msg: str) -> None:
    """Always print error messages."""
    print(f"Error: {msg}")
