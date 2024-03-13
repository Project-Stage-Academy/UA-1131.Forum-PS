from functools import wraps

from authentication.models import CompanyAndUserRelation
from companies.models import Subscription

from .manager import MESSAGE, SUBSCRIPTION, UPDATE
from .manager import NotificationManager as nm
from .manager import NotificationNotFound
from .tasks import create_notification


def get_user_id(request, response, related):
    id_key = 'user_id' if not related else 'relation_id'
    try:
        user_id = response.data.pop(id_key)
    except KeyError:
        try:
            user_id = request.user.__getattribute__(id_key)
        except AttributeError:
            return None
    return user_id, response


def extract_data_for_message(request, response):
    data = {}
    data['type'] = MESSAGE
    data['event_id'] = response.data['inserted_id']
    data['conсerned_users'] = [request.data.get('receiver_id')]
    return data, response


def extract_data_for_subscription(request, response):
    data = {}
    data['type'] = MESSAGE
    data['event_id'] = response.data.pop('subscription_id')
    company_id = response.data.pop('company_id')
    concerned_users = CompanyAndUserRelation.get_relations(company_id=company_id)
    ids = [user.user_id for user in concerned_users]
    data['concerned_users'] = ids
    return data, response


def extract_data_for_update(request, response):
    data = {}
    data['type'] = UPDATE
    data['event_id'] = response.data['document_was_created']['article_id']
    company_id = response.data.pop('company_id')
    concerned_users = Subscription.get_subscriptions(company_id=company_id)
    ids = [investor.relation_id for investor in concerned_users]
    data['concerned_users'] = ids
    return data, response


STRATEGIES = {
    UPDATE: extract_data_for_update,
    MESSAGE: extract_data_for_message,
    SUBSCRIPTION: extract_data_for_subscription
}


def add_notifications_for_user(related=False):
    """Decorator that pulls out the notifications for user and adds them to response data."""

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            request = args[0]
            user_id, response = get_user_id(request, response, related)
            if not user_id: return
            try:
                notifications = nm.extract_notifications_for_user(user_id)
                response.data['notifications'] = notifications
            except NotificationNotFound as e:
                response.data['notifications'] = str(e)
            return response

        return wrapper

    return decorator


def create_notification_from_view(type=None):
    """Creates the notification for the event. You have to pass the event type to decorator."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            if not type:
                return response
            request = args[0]
            extraction_strategy = STRATEGIES[type]
            nf_data, response = extraction_strategy(request, response)
            create_notification(nf_data)
            return response

        return wrapper

    return decorator
