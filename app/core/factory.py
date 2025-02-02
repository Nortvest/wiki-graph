from app.dependencies.dependency_container import DependencyContainer
from app.dependencies.services.settings import Settings


class AppFactory:
    dependency_container: DependencyContainer | None = None

    def __init__(self) -> None:
        self.settings = Settings()

    def configure(self) -> None:
        self.configure_dependency_container()

    def configure_dependency_container(self) -> None:
        log_level: str = self.settings.logger.log_level
        DependencyContainer.configure_logger(log_level)

        self.dependency_container = DependencyContainer()

    def run(self) -> None:
        print(self.settings)
