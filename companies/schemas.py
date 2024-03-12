from datetime import datetime
from pydantic import BaseModel, Field
from bson import ObjectId
from typing import List


class Article(BaseModel):
    article_id:str = Field(default_factory=lambda:str(ObjectId()))
    relation: int
    article_title:str
    article_text: str
    article_tags: str
    created_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
class CompanyArticles(BaseModel):
    company_id:int
    articles:List[Article] = Field(default=[])
