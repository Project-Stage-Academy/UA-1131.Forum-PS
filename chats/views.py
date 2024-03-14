from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from pydantic import ValidationError

from authentication.models import Company
from authentication.permissions import IsAuthenticated
from forum.errors import Error
from notifications.decorators import create_notification_from_view, MESSAGE
from .manager import MessagesManager as manager
from .manager import Message


class MessageDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, message_id):
        message = manager.get_message(message_id)
        company_id = request.user.company.get("company_id")
        if message.get("sender_id") == company_id:
            if bool(message.get("visible_for_sender")):
                del message["visible_for_sender"]
                del message["visible_for_receiver"]
                return Response(message, status=status.HTTP_200_OK)
            return Response({"message": "no such message"}, status=status.HTTP_200_OK)
        if message.get("receiver_id") == company_id:
            if bool(message.get("visible_for_receiver")):
                del message["visible_for_sender"]
                del message["visible_for_receiver"]
                return Response(message, status=status.HTTP_200_OK)
            return Response({"message": "no such message"}, status=status.HTTP_200_OK)
        return Response(message, status=status.HTTP_200_OK)


class SendMessageView(APIView):
    permission_classes = [IsAuthenticated]
    
    @create_notification_from_view(type=MESSAGE)
    def post(self, request):
        data = request.data
        company_id = request.user.company.get("company_id")
        receiver_id = data.get("receiver_id")
        if not company_id == receiver_id:
            sender = Company.objects.get(pk=company_id)
            receiver = Company.objects.get(pk=receiver_id)
            message = {
                "sender_id": company_id,
                "sender_data": sender.brand,
                "receiver_id": receiver_id,
                "receiver_data": receiver.brand,
                "msg_text": data.get("msg_text"),
                "msg_topic": data.get("msg_topic"),
                "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                "visible_for_sender": True,
                "visible_for_receiver": True,
            }
            try:
                message_validated = Message.parse_obj(message)
                message_validated = manager.create_message(message_validated)
                return Response(message_validated, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "You can`t send message to yourself"}, status=status.HTTP_400_BAD_REQUEST)


class MessageDeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, message_id):
        try:
            company_id = request.user.company.get("company_id")
            manager.delete_message(company_id, message_id)
            return Response({"message": "Message was deleted"}, status=status.HTTP_200_OK)
        except AttributeError:
            raise NotAuthenticated(detail=Error.NO_USER_OR_COMPANY_ID.msg)


class OutboxView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            company_id = request.user.company.get("company_id")
            messages = manager.company_outbox_messages(company_id)
            return Response(messages, status=status.HTTP_200_OK)
        except AttributeError:
            raise NotAuthenticated(detail=Error.NO_USER_OR_COMPANY_ID.msg)


class InboxView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            company_id = request.user.company.get("company_id")
            messages = manager.company_inbox_messages(company_id)
            return Response(messages, status=status.HTTP_200_OK)
        except AttributeError:
            raise NotAuthenticated(detail=Error.NO_USER_OR_COMPANY_ID.msg)


class ListMessagesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self,request):
        try:
            company_id = request.user.company.get("company_id")
            messages = manager.get_messages_to_company(company_id)
            return Response(messages, status=status.HTTP_200_OK)
        except AttributeError:
            raise NotAuthenticated(detail=Error.NO_USER_OR_COMPANY_ID.msg)
