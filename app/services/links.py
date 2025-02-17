import json
import re
from urllib.parse import unquote


class LinkPreprocessor:
    def __init__(self, page: str) -> None:
        self._page = page

    def preprocess(self) -> list[str]:
        links: list[str] = self.find_links()
        links = [self._decode_link(link) for link in links]
        return [self._serialize(link) for link in links]

    def find_links(self) -> list[str]:
        return re.findall(r'href="/wiki/([^"]*)"', self._page)

    @staticmethod
    def _decode_link(link: str) -> str:
        return unquote(link)

    @staticmethod
    def _serialize(link: str) -> str:
        return json.dumps(link, ensure_ascii=False)[1:-1]
