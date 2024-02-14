import datetime

import jwt
from django.contrib.auth.hashers import make_password
from authentication.models import CustomUser
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import View
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from forum import settings
from validation.serializers import  CustomValidationSerializer
from .serializers import PasswordRecoverySerializer


class PasswordRecoveryAPIView(APIView):
    def post(self, request):

        serializer = PasswordRecoverySerializer(data=request.data)
        if serializer.is_valid():

            email = serializer.validated_data.get('email')
            try:
                user = CustomUser.objects.get(email=email)

            except CustomUser.DoesNotExist:
                return Response({'error': 'User with this email does not exist'}, status=404)

            jwt_token = self._generate_token(user.email, user.pk)


            reset_link = f"{settings.FRONTEND_URL}/recovery/password-reset/{jwt_token}/"
            try:
                self._send_password_reset_email(email, reset_link)
            except Exception as e:
                return Response({'error': 'Failed to send email'}, status=500)

            return Response({'message': 'Password reset email sent successfully'})
        else:
            return Response(serializer.errors, status=400)

    def _generate_token(self, email, user_id):
        uid = urlsafe_base64_encode(force_bytes(user_id))
        refresh_token_lifetime = settings.SIMPLE_JWT_PASSWORD_RECOVERY['ACCESS_TOKEN_LIFETIME']
        expiration_time = datetime.datetime.utcnow() + refresh_token_lifetime
        expiration_timestamp = int(expiration_time.timestamp())
        jwt_token = jwt.encode({'uid': uid, 'email': email, 'exp': expiration_timestamp},
                               settings.SIMPLE_JWT_PASSWORD_RECOVERY['SIGNING_KEY'], algorithm=settings.SIMPLE_JWT_PASSWORD_RECOVERY['ALGORITHM'])
        return jwt_token

    def _send_password_reset_email(self, email, reset_link):
        subject = 'Password Reset'
        html_message = render_to_string('password_reset_email.html', {'reset_link': reset_link})
        plain_message = strip_tags(html_message)
        email_message = EmailMultiAlternatives(subject, plain_message, settings.EMAIL_HOST_USER, [email])
        email_message.attach_alternative(html_message, "text/html")
        email_message.send()


class PasswordResetView(APIView, CustomValidationSerializer):

    def get(self, request, jwt_token):
        uid, email, exp = self._decode_token(jwt_token)
        if isinstance(uid, JsonResponse):
            return uid

        user = self._get_user(uid, email)
        if user is not None:
            return render(request, 'reset_password_form.html', {'jwt_token': jwt_token})
        else:
            return JsonResponse({'error': 'Invalid token for password reset'}, status=400)

    def post(self, request, jwt_token):
        uid, email, exp = self._decode_token(jwt_token)

        if isinstance(uid, JsonResponse):
            return uid

        user = self._get_user(uid, email)
        if user is not None:
            password1 = request.POST.get('new_password')
            password2 = request.POST.get('confirm_password')

            if password1 != password2:
                return JsonResponse({'error': 'Passwords do not match'}, status=400)
            try:
                self.validation_password(password1,email,user.first_name,user.surname)
            except ValidationError as e:
                raise ValidationError({"password": e.detail})

            user.password = make_password(password1)
            user.save()

            return render(request, 'password_reset_done.html')
        else:
            return JsonResponse({'error': 'Invalid token for password reset'}, status=400)

    def _decode_token(self, jwt_token):
        try:

            decoded_token = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])

            uid = decoded_token.get('uid')
            email = decoded_token.get('email')
            exp = decoded_token.get('exp')

            uid = force_str(urlsafe_base64_decode(uid))
            return uid, email, exp
        except jwt.ExpiredSignatureError:
            return None, None, None

    def _get_user(self, uid, email):
        try:
            user = CustomUser.objects.get(pk=uid)
            if user.email == email:
                return user
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            pass
        return None
