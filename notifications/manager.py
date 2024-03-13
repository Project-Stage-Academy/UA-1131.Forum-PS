from datetime import datetime, timedelta
from typing import Dict, List

import pymongo
from bson import ObjectId
from django.core.mail import EmailMessage, EmailMultiAlternatives
from django.template.loader import render_to_string
from pydantic import BaseModel, Field, ValidationError

from companies.models import Subscription
from forum.managers import MongoManager
from forum.settings import DB, EMAIL_HOST_USER

UPDATE = 'update'
MESSAGE = 'message'
SUBSCRIPTION = 'subscription'


class AlreadyExist(Exception):
    pass


class NotificationNotFound(Exception):
    pass


class InvalidData(Exception):
    pass


class AlreadyViewed(Exception):
    pass


class Viewed(BaseModel):
    """Model for storing users that has viewed the notification."""
    user_id: int
    viewed_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


class Notification(BaseModel):
    """Parent class for notification classes."""
    created_at: str = Field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    concerned_users: List = Field(default=[])
    viewed_by: List[Dict[str, Viewed]] = Field(default=[])
    event_id: int


class UpdateNotification(Notification):
    """Model for update notification"""
    company_id: int
    event_id: str
    type: str = Field(default=UPDATE, frozen=True)


class MessageNotification(Notification):
    """Model for message notification"""
    type: str = Field(default=MESSAGE, frozen=True)


class SubscriptionNotification(Notification):
    """Model for subscription notification"""
    type: str = Field(default=SUBSCRIPTION, frozen=True)


class NotificationManager(MongoManager):
    """
    NotificationManager is responsible for database interactions, including data validating  
    and serializing, errors handling and retrieved data formatting. To register your model 
    in manager you have to include it in types collection, with type as a key and model
    as a value
    """

    db = DB['Notification']
    types = {UPDATE: UpdateNotification,
             MESSAGE: MessageNotification,
             SUBSCRIPTION: SubscriptionNotification}

    @classmethod
    def get_notification_by_query(cls, query, **kwargs):
        """Extracting the single document from database filtered by given query."""

        notification = cls.get_document(query, **kwargs)
        if not notification:
            raise NotificationNotFound("Notification not found")
        return notification

    @classmethod
    def get_notifications_by_query(cls, query, err=None):
        """Extracting the multiple documents from database filtered by given query."""

        err = "There is no notifications that satisfy given conditions" if not err else err
        if not cls.check_if_exist(query):
            raise NotificationNotFound(err)
        notifications = cls.get_and_sort_documents(query, sort_options=('created_at', pymongo.ASCENDING), projection=['event_id', 'type'])
        if not notifications:
            raise NotificationNotFound(
                "Notifications not found, perhaps due to the connection error.")
        return notifications

    @classmethod
    def delete_notification_by_query(cls, query, **kwargs):
        """Delete notification that matches given conditions."""

        notification = cls.delete_document(query, **kwargs)
        if not notification:
            raise NotificationNotFound("Notification not found")
        return notification

    @classmethod
    def delete_old_notifications(cls):
        """Deleted notifications that are 30 days older than current date."""

        date = datetime.now() - timedelta(days=30)
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        query = {"created_at": {"$lt": date}}
        res = cls.delete_documents(query)
        return res

    @classmethod
    def create_notification(cls, data):
        """
        Creating and stores into the database notification with id of the event that triggered 
        the notification's creation (for instance update_id or chat_id) and other defined in the model
        information. Data should include type and event_id. 
        """
        type_ = data.pop('type')
        event_id = data['event_id']
        query = {'event_id': event_id}
        if cls.check_if_exist(query):
            raise AlreadyExist(
                f"Notification for {type_} with EVENT_ID {event_id} already exists.")
        res = cls.create_document(data, type_)
        return res

    @classmethod
    def create_notifications(cls, data: list):
        """Creating notifications from the array of data."""

        res = []
        for nf in data:
            try:
                id_ = cls.create_notification(nf)
                res.append(id_)
            except AlreadyExist:
                continue
        return res

    @classmethod
    def extract_notifications_for_user(cls, u_id):
        """Extracting all the notifications that are regarded to user."""

        query = {'concerned_users': u_id}
        err_msg = f"There is no notifications for the user."
        return cls.get_notifications_by_query(query, err=err_msg)

    @classmethod
    def extract_notifications_by_type(cls, type):
        """Extracting all notifications of given type."""

        query = {'type': type}
        err_msg = f"There is no notifications of type <{type}>."
        return cls.get_notifications_by_query(query, err=err_msg)

    @classmethod
    def store_viewed_user(cls, nf_id, u_id):
        """
        This method stores user id in viewed_by field along with the time of viewing.
        """
        query = {'$and': [{'_id': ObjectId(nf_id)}, {'concerned_users': u_id}]}
        notification = cls.get_notification_by_query(query)
        if any(viewed['user_id'] == u_id for viewed in notification.get('viewed_by', [])):
            raise AlreadyViewed(
                f"User with ID {u_id} already has viewed this notification")
        try:
            viewed = Viewed.model_validate({'user_id': u_id})
        except ValidationError as e:
            raise InvalidData(str(e)) from e
        update = {'$push': {'viewed_by': viewed.model_dump()}}
        notification = cls.update_document(
            query, update, return_document=pymongo.ReturnDocument.AFTER)
        if not notification:
            raise NotificationNotFound(
                "Notification not found, perhaps due the connection error.")
        return notification


class EmailManager:
    """
       EmailManager is responsible for sending emails and formatting email data.

       Methods:
           - _email_sender(data: Dict): Sends a basic email.
           - _email_alternative_sender(data: Dict): Sends an HTML email with alternative content.
           - _data_formatter(email_subject: str, email_body: str, email: str): Formats email data.
           - _email_subscription_filter(company): Filters email subscriptions based on company receiver.

       Note:
           This class utilizes Django's EmailMessage and EmailMultiAlternatives classes for sending emails.
           It also interacts with the Subscription model to filter email subscriptions based on company.
   """

    @staticmethod
    def _email_sender(data: Dict):
        email = EmailMessage(subject=data['email_subject'], body=data['email_body'], from_email=data['from_email'],
                             to=(data['to_email'],))
        email.send()

    @staticmethod
    def _email_alternative_sender(data: Dict):
        email_message = EmailMultiAlternatives(subject=data['email_subject'], body=data['email_body'],
                                               from_email=data['from_email'], to=(data['to_email'],))
        email_message.content_subtype = "html"
        email_message.send()

    @staticmethod
    def _data_formatter(email_subject: str, email_body: str, email: str):
        return {
            'email_subject': email_subject,
            'email_body': email_body,
            'from_email': EMAIL_HOST_USER,
            'to_email': email
        }

    @staticmethod
    def _email_subscription_filter(company):
        queryset = Subscription.objects.filter(company=company, get_email_newsletter=True)
        emails = [record.investor.email for record in queryset]
        return emails


class EmailAuthenticationManager(EmailManager):
    """
        EmailAuthenticationManager extends EmailManager for authentication-related email notifications.

        Methods:
            - send_password_reset_notification(email, reset_link): Sends a password reset notification email.
            - send_password_update_notification(user): Sends a password update notification email.
    """
    @classmethod
    def send_password_reset_notification(cls, email, reset_link):
        email_subject = 'Password Reset'
        html_content = render_to_string('password_reset_email.html', {'reset_link': reset_link})
        data = cls._data_formatter(email_subject, html_content, email)
        cls._email_alternative_sender(data)

    @classmethod
    def send_password_update_notification(cls, user):
        email_subject = 'Password update'
        email_body = (f'Dear {user.first_name} {user.surname}.'
                      ' This is automatically generated email, your password was successfully changed')
        data = cls._data_formatter(email_subject=email_subject, email_body=email_body, email=user.email)
        cls._email_sender(data)


class EmailNotificationManager(EmailManager):
    """
        EmailNotificationManager extends EmailManager for sending notification emails.

        Methods:
        - send_subscribe_notification(company, emails_to_send=None): Sends a notification email about a new subscriber.
    """

    @classmethod
    def send_subscribe_notification(cls, company, emails_to_send=None):
        if emails_to_send is None:
            emails_to_send = cls._email_subscription_filter(company=company)
        for email in emails_to_send:
            email_subject = 'You have a new subscriber'
            email_body = 'Dear user, we would like to inform you about a new subscriber'
            data = cls._data_formatter(email_subject=email_subject, email_body=email_body, email=email)
            cls._email_sender(data)
