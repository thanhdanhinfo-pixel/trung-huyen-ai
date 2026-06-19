from pydantic import BaseModel
from typing import List


class Knowledge(BaseModel):
    title: str
    content: str

    type: str = "Principle"

    tags: List[str] = []

    author: str = "Trung Huyền"

    version: str = "1.0"
