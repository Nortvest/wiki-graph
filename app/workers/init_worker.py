from app.dependencies.dependency_container import DependencyContainer
from app.workers.base import WorkerBase


class InitWorker(WorkerBase):
    _START_PAGE_NAME = "Философия"

    def __init__(self, container: DependencyContainer) -> None:
        self._page_repository = container.graph_repository_container.page_repository
        self._logger = container.logger

    async def run(self) -> None:
        await self._create_start_page(self._START_PAGE_NAME)

    async def _create_start_page(self, page: str) -> None:
        await self._page_repository.create_one_page(page)
        self._logger.info("Created start page '%s'", page)
