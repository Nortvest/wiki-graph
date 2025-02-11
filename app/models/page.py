from pydantic import BaseModel


class Page(BaseModel):
    title: str
