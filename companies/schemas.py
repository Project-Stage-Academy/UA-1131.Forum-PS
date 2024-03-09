from datetime import datetime
from pydantic import BaseModel, Field
from typing import List


class Article(BaseModel):
    relation: int
    article_text: str
    article_tags: str
    created_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
class CompanyArticles(BaseModel):
    company_id:int
    articles:List[Article] = Field(default=[])
