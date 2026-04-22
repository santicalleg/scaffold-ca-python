"""Layer enum and FORBIDDEN_IMPORTS dependency mapping (T013)."""

from enum import StrEnum


class Layer(StrEnum):
    DOMAIN_MODEL = "domain/model"
    DOMAIN_USECASE = "domain/usecase"
    ENTRY_POINTS = "infrastructure/entry-points"
    DRIVEN_ADAPTERS = "infrastructure/driven-adapters"
    HELPERS = "infrastructure/helpers"
    APPLICATION = "application"


# Maps each inner layer to the set of outer layers it must NOT import from.
# Layers not present as keys (APPLICATION) may import from any layer.
FORBIDDEN_IMPORTS: dict[Layer, list[Layer]] = {
    Layer.DOMAIN_MODEL: [
        Layer.DOMAIN_USECASE,
        Layer.ENTRY_POINTS,
        Layer.DRIVEN_ADAPTERS,
        Layer.HELPERS,
        Layer.APPLICATION,
    ],
    Layer.DOMAIN_USECASE: [
        Layer.ENTRY_POINTS,
        Layer.DRIVEN_ADAPTERS,
        Layer.HELPERS,
        Layer.APPLICATION,
    ],
    Layer.ENTRY_POINTS: [
        Layer.APPLICATION,
    ],
    Layer.DRIVEN_ADAPTERS: [
        Layer.APPLICATION,
    ],
    Layer.HELPERS: [
        Layer.APPLICATION,
    ],
    Layer.APPLICATION: [],
}
