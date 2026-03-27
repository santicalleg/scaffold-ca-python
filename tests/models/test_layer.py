"""Tests for Layer enum and FORBIDDEN_IMPORTS mapping (T009)."""

import pytest

from scaffold_ca_python.models.layer import FORBIDDEN_IMPORTS, Layer


def test_layer_has_six_values() -> None:
    assert len(Layer) == 6


def test_layer_values() -> None:
    assert Layer.DOMAIN_MODEL.value == "domain/model"
    assert Layer.DOMAIN_USECASE.value == "domain/usecase"
    assert Layer.ENTRY_POINTS.value == "infrastructure/entry-points"
    assert Layer.DRIVEN_ADAPTERS.value == "infrastructure/driven-adapters"
    assert Layer.HELPERS.value == "infrastructure/helpers"
    assert Layer.APPLICATION.value == "application"


def test_forbidden_imports_exists() -> None:
    assert isinstance(FORBIDDEN_IMPORTS, dict)
    assert len(FORBIDDEN_IMPORTS) > 0


def test_domain_model_cannot_import_any_outer_layer() -> None:
    forbidden = FORBIDDEN_IMPORTS[Layer.DOMAIN_MODEL]
    assert Layer.DOMAIN_USECASE in forbidden
    assert Layer.ENTRY_POINTS in forbidden
    assert Layer.DRIVEN_ADAPTERS in forbidden
    assert Layer.HELPERS in forbidden
    assert Layer.APPLICATION in forbidden


def test_domain_usecase_cannot_import_outer_layers() -> None:
    forbidden = FORBIDDEN_IMPORTS[Layer.DOMAIN_USECASE]
    assert Layer.ENTRY_POINTS in forbidden
    assert Layer.DRIVEN_ADAPTERS in forbidden
    assert Layer.HELPERS in forbidden
    assert Layer.APPLICATION in forbidden


def test_application_has_no_forbidden_imports() -> None:
    # APPLICATION is the outermost layer — it may import everything
    forbidden = FORBIDDEN_IMPORTS.get(Layer.APPLICATION, [])
    assert len(forbidden) == 0


def test_layer_is_inner_relative_to_outer() -> None:
    # DOMAIN_MODEL is inner compared to everything else
    assert Layer.DOMAIN_USECASE in FORBIDDEN_IMPORTS[Layer.DOMAIN_MODEL]
    assert Layer.APPLICATION in FORBIDDEN_IMPORTS[Layer.DOMAIN_MODEL]


def test_layer_string_values_are_path_safe() -> None:
    for layer in Layer:
        assert "/" in layer.value or layer.value == "application"


@pytest.mark.parametrize("layer", [Layer.ENTRY_POINTS, Layer.DRIVEN_ADAPTERS, Layer.HELPERS])
def test_infrastructure_layers_cannot_import_application(layer: Layer) -> None:
    forbidden = FORBIDDEN_IMPORTS.get(layer, [])
    assert Layer.APPLICATION in forbidden
