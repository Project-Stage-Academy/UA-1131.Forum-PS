from functools import wraps
from .manager import NotificationManager as nm, NotificationNotFound
from .tasks import create_notification


def add_notifications_for_user():
    """Decorator that pulls out the notifications for user and adds them to response data."""
    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)

            data = response.data
            try:
                user_id = data['user_id']
            except KeyError:
                request = args[0]
                user_id = request.user.user_id
            try:
                notifications = nm.extract_notifications_for_user(user_id)
                data['notifications'] = notifications
            except NotificationNotFound as e:
                data['notifications'] = str(e)
            response.data = data

            return response

        return wrapper

    return decorator


def create_notification_from_view(type_=None):
    """Creates the notification for the event. You have to pass the event type to decorator."""
    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            response = func(*args, **kwargs)
            if not type_:
                return response

            data = response.data
            data['type'] = type_
            create_notification(data)
            return response
       
        return wrapper
  
    return decorator
