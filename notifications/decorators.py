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
            return None, response
    return user_id, response

def add_prefix_to_id(id, related=False):
    prefix = 'u_' if not related else 'rel_'
    id = prefix + str(id)
    return id


def extract_data_for_message(request, response):
    data = {}
    data['type'] = MESSAGE
    data['event_id'] = response.data['inserted_id']
    data['conсerned_users'] = [add_prefix_to_id(request.data.get('receiver_id'),
                                                related=True)]
    return data, response

def extract_data_for_subscription(request, response):
    data = {}
    data['type'] = SUBSCRIPTION
    try:
        data['event_id'] = response.data.pop('subscription_id')
        company_id = response.data.pop('company_id')
    except KeyError:
        return None, response
    concerned_users = CompanyAndUserRelation.get_relations(company_id=company_id)
    ids = [add_prefix_to_id(relation.user_id.user_id, related=True) for relation in concerned_users]
    data['concerned_users'] = ids
    return data, response


def extract_data_for_update(request, response):
    data = {}
    data['type'] = UPDATE
    data['event_id'] = response.data['document_was_created']['article_id']
    company_id = response.data.pop('company_id')
    concerned_users = Subscription.get_subscriptions(company_id=company_id)
    ids = [add_prefix_to_id(subscription.investor.relation_id, related=True) for subscription in concerned_users]
    data['concerned_users'] = ids
    return data, response

STRATEGIES = {
              UPDATE: extract_data_for_update,
              MESSAGE: extract_data_for_message,
              SUBSCRIPTION: extract_data_for_subscription
             }

def extract_notifications_for_user(related=False):
    """
       Decorator that pulls out the notifications for user and adds them to response data.

       Required parameters:
           - boolean parameter 'related' which indicates if user is
             supposed to be related to company;
             default value is False.
           - user ID or relation ID;
             if no ID is passed in response, takes it from request.user;

       Response:
           - adds 'notifications' to response: list with notifications or else message.
           - if user or relation ID is passed in response, pops it away;
    """
    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            if response.status_code in (400, 403, 302):
                return response
            request = args[1]
            user_id, response = get_user_id(request, response, related)
            if not user_id:
                return response
            try:
                user_id = add_prefix_to_id(user_id, related)
                notifications = nm.extract_notifications_for_user(user_id)
                response.data['notifications'] = notifications
            except NotificationNotFound as e:
                response.data['notifications'] = str(e)
            return response

        return wrapper

    return decorator

def create_notification_from_view(type=None):
    """Creates the notification for the event.

       Required parameters:
           - type thet indicates which type of event to handle;
             types is subscription, message, update

    """
    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            if response.status_code in (400, 403, 302):
                return response
            if not type:
                return response
            request = args[0]
            extraction_strategy = STRATEGIES[type]
            nf_data, response = extraction_strategy(request, response)
            if not nf_data:
                return response
            create_notification(nf_data)
            return response
       
        return wrapper
  
    return decorator


