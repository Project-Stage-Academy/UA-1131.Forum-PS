from celery import shared_task

from .manager import EmailAuthenticationManager, EmailNotificationManager
from .manager import NotificationManager as nm


@shared_task
def send_password_update_notification(user):
    EmailAuthenticationManager.send_password_update_notification(user)


@shared_task
def send_password_reset_notification(email, reset_link):
    EmailAuthenticationManager.send_password_reset_notification(email, reset_link)

@shared_task
def send_article_notification(company_id, users):
    EmailNotificationManager.send_article_notification(company_id, users)


@shared_task
def send_subscribe_notification(company_id):
    EmailNotificationManager.send_subscribe_notification(company_id)


@shared_task
def send_message_notification(user):
    EmailNotificationManager.send_message_notification(user)

@shared_task
def create_notification(data):
    nm.create_notification(data)
