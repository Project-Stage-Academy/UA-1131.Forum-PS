from django.conf import settings
from django.core.mail import EmailMessage
from django.urls import reverse


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
