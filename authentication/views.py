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

from .utils import Utils


class UserRegistrationView(APIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserRegistrationSerializer

    def post(self, request):

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
    authentication_classes = (UserAuthentication,)
    permission_classes = ()

    def get(self, request, jwt_token):
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
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
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
            'access': str(refresh.access_token),
            'user_id': user.user_id,
            'email': email
        })


class RelateUserToCompany(APIView):
    """Binding user to company and inserting linked company's id into token."""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user_id = request.user.user_id
        company_id = request.data['company_id']
        relation = CompanyAndUserRelation.get_relation(user_id, company_id)
        if not relation: 
            return Response({'error': 'You have no access to this company.'}, status=status.HTTP_403_FORBIDDEN)
        access_token = CustomUser.generate_company_related_token(request)
        return Response({'access': f"Bearer {access_token}"})


class UserUpdateView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer
    authentication_classes = (UserAuthentication,)
    permission_classes = (IsAuthenticated, CustomUserUpdatePermission)



class LogoutView(APIView):
    authentication_classes = (UserAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
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

        Utils.send_password_reset_email(email, reset_link)  # TO DO: REWRITE WITH DECORATORS
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
            - Data Params:
                - password: The new password for the user (required)
            - Response:
                - 200 OK: Password reset successfully
                - 400 Bad Request: Invalid token or password format
    """
    authentication_classes = ()
    permission_classes = ()

    serializer_class = PasswordRecoverySerializer

    def post(self, request, jwt_token):
        """Handle POST requests for password reset"""

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
            Utils.send_password_update_email(user)  # TO DO: REWRITE WITH DECORATORS
            return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
