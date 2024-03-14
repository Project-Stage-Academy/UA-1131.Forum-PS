import logging

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.authentications import UserAuthentication
from authentication.models import CompanyAndUserRelation, CustomUser
from authentication.permissions import (CustomUserUpdatePermission,
                                        IsAuthenticated)
from authentication.serializers import (PasswordRecoverySerializer,
                                        UserRegistrationSerializer,
                                        UserUpdateSerializer)
from forum import settings
from forum.errors import Error
from forum.managers import TokenManager
from notifications.decorators import extract_notifications_for_user
from notifications.tasks import (send_password_reset_notification,
                                 send_password_update_notification)

class UserRegistrationView(APIView):
    """
        A view for handling user registration requests.

        This view allows users to register by providing necessary information such as email, password, etc.
        Upon receiving a valid registration request, it creates a new user and sends a verification email.

        Request:
            - Method: POST
            - URL: /auth/register/
            - Data Params:
                - email: The email address of the user (required)
                - password: The password for the user (required)
                - other fields: Additional information for user registration (optional)
            - Response:
                - 201 Created: User registered successfully, verification email sent
                - 400 Bad Request: Invalid data provided for user registration
    """
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserRegistrationSerializer

    def post(self, request):
        """Handle POST requests for user registration"""

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = CustomUser.objects.create_user(**serializer.validated_data)
            refresh_token = TokenManager.generate_refresh_token_for_user(user)

            # TO DO: rewrite with EmailManager
            Utils.send_verification_email(get_current_site(request), user, str(refresh_token.access_token))
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifyEmail(APIView):
    """
        A view for handling email verification requests.

        This view allows users to verify their email address by providing a valid JWT access token.

        Request:
            - Method: GET
            - URL: /auth/verify-email/<jwt_token>/
        Response:
            - 200 OK: Email verification successful
            - 400 Bad Request: Invalid or expired token
            - 404 Not Found: User not found
            - 409 Conflict: User's email is already verified
    """
    authentication_classes = ()
    permission_classes = ()

    def get(self, request, jwt_token):
        """Handle GET requests for email verification"""

        payload = TokenManager.get_access_payload(jwt_token)
        user_id = payload.get('user_id')
        if user_id is None:
            return Response({'error': Error.INVALID_TOKEN.msg}, status=Error.INVALID_TOKEN.status)
        try:
            user = CustomUser.get_user(user_id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': Error.USER_NOT_FOUND.msg}, status=Error.USER_NOT_FOUND.status)

        if user.is_verified:
            return Response({'error': Error.USER_ALREADY_VERIFIED.msg}, status=Error.USER_ALREADY_VERIFIED.status)

        user.is_verified = True
        user.save()

        logger = logging.getLogger('account_update')
        logger.info(f"User {user.email} {user.first_name} {user.surname} : email was verified")
        return Response({'email': 'Successfully Verified'}, status=status.HTTP_200_OK)


class LoginView(APIView):
    """
        A view for handling user login requests.

        This view allows users to log in by providing their email and password.

        Request:
            - Method: POST
            - URL: /auth/login/
            - Data Params:
                - email: The email address of the user (required)
                - password: The password of the user (required)
        Response:
            - 200 OK: Login successful
            - 404 Not Found: User not found
            - 401 Unauthorized: Invalid credentials
    """
    authentication_classes = ()
    permission_classes = ()


    @extract_notifications_for_user(related=False)
    def post(self, request):
        """Handle POST requests for user login"""
        email = request.data.get('email')
        password = request.data.get('password')

        try:
            user = CustomUser.get_user(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': Error.USER_NOT_FOUND.msg}, status=Error.USER_NOT_FOUND.status)

        check = user.check_password(password)
        if not check:
            return Response({'error': Error.INVALID_CREDENTIALS.msg}, status=Error.NOT_AUTHENTICATED.status)

        refresh = TokenManager.generate_refresh_token_for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': 'Bearer ' + str(refresh.access_token),
            'user_id': user.user_id
        })


class LogoutView(APIView):
    authentication_classes = (UserAuthentication,)
    permission_classes = (IsAuthenticated,)


class RelateUserToCompany(APIView):
    """
        A view for binding a user to a company and inserting the linked company's id into the token.

        This view requires authentication and permission.

        Request:
            - Method: POST
            - URL: /auth/relate/
            - Data Params:
                - company_id: The id of the company to bind the user to (required)
        Response:
            - 200 OK: User successfully bound to the company
            - 403 Forbidden: User has no access to this company
            - 401 Unauthorized: Token is invalid or expired
    """
    permission_classes = (IsAuthenticated,)

    @extract_notifications_for_user(related=True)
    def post(self, request, pk=None):
        """Handle POST requests for binding a user"""

        user_id = request.user.user_id
        company_id = pk
        try:
            relation = CompanyAndUserRelation.get_relation(user_id=user_id, company_id=company_id)
        except CompanyAndUserRelation.DoesNotExist:
            return Response({'error': 'You have no access to this company.'}, status=status.HTTP_403_FORBIDDEN)

        user_token = request.auth.token
        access_token = TokenManager.generate_company_related_token(company_id=company_id, token=user_token)
        return Response({'access': f"Bearer {access_token}"})


class UserUpdateView(generics.RetrieveUpdateAPIView):
    """
        A view for updating user information.

        This view allows authenticated users to update their email, first name, surname, and phone number.

        Request:
            - Method: PATCH
            - URL: /auth/users/id
            - Data Params:
                - email: The new email address for the user (required)
                - first_name: The new first name for the user (required)
                - surname: The new surname for the user (required)
                - phone_number: The new phone number for the user (required)
        Response:
            - 200 OK: User information updated successfully
            - 400 Bad Request: Invalid data format
    """
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer
    authentication_classes = (UserAuthentication,)
    permission_classes = (IsAuthenticated, CustomUserUpdatePermission)


class LogoutView(APIView):
    """
        A view for handling user logout.

        This view allows authenticated users to log out by providing their refresh token.

        Request:
            - Method: POST
            - URL: /auth/logout/
            - Data Params:
                - refresh_token: The refresh token of the user (required)
        Response:
            - 204 No Content: User logged out successfully
            - 400 Bad Request: No refresh token provided
    """
    authentication_classes = (UserAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        """Handle POST requests for logout the user"""
        refresh_token = request.data.get("refresh_token")
        if refresh_token is None:
            return Response({'error': Error.NO_TOKEN.msg}, status=Error.NO_TOKEN.status)

        decoded_refresh_token, _ = TokenManager.get_refresh_payload(refresh_token)
        decoded_refresh_token.blacklist()
        return Response(status=status.HTTP_204_NO_CONTENT)


class PasswordRecoveryAPIView(APIView):
    """
       A view for handling password recovery requests.

       This view allows users to request a password reset email by providing their email address.
       Upon receiving a valid email address, it sends a password reset email to the user's email address.

       Note:
           This view does not require authentication or permissions.

       Request:
           - Method: POST
           - URL: /auth/password-recovery/
           - Data Params:
               - email: The email address of the user requesting a password reset (required)
           - Response:
               - 200 OK: Password reset email sent successfully
               - 400 Bad Request: Invalid email format
               - 404 Not Found: User does not exist
   """

    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        """Handle POST requests for password recovery"""

        email = request.data.get('email')
        try:
            validate_email(email)
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = CustomUser.get_user(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': Error.USER_NOT_FOUND.msg}, status=Error.USER_NOT_FOUND.status)

        access_token = TokenManager.generate_access_token_for_user(user)
        reset_link = f"{settings.FRONTEND_URL}/auth/password-reset/{access_token}/"

        send_password_reset_notification.delay(email, reset_link)
        return Response({'message': 'Password reset email sent successfully'}, status=status.HTTP_200_OK)



class PasswordResetView(APIView):
    """
        A view for handling password reset requests.

        This view allows users to reset their password by providing a valid JWT access token and a new password.
        Upon receiving a valid request, it resets the user's password and sends a password update email.

        Note:
            This view does not require authentication or permissions.

        Request:
            - Method: POST
            - URL: /auth/password-reset/<jwt_token>/
            - URL: /auth/password-update/
            - Data Params:
                - password: The new password for the user (required)
            - Response:
                - 200 OK: Password reset successfully
                - 400 Bad Request: Invalid token or password format
                - 404 Not found: User not found
    """
    authentication_classes = (UserAuthentication,)
    permission_classes = ()

    serializer_class = PasswordRecoverySerializer

    def post(self, request, jwt_token=None):
        """Handle POST requests for password reset"""

        if request.user.is_authenticated:
            # handle password update
            user_id = request.user.user_id
        else:
            # handle password reset
            payload = TokenManager.get_access_payload(jwt_token)
            user_id = payload.get('user_id')

        if user_id is None:
            return Response({'error': Error.INVALID_TOKEN.msg}, status=Error.INVALID_TOKEN.status)
        try:
            user = CustomUser.get_user(user_id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': Error.USER_NOT_FOUND.msg}, status=Error.USER_NOT_FOUND.status)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            new_password = serializer.validated_data.get("password")
            user.password = make_password(new_password)
            user.save()

            send_password_update_notification.delay(user)
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
