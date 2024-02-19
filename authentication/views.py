import logging
import jwt
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.exceptions import ValidationError
from authentication.models import CustomUser
from authentication.permissions import CustomUserUpdatePermission, IsNotAuthenticated
from authentication.serializers import UserRegistrationSerializer, UserUpdateSerializer, UserPasswordUpdateSerializer
from authentication.authentications import UserAndCompanyAuthentication, UserAuthentication




class UserRegistrationView(APIView):

    authentication_classes = [UserAuthentication]
    permission_classes = [IsNotAuthenticated]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
          serializer.save()
          return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
          return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class VerifyEmail(generics.GenericAPIView):

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
    authentication_classes = (UserAndCompanyAuthentication,)
    
    def post(self, request):
        if request.user.is_authenticated:
            return Response({'error': 'User has already logged in'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        email = request.data.get('email')
        password = request.data.get('password')
        user = CustomUser.objects.get(email=email, password=password)

        if user.DoesNotExist:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user_id': user.id,
            'email': email
        })

class UserUpdateView(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserUpdateSerializer
    authentication_classes = (UserAndCompanyAuthentication,)
    permission_classes = (IsAuthenticated, CustomUserUpdatePermission | IsAdminUser)

class UserPasswordUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UserPasswordUpdateSerializer
    authentication_classes = (UserAndCompanyAuthentication,)
    permission_classes = (CustomUserUpdatePermission,)

class LogoutView(APIView):
    authentication_classes = (UserAndCompanyAuthentication,)
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

