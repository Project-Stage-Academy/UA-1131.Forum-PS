import pymongo
from typing import Dict
from pydantic import BaseModel, ValidationError
from django.core.mail import EmailMessage
from .settings import EMAIL_HOST_USER
from rest_framework_simplejwt.exceptions import (AuthenticationFailed,
                                                 TokenError)
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from authentication.models import CustomUser

from .errors import Error


class TokenManager:

    @classmethod
    def generate_access_token_for_user(cls, user: CustomUser) -> str:
        """Generates token for user"""

        access_token = AccessToken.for_user(user)
        return str(access_token)

    @classmethod
    def generate_refresh_token_for_user(cls, user: CustomUser) -> str:
        """Generates token for user"""

        refresh_token = RefreshToken.for_user(user)
        return str(refresh_token)

    @classmethod
    def get_access_payload(cls, token: str) -> dict:
        """Returns payload for access token as dict"""

        decoded_token = cls.__get_decoded_access_token(token)
        return decoded_token.payload

    @classmethod
    def get_refresh_payload(cls, token: str) -> tuple:
        """Returns payload for refresh token as tuple with refresh and access tokens"""

        decoded_tokens = cls.__get_decoded_refresh_token(token)
        return decoded_tokens

    @classmethod
    def __get_decoded_access_token(cls, token) -> AccessToken:
        """Returns decoded token as Dict"""

        try:
            decoded_token = AccessToken(token)
        except TokenError:
            raise AuthenticationFailed(detail=Error.INVALID_TOKEN.msg)
        return decoded_token

    @classmethod
    def __get_decoded_refresh_token(cls, token) -> tuple[RefreshToken, AccessToken]:
        """Returns tuple with decoded tokens as Dict"""

        try:
            decoded_token = RefreshToken(token)
            decoded_access_token = decoded_token.access_token
        except TokenError:
            raise AuthenticationFailed(detail=Error.INVALID_TOKEN.msg)
        return decoded_token, decoded_access_token


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
    
    @classmethod
    def delete_document(cls, query, **kwargs):
        res = cls.db.find_one_and_delete(query, **kwargs)
        return res

    @classmethod
    def delete_from_document(cls, query,delete_part, **kwargs):
        res = cls.db.update_one(query,delete_part, **kwargs)
        if res.modified_count == 0:
            return
        return res
    
    

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

