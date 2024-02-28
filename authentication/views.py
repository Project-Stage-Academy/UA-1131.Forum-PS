import logging
import jwt
from authentication.serializers import UserRegistrationSerializer, UserUpdateSerializer, PasswordRecoverySerializer, \
    UserPasswordUpdateSerializer
from authentication.models import CustomUser
from authentication.permissions import CustomUserUpdatePermission, IsAuthenticated
from authentication.authentications import UserAuthentication
from django.contrib.auth import authenticate, user_logged_in
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import status, generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from forum import settings
from .utils import Utils



class UserRegistrationView(APIView):

    def post(self, request):
        print(request.user)
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
          CustomUser.objects.create_user(**serializer.validated_data)
          return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
          return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        user = authenticate(request=request, email=email, password=password)
        if user:
            user_logged_in.send(sender=user.__class__, request=request, user=user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user_id': user.user_id,
                'email': email
            })
        else:
            return Response({'error':'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


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


class PasswordRecoveryAPIView(APIView):
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
            Utils.send_password_reset_email(email, reset_link)
        except Exception as e:
            return Response({'error': 'Failed to send email'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'message': 'Password reset email sent successfully'}, status=status.HTTP_200_OK)



class PasswordResetView(APIView):
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
