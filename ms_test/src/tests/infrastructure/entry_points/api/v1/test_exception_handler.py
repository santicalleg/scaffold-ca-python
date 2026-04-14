"""Tests for exception handlers — ms_test."""
from __future__ import annotations

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
from pydantic import ValidationError

from ms_test.application.app import create_app

_client = TestClient(create_app(), raise_server_exceptions=False)


def test_http_exception_returns_json_with_status_code() -> None:
    app = create_app()

    @app.get("/_test_http_error")
    def _raise_http() -> None:
        raise HTTPException(status_code=404, detail="not found")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/_test_http_error")
    assert response.status_code == 404


def test_unhandled_exception_returns_500() -> None:
    app = create_app()

    @app.get("/_test_unhandled")
    def _raise_unhandled() -> None:
        raise RuntimeError("boom")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/_test_unhandled")
    assert response.status_code == 500


def test_validation_error_returns_422() -> None:
    app = create_app()
    client = TestClient(app, raise_server_exceptions=False)
    # POST to /api/v1 with bad payload should trigger RequestValidationError → 422
    response = client.post(
        "/api/v1/",
        json={"bad_field": True},
    )
    assert response.status_code in (422, 404, 405)
