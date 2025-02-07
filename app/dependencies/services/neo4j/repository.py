from logging import Logger

from typing_extensions import Protocol


class Connection(Protocol):
    async def close(self) -> None:
        """Закрывает соединение с базой данных."""

    async def query(self, query: str, parameters: dict[str, str] | None = None) -> list[dict] | None:
        r"""
        Выполняет запрос к базе данных.

        :param query: Запрос. Пример:
        MERGE (p1:Page {title:$p1_title}) MERGE (p2:Page {title:$p2_title}) MERGE (p1)-[l:link]->(p2) RETURN p1, p2

        :param parameters: Параметры запроса. Пример: {"p1_title": "Философия", "p2_title": "Позитивизм"}

        :return: Результат запроса \ Ничего, если возникла ошибка. Пример:
        [{'p1': {'title': 'Философия'}, 'p2': {'title': 'Позитивизм'}}]
        """


class GraphRepository:  # noqa B903
    def __init__(self, connection: Connection, logger: Logger) -> None:
        self._connection = connection
        self._logger = logger


class PageRepository(GraphRepository):
    _CREATE_ONE_PAGE_QUERY = """MERGE (p:Page {title: $page_title})"""
    _CREATE_TWO_PAGES_QUERY = """MERGE (p1:Page {title: $page_title_1}) MERGE (p2:Page {title: $page_title_2})"""

    _CREATE_TWO_PAGES_AND_LINK_QUERY = _CREATE_TWO_PAGES_QUERY + """MERGE (p1)-[l:link]->(p2)"""

    async def create_one_page(self, page_title: str) -> None:
        await self._connection.query(self._CREATE_ONE_PAGE_QUERY, parameters={"page_title", page_title})
        self._logger.info(f"Page with title '{page_title}' was been saved.")

    async def create_two_pages_and_link(self, page_title_1: str, page_title_2: str) -> None:
        await self._connection.query(
            self._CREATE_TWO_PAGES_AND_LINK_QUERY,
            parameters={
                "page_title_1": page_title_1,
                "page_title_2": page_title_2,
            },
        )
        self._logger.info(f"Pages with title '{page_title_1}' and '{page_title_2}' and Link between them were saved.")
