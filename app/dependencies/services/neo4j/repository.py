from __future__ import annotations

import asyncio
from itertools import batched

from typing_extensions import TYPE_CHECKING, Protocol

from app.models.page import LinkedPages, Page, PageStatus

if TYPE_CHECKING:
    from logging import Logger

type ParametersValue = str | int | list[PageStatus | str] | PageStatus


class Connection(Protocol):
    async def close(self) -> None:
        """Закрывает соединение с базой данных."""

    async def query(self, query: str, parameters: dict[str, ParametersValue] | None = None) -> list[dict]:
        r"""
        Выполняет запрос к базе данных.

        :param query: Запрос. Пример:
        MERGE (p1:Page {title:$p1_title}) MERGE (p2:Page {title:$p2_title}) MERGE (p1)-[l:link]->(p2) RETURN p1, p2

        :param parameters: Параметры запроса. Пример: {"p1_title": "Философия", "p2_title": "Позитивизм"}

        :return: Результат запроса \ Ничего, если возникла ошибка. Пример:
        [{'p1': {'title': 'Философия'}, 'p2': {'title': 'Позитивизм'}}]
        """


class GraphRepositoryContainer:
    _page_repository: PageRepository | None = None

    def __init__(self, connection: Connection, logger: Logger) -> None:
        self._connection = connection
        self._logger = logger

    @property
    def page_repository(self) -> PageRepository:
        if not self._page_repository:
            self._page_repository = PageRepository(connection=self._connection, logger=self._logger)
        return self._page_repository


class GraphRepository:  # noqa B903
    def __init__(self, connection: Connection, logger: Logger) -> None:
        self._connection = connection
        self._logger = logger


class PageRepository(GraphRepository):
    def __init__(self, connection: Connection, logger: Logger) -> None:
        super().__init__(connection, logger)
        self._read_lock = asyncio.Lock()
        self._write_lock = asyncio.Lock()

    _CREATE_ONE_PAGE_QUERY = """MERGE (p:Page {title: $page_title}) ON CREATE SET p.status = $page_status"""

    _UPDATE_PAGES_STATUS_QUERY = """MATCH (p:Page) WHERE p.title in $page_titles SET p.status = $page_status"""

    _CREATE_TWO_PAGES_QUERY = """MERGE (p1:Page {title: $page_title_1})
                                 MERGE (p2:Page {title: $page_title_2}) ON CREATE SET p2.status = $page_status_2"""

    _CREATE_TWO_PAGES_AND_LINK_QUERY = _CREATE_TWO_PAGES_QUERY + """ MERGE (p1)-[l:link]->(p2)"""

    _CREATE_MANY_PAGES_AND_LINKS_QUERY = """
            MERGE (p%s1:Page {title: $page_title_%s1})
            MERGE (p%s2:Page {title: $page_title_%s2})
            ON CREATE SET p%s2.status = $page_status_%s2
            MERGE (p%s1)-[l%s:link]->(p%s2)

            """

    _GET_PAGE_WITHOUT_LINKS_QUERY = """MATCH (page:Page) WHERE not ((page)-[:link]->(:Page))
                                       AND page.status IN $target_statuses
                                       RETURN page LIMIT $limit"""

    async def create_one_page(self, page: Page) -> None:
        async with self._write_lock:
            await self._connection.query(
                self._CREATE_ONE_PAGE_QUERY,
                parameters={"page_title": page.title, "page_status": PageStatus.open},
            )
        self._logger.debug("Page '%s' was been saved.", page)

    async def update_page_status(self, page: Page, status: PageStatus) -> None:
        async with self._write_lock:
            await self._connection.query(
                self._UPDATE_PAGES_STATUS_QUERY,
                parameters={"page_titles": [page.title], "page_status": status},
            )
        self._logger.debug("Page '%s' was changed status to '%s'.", page, status)

    async def create_two_pages_and_link(self, pages: LinkedPages) -> None:
        async with self._write_lock:
            await self._connection.query(
                self._CREATE_TWO_PAGES_AND_LINK_QUERY,
                parameters={
                    "page_title_1": pages.main_page.title,
                    "page_title_2": pages.secondary_page.title,
                    "page_status_2": PageStatus.open,
                },
            )
        self._logger.debug("Pages '%s' and Link between them were saved.", pages)

    async def create_pages_and_links(self, *linked_pages: LinkedPages, batch_size: int = 100) -> None:
        for pages in batched(linked_pages, n=batch_size):
            params: dict[str, str] = {}
            queries: list[str] = []

            for i, page in enumerate(pages, start=1):
                queries.append(
                    self._CREATE_MANY_PAGES_AND_LINKS_QUERY % ((i, ) * 9),
                )

                params[f"page_title_{i}1"] = page.main_page.title
                params[f"page_title_{i}2"] = page.secondary_page.title
                params[f"page_status_{i}2"] = PageStatus.open

            async with self._write_lock:
                await self._connection.query("\n".join(queries), parameters=params)  # type: ignore

            self._logger.debug("Pages '%s' and Link between them were saved.", pages)

    async def get_pages_without_links(self, limit: int = 10) -> list[Page]:
        params = {
            "limit": limit,
            "target_statuses": [PageStatus.open, PageStatus.failed],
            "page_status": PageStatus.in_progress,
        }

        async with self._read_lock:
            pages = await self._connection.query(self._GET_PAGE_WITHOUT_LINKS_QUERY, parameters=params)  # type: ignore
            page_models: list[Page] = [Page.model_validate(page["page"]) for page in pages]

            await self._connection.query(
                self._UPDATE_PAGES_STATUS_QUERY,
                parameters={"page_titles": [page.title for page in page_models], "page_status": PageStatus.in_progress},
            )

        self._logger.debug("Pages without links were received. %s", page_models)
        return page_models
