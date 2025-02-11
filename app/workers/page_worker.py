from app.dependencies.dependency_container import DependencyContainer
from app.workers.base import WorkerBase


class PageWorker(WorkerBase):
    def __init__(self, container: DependencyContainer) -> None:
        self._wiki_fetchers = container.fetchers_container.wiki_fetchers
        self._page_repository = container.graph_repository_container.page_repository
        self._logger = container.logger

    async def run(self) -> None:
        res = await self._page_repository.get_pages_without_links()
        self._logger.info(res)
