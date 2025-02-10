import asyncio

from app.core.settings import Settings
from app.core.workers_factory import WorkersFactory
from app.dependencies.dependency_container import DependencyContainer
from app.workers.workers_manager import WorkersManger


class AppFactory:
    _dependency_container: DependencyContainer | None = None
    _workers_manger: WorkersManger | None = None

    def __init__(self) -> None:
        self.settings = Settings()

    def configure(self) -> None:
        self.configure_dependency_container()
        self.configure_workers()

    def configure_dependency_container(self) -> None:
        log_level: str = self.settings.logger.log_level
        DependencyContainer.configure_logger(log_level)
        DependencyContainer.configure_neo4j(self.settings.graph_db)

        self._dependency_container = DependencyContainer()

    def configure_workers(self) -> None:
        if not self._dependency_container:
            msg = "'DependencyContainer' is not defined! Call 'configure_dependency_container' method."
            raise ValueError(msg)

        workers_factory = WorkersFactory(
            container=self._dependency_container,
            num_page_workers=self.settings.app.num_page_workers,
        )
        workers_factory.configure()
        self._workers_manger: WorkersManger = workers_factory.workers_manger

    def run(self) -> None:
        loop = asyncio.get_event_loop()

        loop.run_until_complete(self._workers_manger.run())
