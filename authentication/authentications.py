import os
from datetime import datetime
from typing import Tuple, Optional
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed, InvalidToken, TokenError
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.utils import get_md5_hash_password
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import Token
from .models import AuthUser, CustomUser, CompaniesAndUsersRelations
from forum.errors import Error


class CustomAuthentication(JWTAuthentication):
    def authenticate(self, request: Request) -> Optional[Tuple[AuthUser, Token]]:
        header = self.get_header(request) # extracting tokens from "Authorisation" field

        # if no tokens provided, empty AuthUser instance is returned with 
        # corresponding error in "error" field
        if header is None:
            return self.user_model(error=Error.NO_HEADER), None 

        raw_token = self.get_raw_token(header) # extracting token, prefix removed

        # same as previous error handling
        if raw_token is None:
            return self.user_model(error=Error.NO_TOKEN), None

        validated_token = self.get_validated_token(raw_token) #extracting payload

        return self.get_user(validated_token), validated_token 

    def get_user(self, validated_token: Token) -> AuthUser:
        if not 'company_id' in validated_token: # if token has not company_id claim in it's payload
            try:
                user_id = validated_token[api_settings.USER_ID_CLAIM] # getting user id
                user_and_company = CustomUser.objects.get(user_id=user_id) # getting user from db by user_id
                user_and_company = user_and_company.get_auth_data() #getting needed fields for AuthUser instance
            except KeyError: # in case of no expected claims in payload
                return self.user_model(error=Error.NO_USER_ID)
            except CustomUser.DoesNotExist: # in case of no such user in db
                return self.user_model(error=Error.USER_NOT_FOUND)
        else:
            try:
                user_id = validated_token[api_settings.USER_ID_CLAIM] 
                company_id = validated_token[api_settings.COMPANY_ID_CLAIM] # getting company id
                # getting joined user and company data from database and extracted all needed values
                user_and_company = CompaniesAndUsersRelations.objects.filter(
                    user_id=user_id, company_id=company_id)[0].values(self.user_model.required_fields) 
            except KeyError:
                return self.user_model(error=Error.NO_USER_OR_COMPANY_ID)
            except CompaniesAndUsersRelations.DoesNotExist:
                return self.user_model(error=Error.NO_RELATED_TO_COMPANY)
        # optional; we pass it as an error with no other data, therefore user is not authorised even if they 
        # already exists in database. this could be removed as we can check the field later in permission or in the view
        if not user_and_company.is_validated: 
            return self.user_model(error=Error.USER_IS_NOT_VALDATED)

        if api_settings.CHECK_REVOKE_TOKEN:
            if validated_token.get(
                api_settings.REVOKE_TOKEN_CLAIM
            ) != get_md5_hash_password(self.user_model.password):
                return self.user_model(
                    error=("The user's password has been changed."), code="password_changed"
                )

        return self.user_model(**user_and_company)

# doing exactly the same as CustomAuthentication, added in case of nedd for additional specific functionality
# could be removed and CustomAuthentication renamed to UserAuthentication instead
class UserAuthentication(CustomAuthentication):
    def authenticate(self, request: Request) -> Tuple[AuthUser, Token] | None:
        return super().authenticate(request)


class UserAndCompanyAuthentication(CustomAuthentication):
    def authenticate(self, request: Request) -> Tuple[AuthUser, Token] | None:
        return super().authenticate(request)
