from app.core.settings import Settings
from app.dependencies.dependency_container import DependencyContainer


class AppFactory:
    dependency_container: DependencyContainer | None = None

    def __init__(self) -> None:
        self.settings = Settings()

    def configure(self) -> None:
        self.configure_dependency_container()

    def configure_dependency_container(self) -> None:
        log_level: str = self.settings.logger.log_level
        DependencyContainer.configure_logger(log_level)
        DependencyContainer.configure_neo4j(self.settings.graph_db)

        self.dependency_container = DependencyContainer()

    def run(self) -> None:
        pass
