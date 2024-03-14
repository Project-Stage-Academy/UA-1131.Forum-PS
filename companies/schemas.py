from datetime import datetime
from typing import List

from bson import ObjectId
from pydantic import BaseModel, Field


class Article(BaseModel):
    article_id: str = Field(default_factory=lambda: str(ObjectId()))
    relation: int
    article_title: str
    article_text: str
    article_tags: str
    created_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class CompanyArticles(BaseModel):
    company_id: int
    articles: List[Article] = Field(default=[])
