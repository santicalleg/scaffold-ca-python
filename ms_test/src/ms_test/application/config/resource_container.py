"""Resource DI container — wires infrastructure resources (DB pools, HTTP clients, etc.)."""
from dependency_injector import containers, providers
from pydantic_settings import BaseSettings

from ms_test.application.config.config import Settings


class ResourceContainer(containers.DeclarativeContainer):
    """Wire resource-level singletons (connections, clients) here."""

    settings: providers.Provider[BaseSettings] = providers.Singleton(Settings)

    # Example:
    # db_pool = providers.Resource(
    #     ms_test.infrastructure.driven_adapters.db.init_pool,
    #     url=settings.provided.DATABASE_URL,
    # )
