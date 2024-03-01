from celery import shared_task
from .manager import EmailNotificationManager, NotificationManager as nm


@shared_task
def send_update_email(company):
    EmailNotificationManager.send_update_notification(company=company)


@shared_task
def send_message_email(message, company):
    EmailNotificationManager.send_message_notification(message=message, company=company)


@shared_task
def send_subscribe_email(company):
    EmailNotificationManager.send_subscribe_notification(company=company)

@shared_task
def create_notification(data):
    nm.create_notification(data)
