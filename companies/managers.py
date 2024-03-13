from typing import Any, Dict

from bson import ObjectId
from pydantic import BaseModel
from pymongo import MongoClient

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
    """This manager is responsible for adding, retrieving, redacting and deleting the articles."""
    db:MongoClient = DB['Articles']
    types: Dict[str, BaseModel] = {
        ARTICLE: Article, COMPANY_ARTICLES: CompanyArticles}
    limit:int = LIMIT

    @classmethod
    def get_articles_for_company(cls, company_id:int, skip=0, **kwargs) -> list[dict[str, Any]]:
        """Retrieves articles for the specific company. 
           10 articles is returned, the latest ones first. 
           Required parameters:
             - company_id: id of the company in question;
             - skip: the number of articles we have to skip;
                     this parameter is depending on paginating
                     and is the result of this formula: LIMIT * (page - 1);
        """
        query = {'company_id': company_id}
        company_articles = cls.get_document(query, **kwargs)
        if not company_articles:
            return []
        articles = company_articles.get('articles', [])
        sorted_articles = articles[::-1]
        skipped_articles = sorted_articles[skip:]
        limited_articles = skipped_articles[0:LIMIT]
        for article in limited_articles:
            article['article_id'] = str(article['article_id'])
        return limited_articles

    @classmethod
    def add_article(cls, article: dict) -> dict[str, Any]:
        """Insert article into the database. Takes dict as a paramreter.
           Id of the company in question (company_id) should be inside the dict.
        """
        company_id = int(article.pop('company_id', None))
        if not company_id:
            raise NoCompanyProvided(
                'No company_id was provided, creating of an article is not possible')
        query = {'company_id': company_id}
        inserted_id = None
        if not cls.check_if_exist(query):
            inserted_id = cls.create_document(
                {'company_id': company_id}, COMPANY_ARTICLES)
        query = {'company_id': company_id} if not inserted_id else {
            '_id': ObjectId(inserted_id)}
        model = cls.types[ARTICLE]
        v_model = model.model_validate(article)
        update = {'$push': {'articles': v_model.model_dump()}}
        res = cls.update_document(query, update, projection={
                                  'articles': 1, '_id': 0})
        return cls.id_to_string(res['articles'][-1])

    @classmethod
    def update_article(cls, company_id:int, art_id:str, data:dict) -> dict[str, Any] | None:
        """Updates the article. Required parameters:
           - company_id;
           - article_id;
           - dict with updates;

           Fields that is posiible for updating: article_text, article_title, article_tags.
        """
        query = {'company_id': company_id, 'articles.article_id': art_id}
        possible_fields_to_update = ['article_text', 'article_title', 'article_tags']
        update_fields = {}
        for field in data:
            if field in possible_fields_to_update:
                update_fields[f'articles.$.{field}'] = data[field] 
        update = {'$set': update_fields}
        projection = {'articles.article_id': art_id}
        res = cls.update_document(query, update, projection=projection)
        if res:
            query = [
                {'$match': {'company_id': company_id, 'articles.article_id': art_id}},
                {'$unwind': '$articles'},
                {'$match': {'articles.article_id': art_id}},
            ]
            res = cls.db.aggregate(query)
            return cls.id_to_string(res.next()['articles'])
        return None

    @classmethod
    def delete_article(cls, company_id, art_id) -> bool:
        """Deletes article from the database."""
        query = {'company_id': company_id}
        delete_part = {'$pull': {'articles': {'article_id': art_id}}}
        res = cls.delete_from_document(query, delete_part)
        if not res:
            return False
        return True
