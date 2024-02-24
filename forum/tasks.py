from django.core.mail import EmailMessage
from celery import shared_task

@shared_task
def email_sender_celery(data):
    email = EmailMessage(subject=data['email_subject'], body=data['email_body'], from_email=data['from_email'],
                            to=(data['to_email'],))
    email.send()
