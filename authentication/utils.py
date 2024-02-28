import datetime

import jwt
from django.conf import settings

from django.urls import reverse
import logging
from jwt.utils import force_bytes
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.encoding import force_str
from django.utils.html import strip_tags
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from authentication.models import CustomUser

from django.core.mail import EmailMultiAlternatives, EmailMessage


class Utils:
    @staticmethod
    def email_sender(data):
        email = EmailMessage(subject=data['email_subject'], body=data['email_body'], from_email=data['from_email'],
                             to=(data['to_email'],))
        email.send()

    @staticmethod
    def send_verification_email(domain, user, access_token):
        current_site = domain
        access_token = access_token
        verification_link = reverse('email_verify')
        absurl = f"http://{current_site}{verification_link}?token={str(access_token)}"
        from_email = settings.EMAIL_HOST_USER
        email_body = f'Hello {user.first_name} {user.surname} Use link below to verify your account\n {absurl}'
        data = {'to_email': user.email,
                'from_email': from_email,
                'email_body': email_body,
                'email_subject': "Email verification"}
        Utils.email_sender(data)

    @staticmethod
    def send_password_update_email(user):
        from_email = settings.EMAIL_HOST_USER
        email_body = f'Hello {user.first_name} {user.surname}. This is automatically generated email, your password was successfully changed '
        data = {'to_email': user.email,
                'from_email': from_email,
                'email_body': email_body,
                'email_subject': "Password update"}
        Utils.email_sender(data)

    @staticmethod
    def send_password_reset_email(email, reset_link):
        subject = 'Password Reset'
        html_message = render_to_string('password_reset_email.html', {'reset_link': reset_link})
        plain_message = strip_tags(html_message)
        try:
            email_message = EmailMultiAlternatives(subject, plain_message, settings.EMAIL_HOST_USER, [email])
            email_message.attach_alternative(html_message, "text/html")
            email_message.send()
        except:
            logger = logging.getLogger('email_sending') 
            logger.error(f'Error during email sending to {email}.')   

    @staticmethod
    def generate_token(email, user_id):
        uid = urlsafe_base64_encode(force_bytes(user_id))
        refresh_token_lifetime = settings.SIMPLE_JWT_PASSWORD_RECOVERY['ACCESS_TOKEN_LIFETIME']
        expiration_time = datetime.datetime.utcnow() + refresh_token_lifetime
        expiration_timestamp = int(expiration_time.timestamp())
        jwt_token = jwt.encode({'uid': uid, 'email': email, 'exp': expiration_timestamp},
                               settings.SIMPLE_JWT_PASSWORD_RECOVERY['SIGNING_KEY'],
                               algorithm=settings.SIMPLE_JWT_PASSWORD_RECOVERY['ALGORITHM'])
        return jwt_token

    @staticmethod
    def decode_token(jwt_token):

        try:
            decoded_token = jwt.decode(jwt_token, settings.SECRET_KEY, algorithms=['HS256'])
            uid = decoded_token.get('uid')
            email = decoded_token.get('email')
            exp = decoded_token.get('exp')
            uid = force_str(urlsafe_base64_decode(uid))

            return uid, email, exp
        except (jwt.ExpiredSignatureError, jwt.DecodeError):
            return None, None, None
        
    @staticmethod
    def get_user(uid, email):
        try:
            user = CustomUser.objects.get(pk=uid)
            if user.email == email:
                return user
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            pass
        return None