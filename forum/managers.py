from rest_framework_simplejwt.exceptions import (AuthenticationFailed,
                                                 TokenError)
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from authentication.models import CustomUser

from .errors import Error


class TokenManager:

    @classmethod
    def generate_access_token_for_user(cls, user: CustomUser) -> AccessToken:
        """Generates token for user"""

        access_token = AccessToken.for_user(user)
        return access_token

    @classmethod
    def generate_refresh_token_for_user(cls, user: CustomUser) -> RefreshToken:
        """Generates token for user"""

        refresh_token = RefreshToken.for_user(user)
        return refresh_token

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
