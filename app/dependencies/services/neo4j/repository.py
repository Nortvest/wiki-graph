from __future__ import annotations

from pydantic import TypeAdapter
from typing_extensions import TYPE_CHECKING, Protocol

from app.models.page import Page

if TYPE_CHECKING:
    from logging import Logger


class Connection(Protocol):
    async def close(self) -> None:
        """Закрывает соединение с базой данных."""

    async def query(self, query: str, parameters: dict[str, str | int] | None = None) -> list[dict]:
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
    _CREATE_ONE_PAGE_QUERY = """MERGE (p:Page {title: $page_title})"""
    _CREATE_TWO_PAGES_QUERY = """MERGE (p1:Page {title: $page_title_1}) MERGE (p2:Page {title: $page_title_2})"""

    _CREATE_TWO_PAGES_AND_LINK_QUERY = _CREATE_TWO_PAGES_QUERY + """MERGE (p1)-[l:link]->(p2)"""

    _GET_PAGE_WITHOUT_LINKS_QUERY = """MATCH (page:Page) WHERE not ((page)-[:link]->(:Page)) RETURN page LIMIT $limit"""

    async def create_one_page(self, page_title: str) -> None:
        await self._connection.query(self._CREATE_ONE_PAGE_QUERY, parameters={"page_title": page_title})
        self._logger.debug("Page with title '%s' was been saved.", page_title)

    async def create_two_pages_and_link(self, page_title_1: str, page_title_2: str) -> None:
        await self._connection.query(
            self._CREATE_TWO_PAGES_AND_LINK_QUERY,
            parameters={
                "page_title_1": page_title_1,
                "page_title_2": page_title_2,
            },
        )
        self._logger.debug(
            "Pages with title '%s' and '%s' and Link between them were saved.",
            page_title_1,
            page_title_2,
        )

    async def get_pages_without_links(self, limit: int = 10) -> list[Page]:
        pages = await self._connection.query(self._GET_PAGE_WITHOUT_LINKS_QUERY, parameters={"limit": limit})

        adapter = TypeAdapter(list[Page])
        pages_values = [page["page"] for page in pages]
        page_models = adapter.validate_python(pages_values)

        self._logger.debug("Pages without links were received. %s", page_models)
        return page_models
