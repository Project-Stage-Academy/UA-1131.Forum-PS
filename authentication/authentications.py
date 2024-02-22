from typing import Tuple, Optional
from rest_framework.request import Request
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.utils import get_md5_hash_password
from rest_framework_simplejwt.tokens import Token
from .models import AuthUser, CustomUser, CompaniesAndUsersRelations
from forum.errors import Error


class UserAuthentication(JWTAuthentication):
    def authenticate(self, request: Request) -> Optional[Tuple[AuthUser, Token]]:
        header = self.get_header(request) 

        if header is None:
            return self.user_model(error=Error.NO_HEADER), None 

        raw_token = self.get_raw_token(header) 
        if raw_token is None:
            return self.user_model(error=Error.NO_TOKEN), None

        validated_token = self.get_validated_token(raw_token) 
        return self.get_user(validated_token), validated_token 

    def get_user(self, validated_token: Token) -> AuthUser:
        if not 'company_id' in validated_token:
            try:
                user_id = validated_token[api_settings.USER_ID_CLAIM] 
                user_and_company = CustomUser.objects.get(user_id=user_id) 
                user_and_company = user_and_company.get_auth_data() 
            except KeyError: 
                return self.user_model(error=Error.NO_USER_ID)
            except CustomUser.DoesNotExist: 
                return self.user_model(error=Error.USER_NOT_FOUND)
        else:
            try:
                user_id = validated_token[api_settings.USER_ID_CLAIM] 
                company_id = validated_token[api_settings.COMPANY_ID_CLAIM] 
                user_and_company = CompaniesAndUsersRelations.objects.filter(
                    user_id=user_id, company_id=company_id)[0].values(self.user_model.required_fields) 
            except KeyError:
                return self.user_model(error=Error.NO_USER_OR_COMPANY_ID)
            except CompaniesAndUsersRelations.DoesNotExist:
                return self.user_model(error=Error.NO_RELATED_TO_COMPANY)
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

