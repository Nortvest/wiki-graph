from enum import StrEnum, auto

from pydantic import BaseModel


class PageStatus(StrEnum):
    open = auto()
    in_progress = auto()
    failed = auto()
    success = auto()


class Page(BaseModel):
    title: str


class LinkedPages(BaseModel):
    main_page: Page
    secondary_page: Page
