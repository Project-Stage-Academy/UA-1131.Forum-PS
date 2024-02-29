import logging
import jwt
from django.conf import settings
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import generics
from rest_framework import status
from rest_framework.views import APIView
from authentication.authentications import UserAuthentication
from authentication.models import CustomUser
from authentication.permissions import (CustomUserUpdatePermission, IsAuthenticated)
from authentication.serializers import (UserRegistrationSerializer, UserUpdateSerializer, UserPasswordUpdateSerializer)
from forum import settings


class UserRegistrationView(generics.CreateAPIView):
    model = CustomUser
    serializer_class = UserRegistrationSerializer


class VerifyEmail(APIView):

    def get(self, request):
        logger = logging.getLogger('account_update')
        token = request.GET.get('token')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = CustomUser.objects.get(id=payload['user_id'])
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

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = CustomUser.get_user(email=email)
        check = user.check_password(password)
        if not check:
            return Response({'error': 'Wrong password'}, status=status.HTTP_401_UNAUTHORIZED)
        if not user:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.user_id,
                'email': email
            })


class UserUpdateView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer
    authentication_classes = (UserAuthentication,)
    permission_classes = (IsAuthenticated, CustomUserUpdatePermission)


class UserPasswordUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserPasswordUpdateSerializer
    authentication_classes = (UserAuthentication,)
    permission_classes = (CustomUserUpdatePermission,)


class LogoutView(APIView):
    authentication_classes = (UserAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            print("Exception", e)
            return Response(status=status.HTTP_400_BAD_REQUEST)
