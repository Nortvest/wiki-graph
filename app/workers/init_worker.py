from neo4j.exceptions import ServiceUnavailable

from app.dependencies.dependency_container import DependencyContainer
from app.models.page import Page
from app.services.retries import async_retries
from app.workers.base import WorkerBase


class InitWorker(WorkerBase):
    _START_PAGE_NAME = "Философия"

    def __init__(self, container: DependencyContainer) -> None:
        self._page_repository = container.graph_repository_container.page_repository
        self._neo4j_connection = container.neo4j_connection
        self._logger = container.logger

    async def run(self) -> None:
        await self._create_start_page(self._START_PAGE_NAME)

    @async_retries(num_retries=5, timeout=3, exception=ServiceUnavailable)
    async def _create_start_page(self, page: str) -> None:
        page_model = Page(title=page)

        await self._page_repository.create_one_page(page_model)
        self._logger.info("Created start page '%s'", page)
