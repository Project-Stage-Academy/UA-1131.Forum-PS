import logging
from channels.auth import AuthMiddlewareStack
from django.conf import settings
from channels.db import database_sync_to_async
from django.db import close_old_connections
from rest_framework import status
from rest_framework.response import Response
from jwt import decode as jwt_decode
from authentication.models import CustomUser


class JWTAuthMiddleware:
    """ Checking JWT token for the user"""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        close_old_connections()
        try:
            headers = dict(scope['headers'])
            token_header = headers.get(b'authorization', b'').decode("utf-8")
            if not token_header.startswith("Bearer "):
                raise ValueError(f"Invalid Authorization header format {token_header}")
            jwt_token = token_header.split("Bearer ")[-1]
            if jwt_token:
                jwt_payload = self.get_payload(jwt_token)
                user_credentials = self.get_user_credentials(jwt_payload)
                user = await self.get_logged_in_user(user_credentials)
                scope['user'] = user
            else:
                logger = logging.getLogger('websocket_jwt_error')
                logger.error("Troubles with provided jwt token")
                return Response({'error': "Troubles with provided jwt token"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger = logging.getLogger('websocket_jwt_error')
            logger.error(e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return await self.app(scope, receive, send)

    def get_payload(self, jwt_token):
        payload = jwt_decode(
            jwt_token, settings.SECRET_KEY, algorithms=["HS256"])

        return payload

    def get_user_credentials(self, payload):
        """
        method to get user credentials from jwt token payload.
        defaults to user id.
        """
        user_id = payload.get('user_id')
        if user_id is None:
            raise ValueError("user_id is missing in JWT payload")
        return user_id

    async def get_logged_in_user(self, user_id):
        user = await self.get_user(user_id)
        return user

    @database_sync_to_async
    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(user_id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': "Wrong user id"}, status=status.HTTP_400_BAD_REQUEST)


def JWTAuthMiddlewareStack(app):
    return JWTAuthMiddleware(AuthMiddlewareStack(app))
