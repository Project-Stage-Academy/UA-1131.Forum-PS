import pymongo
from typing import Dict
from pydantic import BaseModel, ValidationError
from django.core.mail import EmailMessage
from .settings import EMAIL_HOST_USER


class MongoManager:
    db = None
    types = {}

    @classmethod
    def id_to_string(cls, document):
        """Changes _id field of returned document from ObjectId to string."""
        try:
            document['_id'] = str(document['_id'])
        except (KeyError, TypeError):
            pass
        return document
    
    @classmethod
    def to_list(cls, cursor):
        """Returns the list of objects from the PyMongo cursor."""

        res = []
        for el in cursor:
            res.append(cls.id_to_string(el))
        return res
    
    @classmethod
    def check_if_exist(cls, query):
        res = cls.db.count_documents(query)
        if not res: 
            return False
        return True
    
    @classmethod
    def get_document(cls, query, **kwargs):
        document = cls.db.find_one(query, **kwargs)
        return cls.id_to_string(document)
    
    @classmethod
    def get_documents(cls, query, **kwargs):
        document = cls.db.find(query, **kwargs)
        return cls.to_list(document)
    
    @classmethod
    def create_document(cls, data, key) -> str | None:
        model:BaseModel = cls.types[key]
        validated_model = model.model_validate(data)
        res = cls.db.insert_one(validated_model.model_dump())
        return str(res.inserted_id) if res.acknowledged else None
    
    @classmethod
    def update_document(cls, query, update, **kwargs):
        document = cls.db.find_one_and_update(query, update, return_document=pymongo.ReturnDocument.AFTER, **kwargs)
        return cls.id_to_string(document)

   
    
    

class EmailManager:
    @staticmethod
    def _email_sender(data: Dict):
        email = EmailMessage(subject=data['email_subject'], body=data['email_body'], from_email=data['from_email'],
                             to=(data['to_email'],))
        email.send()

    @staticmethod
    def _data_formatter(email_subject: str, email_body: str, email: str):
        return {
            'email_subject': email_subject,
            'email_body': email_body,
            'from_email': EMAIL_HOST_USER,
            'to_email': email
        }

