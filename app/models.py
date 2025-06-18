from pydantic import BaseModel

class DocItem(BaseModel):
    title: str
    content: str

class TitleItem(BaseModel):
    title: str
