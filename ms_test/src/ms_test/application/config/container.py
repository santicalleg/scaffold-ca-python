"""Root application DI container."""
from dependency_injector import containers, providers

from ms_test.application.config.driven_adapters_container import DAContainer
from ms_test.application.config.usecases_container import UseCaseContainer


class Container(containers.DeclarativeContainer):
    """Top-level container wiring all sub-containers."""

    da_container = providers.Container(DAContainer)
    usecase_container = providers.Container(
        UseCaseContainer,
        da_container=da_container,
    )
