from celery import shared_task
from .manager import EmailNotificationManager, EmailAuthenticationManager, NotificationManager as nm


@shared_task
def send_password_update_notification(user):
    EmailAuthenticationManager.send_password_update_notification(user)


@shared_task
def send_password_reset_notification(email, reset_link):
    EmailAuthenticationManager.send_password_reset_notification(email, reset_link)


@shared_task
def create_notification(data):
    nm.create_notification(data)
