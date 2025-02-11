from __future__ import annotations

import asyncio
from enum import StrEnum

import aiohttp
from tenacity import AsyncRetrying, RetryError, retry_if_exception_type, stop_after_attempt, wait_fixed


class HttpClientErrors(StrEnum):
    INTERNAL_SERVER_ERROR = "Internal Server Error."
    GET_REQUEST_TIMEOUT = "Get request was not executed due to a timeout. URL: {url}"
    POST_REQUEST_TIMEOUT = "Post request was not executed due to a timeout. URL: {url}"


class HttpClient:
    def __init__(
        self,
        base_url: str | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
        max_retries: int = 1,
        retry_wait: float = 5.0,
    ) -> None:
        """
        Инициализируйте клиент с помощью необязательных заголовков, базового URL-адреса и тайм-аута.

        :param base_url: Необязательный базовый URL-адрес, который будет использоваться для всех запросов.
        :param headers: Необязательные заголовки, которые будут добавляться ко всем HTTP-запросам. Должен быть словарь.
        :param timeout: Необязательный тайм-аут для запросов в секундах.
                        Если он не указан, используется тайм-аут по умолчанию.
        :param max_retries: Максимальное количество повторных попыток.
        :param retry_wait: Время ожидания между повторными попытками измеряется в секундах.
        """
        self.base_url = base_url
        self.headers = headers or {}
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_wait = retry_wait

    @staticmethod
    async def fetch(
            session: aiohttp.ClientSession,
            method: str,
            url: str,
            **request_kwargs: float | bool | str | list | dict | None) -> float | bool | str | list | dict | None:
        """
        Статический вспомогательный метод для выполнения HTTP-запроса.

        :param session: Экземпляр aiohttp.ClientSession для выполнения HTTP-запросов.
        :param method: Метод HTTP-запроса (например, 'GET', 'POST').
        :param url: URL-адрес, по которому выполняется запрос.
        :param request_kwargs: Дополнительные аргументы для запроса, такие как параметры, данные, JSON и заголовки.
        :return: Ответ в формате JSON или текстовый ответ в зависимости от типа содержимого.
        :raises aiohttp.ClientResponseError: Если в ответе содержится сообщение об ошибке HTTP.
        :raises aiohttp.ClientError: Для других ошибок, связанных с клиентом.
        """
        async with session.request(method, url, **request_kwargs) as response:  # type: ignore
            response.raise_for_status()
            try:
                return await response.json()
            except aiohttp.ContentTypeError:
                return await response.text()

    async def _request_with_retries(  # type: ignore
        self,
        method: str,
        url: str,
        **request_kwargs: dict | str | None,
    ) -> dict | str:
        """
        Внутренний метод для выполнения HTTP-запроса с логикой повторных попыток.

        :param method: Метод HTTP-запроса (например, 'GET', 'POST').
        :param url: URL-адрес, по которому выполняется запрос.
        :param request_kwargs: Дополнительные аргументы для запроса.
        :return: Ответ в формате JSON или текстовый ответ в зависимости от типа содержимого.
        :raises Exception: Последнее исключение, возникающее после того, как все повторные попытки будут исчерпаны.
        """
        retry_strategy = AsyncRetrying(
            stop=stop_after_attempt(self.max_retries),
            wait=wait_fixed(self.retry_wait),
            retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
            reraise=True,
        )

        try:
            async for attempt in retry_strategy:
                with attempt:
                    return await self._perform_request(method, url, **request_kwargs)
        except RetryError:
            raise RuntimeError(HttpClientErrors.INTERNAL_SERVER_ERROR) from None
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            raise RuntimeError(HttpClientErrors.INTERNAL_SERVER_ERROR) from e

    async def _perform_request(
        self,
        method: str,
        url: str,
        **request_kwargs: dict | str | None,
    ) -> dict | str:
        """
        Выполняет фактический запрос с тайм-аутом.

        :param method: Метод HTTP-запроса (например, 'GET', 'POST').
        :param url: URL-адрес, по которому выполняется запрос.
        :param request_kwargs: Дополнительные аргументы для запроса.
        :return: Ответ в формате JSON или текстовый ответ в зависимости от типа содержимого.
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with asyncio.timeout(self.timeout):
                return await self.fetch(session, method, url, **request_kwargs)

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
        if self.base_url and not url.startswith(("http://", "https://")):
            url = self.base_url + url

        try:
            return await self._request_with_retries("GET", url, params=params, **kwargs)
        except asyncio.TimeoutError:
            error_message = HttpClientErrors.GET_REQUEST_TIMEOUT.format(url=url)
            raise TimeoutError(error_message) from None

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
        if self.base_url and not url.startswith(("http://", "https://")):
            url = self.base_url + url

        try:
            return await self._request_with_retries("POST", url, data=data, json=json, **kwargs)
        except asyncio.TimeoutError:
            error_message = HttpClientErrors.POST_REQUEST_TIMEOUT.format(url=url)
            raise TimeoutError(error_message) from None
