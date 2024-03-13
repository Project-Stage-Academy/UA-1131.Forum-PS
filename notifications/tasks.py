from celery import shared_task
from .manager import EmailNotificationManager, EmailAuthenticationManager, NotificationManager as nm


@shared_task
def send_password_update_notification(user):
    EmailAuthenticationManager.send_password_update_notification(user)


@shared_task
def send_password_reset_notification(email, reset_link):
    EmailAuthenticationManager.send_password_reset_notification(email, reset_link)

@shared_task
def send_article_notification(company_id, emails_to_send):
    EmailNotificationManager.send_article_notification(company_id, emails_to_send)


@shared_task
def send_subscribe_notification(emails_to_send):
    EmailNotificationManager.send_subscribe_notification(emails_to_send)


@shared_task
def send_message_notification(user_email):
    EmailNotificationManager.send_message_notification(user_email)

@shared_task
def create_notification(data):
    nm.create_notification(data)
