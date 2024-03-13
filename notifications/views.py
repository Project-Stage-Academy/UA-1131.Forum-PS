from rest_framework.response import Response
from rest_framework.views import APIView

from .manager import AlreadyExist
from .manager import NotificationManager as nm
from .manager import NotificationNotFound

cl = 'Notification'


class CreateNotification(APIView):
    def post(self, request):
        data = request.data
        try:
            res = nm.create_notification(data)
        except AlreadyExist as e:
            return Response({"error": str(e)})
        return Response(res)


class DeleteNotifications(APIView):
    def get(self, request):
        res = nm.delete_old_notifications()
        return Response(res)


class CreateNotifications(APIView):
    def post(self, request):
        data = request.data
        res = nm.create_notifications(data)
        return Response(res)


class GetNotifications(APIView):
    def get(self, request):
        data = request.data
        id = data['user_id']
        try:
            res = nm.extract_notifications_for_user(id)
        except NotificationNotFound as e:
            return Response({"error": str(e)})
        return Response(res)


class GetNotificationsByType(APIView):
    def get(self, request):
        data = request.data
        type = data['type']
        try:
            res = nm.extract_notifications_by_type(type)
        except NotificationNotFound as e:
            return Response({"error": str(e)})
        return Response(res)


class NotificationViewed(APIView):
    def post(self, request):
        data = request.data
        n_id = data['notification_id']
        u_id = data['user_id']
        try:
            notification = nm.store_viewed_user(n_id, u_id)
        except (NotificationNotFound, AlreadyExist) as e:
            return Response({"error": str(e)})
        return Response(notification)
