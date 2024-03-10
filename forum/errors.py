from rest_framework import status


class Error:
    """Pre-formatted errors for easier handling"""

    class NO_HEADER:
        msg = "No authentication header provided"
        status = status.HTTP_401_UNAUTHORIZED

    class NO_TOKEN:
        msg = "No token provided"
        status = status.HTTP_400_BAD_REQUEST

    class NO_COMPANY_FOUND:
        msg = "No company found"
        status = status.HTTP_404_NOT_FOUND

    class INVALID_TOKEN:
        msg = "Token is invalid or expired"
        status = status.HTTP_401_UNAUTHORIZED


    class NO_USER_ID:
        msg = "Token contained no recognizable user identification"
        status = status.HTTP_401_UNAUTHORIZED

    class USER_IS_NOT_VERIFIED:
        msg = "User is not verified"
        status = status.HTTP_401_UNAUTHORIZED

    class NOT_AUTHENTICATED:
        msg = "User is not authenticated"
        status = status.HTTP_401_UNAUTHORIZED

    class NOT_INVESTOR:
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
        msg = "User has not representative position"
        status = status.HTTP_403_FORBIDDEN

    class NO_CREDENTIALS:
        msg = "No credentials were provided"
        status = status.HTTP_400_BAD_REQUEST

    class INVALID_ARTICLE:
        msg = "Invalid article data provided"
        status = status.HTTP_400_BAD_REQUEST   