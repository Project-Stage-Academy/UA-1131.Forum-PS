from typing import Tuple, Optional
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.utils import get_md5_hash_password
from rest_framework_simplejwt.tokens import Token
from .models import AuthUser, CustomUser, CompaniesAndUsersRelations
from forum.errors import Error


class UserAuthentication(JWTAuthentication):
    """
    This authentication class is default for all the views. It decodes recieved request token and checks if user 
    exists in database; if token contains company related credentials, it retrieves and combines information from
    related company.
    This authentification always returns AuthUser instance (request.user). If no user found or other error occures
    the empty AuthUser instance is returned with error written in related AuthUser field. 
    
    """
    def error_handling(self, error):
        return self.user_model(error=error) 
    
    def authenticate(self, request: Request) -> Optional[Tuple[AuthUser, Token]]:
        """
        This method gets and decodes token from request, then retrieves user with given in the token credentials 
        from the database and returns it as a request.user.

        """
        header = self.get_header(request) 

        if header is None:
            return self.error_handling(Error.NO_HEADER), None

        raw_token = self.get_raw_token(header) 
        if raw_token is None:
            return self.error_handling(Error.NO_TOKEN), None

        validated_token = self.get_validated_token(raw_token) 
        return self.get_user(validated_token), validated_token 

    def get_user(self, validated_token: Token) -> AuthUser:
        """
        This method retrieves the user from the database. If company credentials are present in token,
        company information is added. 

        """
        if not 'company_id' in validated_token:
            try:
                user_id = validated_token[api_settings.USER_ID_CLAIM] 
                user_and_company = CustomUser.get_user(user_id=user_id)
                user_and_company = user_and_company.get_auth_data() 
            except KeyError: 
                return self.error_handling(Error.NO_USER_ID)
            except CustomUser.DoesNotExist: 
                return self.error_handling(Error.USER_NOT_FOUND)
        else:
            try:
                user_id = validated_token[api_settings.USER_ID_CLAIM] 
                company_id = validated_token[api_settings.COMPANY_ID_CLAIM] 
                user_and_company = CompaniesAndUsersRelations.get_relation(user_id, company_id) 
            except KeyError:
                return self.error_handling(Error.NO_USER_OR_COMPANY_ID)
            except CompaniesAndUsersRelations.DoesNotExist:
                return self.error_handling(Error.NO_RELATED_TO_COMPANY)
            
        if not user_and_company.is_validated: 
            return self.error_handling(Error.USER_IS_NOT_VALDATED)

        if api_settings.CHECK_REVOKE_TOKEN:
            if validated_token.get(
                api_settings.REVOKE_TOKEN_CLAIM
            ) != get_md5_hash_password(self.user_model.password):
                return self.error_handling(Error.WRONG_PASSWORD)

        return self.user_model(**user_and_company)

