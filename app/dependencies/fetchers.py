from __future__ import annotations

from typing_extensions import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from app.dependencies.services.logger import Logger

type HTMLString = str


class HttpClient(Protocol):
    base_url: str | None
    headers: dict[str, str] | None
    timeout: int | None

    async def get(
            self,
            url: str,
            params: dict | None = None,
            **kwargs: dict | str | None,
    ) -> dict | str:
        """
        Асинхронный метод для выполнения запросов GET с логикой повторных попыток.

        :param url: Путь или полный URL-адрес, по которому выполняется запрос GET.
        :param params: Необязательный словарь параметров запроса, который будет добавлен к URL.
        :param kwargs: Дополнительные аргументы ключевого слова, которые должны быть переданы в запрос.
        :return: Ответ в формате JSON или текстовый ответ в зависимости от типа содержимого.
        :raises TimeoutError: Если время ожидания запроса истекло после всех повторных попыток.
        :raises Exception: Другие исключения, возникающие во время запроса.
        """

    async def post(
            self,
            url: str,
            data: dict | None = None,
            json: dict | None = None,
            **kwargs: dict | str | None,
    ) -> dict | str:
        """
        Асинхронный метод для выполнения POST-запросов с логикой повторных попыток.

        :param url: Путь или полный URL-адрес, на который отправляется POST-запрос.
        :param data: Необязательные данные формы, которые будут отправлены в теле запроса.
        :param json: Необязательный объект JSON, который должен быть отправлен в теле запроса.
        :param kwargs: Дополнительные аргументы ключевого слова, которые должны быть переданы в запрос.
        :return: Ответ в формате JSON или текстовый ответ в зависимости от типа содержимого.
        :raises TimeoutError: Если время ожидания запроса истекло после всех повторных попыток.
        :raises Exception: Другие исключения, возникающие во время запроса.
        """


class FetchersContainer:
    _wiki_fetchers: WikiFetchers | None = None

    def __init__(self, http_client: HttpClient, logger: Logger) -> None:
        self._http_client = http_client
        self._logger = logger

    @property
    def wiki_fetchers(self) -> WikiFetchers:
        if not self._wiki_fetchers:
            self._wiki_fetchers = WikiFetchers(http_client=self._http_client, logger=self._logger)
        return self._wiki_fetchers


class Fetchers:  # noqa B903
    BASE_URL: str = ""

    def __init__(self, http_client: HttpClient, logger: Logger) -> None:
        self._http_client = http_client
        self._logger = logger

    def _build_page_url(self, *paths: str) -> str:
        return self.BASE_URL + "".join(paths)


class WikiFetchers(Fetchers):
    BASE_URL = "https://ru.wikipedia.org/"

    WIKI_PAGE_PATH = "wiki/"

    def __init__(self, http_client: HttpClient, logger: Logger) -> None:
        http_client.base_url = self.BASE_URL
        super().__init__(http_client, logger)

    async def fetch_wiki_page(self, page_name: str) -> HTMLString | None:
        url = self._build_page_url(self.WIKI_PAGE_PATH, page_name)

        try:
            html: dict | HTMLString = await self._http_client.get(url=url)
        except TimeoutError:
            self._logger.exception("Wikipedia page '%s' timed out.", page_name)
            return None
        else:
            if isinstance(html, str):
                return html
            self._logger.warning("Wikipedia page '%s' is not string. Out: %s", page_name, html)
        return None

