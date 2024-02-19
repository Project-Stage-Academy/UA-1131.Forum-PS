from rest_framework import status
# pre-formatted errors for easier handling
class Error:
    NO_HEADER = {'msg': "No authentication header provided",
                  'status': status.HTTP_401_UNAUTHORIZED}
    NO_TOKEN = {'msg': "No token provided",
                'status': status.HTTP_400_BAD_REQUEST}
    NO_USER_ID = {'msg': "Token contained no recognizable user identification",
                  'status': status.HTTP_401_UNAUTHORIZED}
    USER_IS_NOT_VALDATED = {'msg': "User is not validated",
                            'status': status.HTTP_401_UNAUTHORIZED}
    USER_NOT_FOUND = {'msg': "User not found",
                      'status': status.HTTP_403_FORBIDDEN}
    NO_USER_OR_COMPANY_ID = {'msg': "Token contained no recognizable user or company identification",
                             'status': status.HTTP_401_UNAUTHORIZED}
    NO_RELATED_TO_COMPANY = {'msg': "User isn`t related to any company",
                             'status': status.HTTP_403_FORBIDDEN}