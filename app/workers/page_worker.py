import asyncio

from app.dependencies.dependency_container import DependencyContainer
from app.models.page import LinkedPages, Page, PageStatus
from app.services.links import LinkPreprocessor
from app.workers.base import WorkerBase


class PageWorker(WorkerBase):
    def __init__(self, container: DependencyContainer) -> None:
        self._wiki_fetchers = container.fetchers_container.wiki_fetchers
        self._page_repository = container.graph_repository_container.page_repository
        self._logger = container.logger

    async def run(self) -> None:
        while True:
            pages: list[Page] = await self._page_repository.get_pages_without_links()

            try:
                await self._process_pages(pages)
            except Exception:
                self._logger.exception("Failed to process pages")

                for page in pages:
                    await self._page_repository.update_page_status(page=page, status=PageStatus.failed)

    async def _process_pages(self, pages: list[Page]) -> None:
        if not pages:
            await asyncio.sleep(5)
            return

        for page in pages:
            await self._process_page(page)

    async def _process_page(self, page: Page) -> None:
        try:
            page_html = await self._wiki_fetchers.fetch_wiki_page(page.title)

            if page_html is None:
                await self._page_repository.update_page_status(page=page, status=PageStatus.success)
                return

        except Exception:
            await self._page_repository.update_page_status(page=page, status=PageStatus.success)
            self._logger.exception("Failed to fetch wiki page")
            return

        link_preprocessor = LinkPreprocessor(page=page_html)
        page_names: list[str] = link_preprocessor.preprocess()

        linked_pages: list[LinkedPages] = [
            LinkedPages(main_page=page, secondary_page=Page(title=name))
            for name in page_names
        ]

        await self._page_repository.create_pages_and_links(*linked_pages, batch_size=10)
        self._logger.info(
            "[Worker %s] Created %d pages. From page: %s",
            id(self), len(linked_pages), page.title,
        )

        await self._page_repository.update_page_status(page=page, status=PageStatus.success)
