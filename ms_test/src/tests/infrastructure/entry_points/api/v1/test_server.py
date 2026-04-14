"""Tests for server entry point — ms_test."""
from __future__ import annotations

import importlib


def test_start_server_is_callable() -> None:
    from ms_test.application.app import start_server

    assert callable(start_server)


def test_server_module_imports_without_error() -> None:
    mod = importlib.import_module("ms_test.server")
    assert mod is not None
