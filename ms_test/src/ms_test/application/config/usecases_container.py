"""Use-case DI container."""
from dependency_injector import containers, providers

from ms_test.application.config.driven_adapters_container import DAContainer


class UseCaseContainer(containers.DeclarativeContainer):
    """Wire use-case singletons here, injecting driven adapters."""

    da_container = providers.DependenciesContainer()

    # Example:
    # my_use_case = providers.Singleton(
    #     ms_test.application.usecases.my_use_case.MyUseCase,
    #     my_repo=da_container.my_repo,
    # )
