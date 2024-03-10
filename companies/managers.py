from pydantic import BaseModel
from typing import Dict
from bson import ObjectId
from authentication.models import Company, CompanyAndUserRelation
from forum.managers import MongoManager
from forum.settings import DB
from .schemas import Article, CompanyArticles

class NoCompanyProvided(Exception):
    pass

class CompanyDoesNotExist(Exception):
    pass

ARTICLE = 'article'
COMPANY_ARTICLES = 'company_articles'
LIMIT = 10

class ArticlesManager(MongoManager):
    db = DB['Articles']
    types:Dict[str, BaseModel] = {ARTICLE: Article, COMPANY_ARTICLES: CompanyArticles}
    limit = LIMIT
    
    @classmethod
    def get_articles_for_company(cls, company_id, skip=0, **kwargs):
        query = {'company_id': company_id}
        company_articles = cls.get_document(query, **kwargs)
        if not company_articles:
            return []
        articles = company_articles.get('articles', [])
        sorted_articles = articles[::-1]
        skipped_articles = sorted_articles[skip:]
        limited_articles = skipped_articles[0:LIMIT]
        return limited_articles
    
    @classmethod
    def add_article(cls, article:dict):
        company_id = int(article.pop('company_id', None))
        if not company_id:
            raise NoCompanyProvided('No company_id was provided, creating of an article is not possible')
        query = {'company_id': company_id}
        inserted_id = None
        if not cls.check_if_exist(query):
            inserted_id = cls.create_document({'company_id': company_id}, COMPANY_ARTICLES)
        query = {'company_id': company_id} if not inserted_id else {'_id': ObjectId(inserted_id)}
        model = cls.types[ARTICLE]
        v_model = model.model_validate(article)
        update = {'$push': {'articles': v_model.model_dump()}}
        res = cls.update_document(query, update, projection={'articles': 1, '_id': 0})
        return res['articles'][-1]
    
    @classmethod
    def update_article(cls, company_id, art_id, data):
        query = {'company_id': company_id, 'articles.article_id': art_id}
        update = {'$set': {'articles.$.article_text': data['new_content']}}
        res = cls.update_document(query, update)
        return res.acknowledged
    
    @classmethod
    def delete_article(cls, company_id, art_id):
        pass




        

