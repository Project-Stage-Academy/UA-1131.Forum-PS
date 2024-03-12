from rest_framework import status
from rest_framework.response import Response


class Error:
    """Pre-formatted errors for easier handling"""

    class BaseError:
        msg = None
        status = None

        @classmethod
        def response(cls):
            return Response({'error': cls.msg}, status=cls.status)

    class NO_HEADER(BaseError):
        msg = "No authentication header provided"
        status = status.HTTP_401_UNAUTHORIZED

    class NO_TOKEN(BaseError):
        msg = "No token provided"
        status = status.HTTP_400_BAD_REQUEST

    class NO_COMPANY_FOUND(BaseError):
        msg = "No company found"
        status = status.HTTP_404_NOT_FOUND

    class INVALID_TOKEN(BaseError):
        msg = "Token is invalid or expired"
        status = status.HTTP_401_UNAUTHORIZED

    class NO_USER_ID(BaseError):
        msg = "Token contained no recognizable user identification"
        status = status.HTTP_401_UNAUTHORIZED

    class USER_IS_NOT_VERIFIED(BaseError):
        msg = "User is not verified"
        status = status.HTTP_400_BAD_REQUEST

    class USER_ALREADY_VERIFIED(BaseError):
        msg = "User is already verified"
        status = status.HTTP_409_CONFLICT

    class NOT_AUTHENTICATED(BaseError):
        msg = "User is not authenticated"
        status = status.HTTP_401_UNAUTHORIZED

    class INVALID_CREDENTIALS:
        msg = "Invalid credentials"
        status = status.HTTP_401_UNAUTHORIZED

    class NOT_INVESTOR(BaseError):
        msg = "Related company is not of investment"
        status = status.HTTP_403_FORBIDDEN

    class NOT_STARTUP:
        msg = "Related company is not of startup"
        status = status.HTTP_403_FORBIDDEN

    class USER_NOT_FOUND:
        msg = "User not found"
        status = status.HTTP_404_NOT_FOUND

    class NO_USER_OR_COMPANY_ID:
        msg = "Token contained no recognizable user or company identification"
        status = status.HTTP_401_UNAUTHORIZED

    class NO_RELATED_TO_COMPANY:
        msg = "User isn't related to any company"
        status = status.HTTP_403_FORBIDDEN

    class NO_COMPANY_TYPE:
        msg = "No company type is recognised"
        status = status.HTTP_401_UNAUTHORIZED

    class ALREADY_LOGGED_IN:
        msg = "User is already logged in"
        status = status.HTTP_403_FORBIDDEN

    class WRONG_PASSWORD:
        msg = "Password is wrong"
        status = status.HTTP_401_UNAUTHORIZED

    class NOT_FOUNDER:
        msg = "User has not founder position"
        status = status.HTTP_403_FORBIDDEN

    class NOT_REPRESENTATIVE:
        msg = "User has not founder position"
        status = status.HTTP_403_FORBIDDEN

    class NO_CREDENTIALS(BaseError):
        msg = "No credentials were provided"
        status = status.HTTP_400_BAD_REQUEST

    class SUBSCRIPTION_NOT_FOUND(BaseError):
        msg = "Subscription not found"
        status = status.HTTP_404_NOT_FOUND

    class NO_COMPANY_ID(BaseError):
        msg = "Company ID required"
        status = status.HTTP_400_BAD_REQUEST

