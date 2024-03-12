from typing import Optional, Tuple

from rest_framework.exceptions import NotAuthenticated
from rest_framework.request import Request

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import Token
from rest_framework_simplejwt.utils import get_md5_hash_password

from forum.errors import Error

from .models import CompanyAndUserRelation, CustomUser


class UserAuthentication(JWTAuthentication):
    """
    This authentication class is default for all the views. It decodes recieved request token and checks if user 
    exists in database; if token contains company related credentials, it retrieves and combines information from
    related company.
    This authentification always returns AuthUser instance (request.user). If no user found or other error occures
    the empty AuthUser instance is returned with error written in related AuthUser field. 
    
    """
    
    def authenticate(self, request: Request) -> Optional[Tuple[CustomUser, Token]]:
        """
        This method gets and decodes token from request, then retrieves user with given in the token credentials 
        from the database and returns it as a request.user.

        """
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header) 
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token) 
        return self.get_user(validated_token), validated_token 

    def get_user(self, validated_token: Token) -> CustomUser:
        """
        This method retrieves the user from the database. If company credentials are present in token,
        company information is added. 

        """
        if not 'company_id' in validated_token:
            try:
                user_id = validated_token[api_settings.USER_ID_CLAIM] 
                user = CustomUser.get_user(user_id=user_id)
            except KeyError: 
                raise NotAuthenticated(detail=Error.NO_USER_ID.msg, status_code=Error.NO_USER_ID.status)
            except CustomUser.DoesNotExist: 
                raise NotAuthenticated(detail=Error.USER_NOT_FOUND.msg, status_code=Error.USER_NOT_FOUND.status)
        else:
            try:
                user_id = validated_token[api_settings.USER_ID_CLAIM] 
                company_id = validated_token['company_id'] 
                user = CustomUser.get_user(user_id=user_id)
                relation = CompanyAndUserRelation.get_relation(user_id=user_id, company_id=company_id)
                user.company = relation.company_id.__dict__
                user.position = relation.position
                user.relation_id = relation.relation_id
            except KeyError:
                raise NotAuthenticated(detail=Error.NO_USER_OR_COMPANY_ID.msg)
            

        if api_settings.CHECK_REVOKE_TOKEN:
            if validated_token.get(
                api_settings.REVOKE_TOKEN_CLAIM
            ) != get_md5_hash_password(self.user_model.password):
                raise NotAuthenticated(detail=Error.WRONG_PASSWORD.msg)
            
        user.is_authenticated = True
        return user

