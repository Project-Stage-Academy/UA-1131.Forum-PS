from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import InvalidToken, AuthenticationFailed
from .errors import Error


class TokenManager:

    @classmethod
    def generate_token_for_user(cls, user) -> str:
        """Generates token for user"""

        access_token = AccessToken.for_user(user)
        return str(access_token)

    @classmethod
    def generate_refresh_token_for_user(cls, user) -> str:
        """Generates token for user"""

        refresh_token = RefreshToken.for_user(user)
        return str(refresh_token)

    @classmethod
    def get_payload(cls, token) -> dict:
        """Returns payload for token"""

        decoded_token = cls.__get_decoded_token(token)
        return decoded_token.payload

    @classmethod
    def __get_decoded_token(cls, token) -> AccessToken:
        """Returns decoded token as Dict"""

        try:
            decoded_token = AccessToken(token)
        except InvalidToken:
            raise AuthenticationFailed(detail=Error.INVALID_TOKEN.msg)
        return decoded_token
