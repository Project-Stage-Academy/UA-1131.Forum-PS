import logging
import jwt
from django.contrib.auth import authenticate, user_logged_in
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.authentications import UserAuthentication
from authentication.models import CustomUser, CompanyAndUserRelation
from authentication.permissions import (CustomUserUpdatePermission, IsAuthenticated)
from authentication.serializers import (UserRegistrationSerializer, UserUpdateSerializer, UserPasswordUpdateSerializer, PasswordRecoverySerializer)
from forum import settings
from .utils import Utils



class UserRegistrationView(generics.CreateAPIView):
    model = CustomUser
    serializer_class = UserRegistrationSerializer


class VerifyEmail(APIView):

    def get(self, request):
        logger = logging.getLogger('account_update')
        token = request.GET.get('token')
        try:
            payload = AccessToken(token).payload
            user = CustomUser.objects.get(user_id=payload['user_id'])
            user.is_verified = True
            user.save()
            logger.info(
                f"User {user.email} {user.first_name} {user.surname} : email was verified")
            return Response({'email': 'Successfully Verified'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError as e:
            return Response({'email': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError as e:
            return Response({'email': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    authentication_classes = ()
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = CustomUser.get_user(email=email)
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        check = user.check_password(password)
        if not check:
            return Response({'error': 'Wrong password'}, status=status.HTTP_401_UNAUTHORIZED)
        refresh = RefreshToken.for_user(user)
        return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.user_id,
                'email': email
            })
    
class LogoutView(APIView):
    authentication_classes = (UserAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except TokenError as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class RelateUserToCompany(APIView):
    """Binding user to company and inserting linked company's id into token."""
    permission_classes = (IsAuthenticated,)
    
    def post(self, request):
        user_id = request.user.user_id
        company_id = request.data['company_id']
        try:
            relation = CompanyAndUserRelation.get_relation(user_id=user_id, company_id=company_id)
        except CompanyAndUserRelation.DoesNotExist: 
            return Response({'error': 'You have no access to this company.'}, status=status.HTTP_403_FORBIDDEN)
        access_token = CustomUser.generate_company_related_token(request)
        return Response({'access': f"Bearer {access_token}"})
    


class UserUpdateView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer
    authentication_classes = (UserAuthentication,)
    permission_classes = (IsAuthenticated, CustomUserUpdatePermission)


class UserPasswordUpdateView(generics.UpdateAPIView): #doesn't this view double the password reset and recovery functions?
    queryset = CustomUser.objects.all()
    serializer_class = UserPasswordUpdateSerializer
    authentication_classes = (UserAuthentication,)
    permission_classes = (CustomUserUpdatePermission,)


class PasswordRecoveryView(APIView):
    def post(self, request):
        email = request.data.get('email')
        try:
            validate_email(email)
        except ValidationError:
            return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({'error': 'Bad request'}, status=status.HTTP_400_BAD_REQUEST)

        jwt_token = Utils.generate_token(user.email, user.pk)
        reset_link = f"{settings.FRONTEND_URL}/auth/password-reset/{jwt_token}/"
        try:
            Utils.send_password_reset_email.delay(email, reset_link)
        except Exception as e:
            return Response({'error': 'Failed to send email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'message': 'Password reset email sent successfully'}, status=status.HTTP_200_OK)


class PasswordResetView(APIView):              # This view will be rewritten after implementing custom authentication into the main branch.
    serializer_class = PasswordRecoverySerializer

    def post(self, request, jwt_token):
        uid, email, exp = Utils.decode_token(jwt_token)
        if uid and email:
            user = Utils.get_user(uid, email)
            if user is not None:
                serializer = self.serializer_class(instance=user, data=request.data)
                try:
                    serializer.is_valid(raise_exception=True)
                    serializer.save()
                    return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
                except ValidationError as e:   
                    return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': 'Invalid token for password reset'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Invalid token for password reset'}, status=status.HTTP_400_BAD_REQUEST)

