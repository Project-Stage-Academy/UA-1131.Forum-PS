from django.utils import timezone
from pydantic import ValidationError
from rest_framework import status
from rest_framework.exceptions import NotAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import Company, CompanyAndUserRelation
from authentication.permissions import IsAuthenticated
from forum.errors import Error

from .manager import Message, MessageNotFound
from .manager import MessagesManager as mm
from notifications.decorators import create_notification_from_view, MESSAGE


class MessageDetailView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, message_id):
        try:
            message = mm.get_message(message_id)
            company_id = request.user.company.get("company_id")
            if message.get("sender_company_id") == company_id:
                if bool(message.get("visible_for_sender")):
                    del message["visible_for_sender"]
                    del message["visible_for_receiver"]
                    return Response(message, status=status.HTTP_200_OK)
                return Response({"message": "No such message"}, status=status.HTTP_302_FOUND)
            if message.get("receiver_company_id") == company_id:
                if bool(message.get("visible_for_receiver")):
                    del message["visible_for_sender"]
                    del message["visible_for_receiver"]
                    return Response(message, status=status.HTTP_200_OK)
                return Response({"message": "No such message"}, status=status.HTTP_400_BAD_REQUEST)
            return Response(message, status=status.HTTP_200_OK)
        except MessageNotFound:
            return Response({"message": "Cannot find such message"}, status=status.HTTP_400_BAD_REQUEST)

class SendMessageView(APIView):
    """
      A view for sending messages.

      This view send message from one user, related to sender company to another user related with some another company.


      Request:
          - Method: POST
          - URL: /messages/send message/
          - Data Params:
              - receiver_id: relation id for getting receiver user and receiver company;
              - msg_topic: message topic
              - msg_text: message text
          - Response:
              - 201 Created: Message was created and send to receiver
              - 400 Bad Request: Invalid message format or you try to send message to your company

  """

    permission_classes = [IsAuthenticated]

    @create_notification_from_view(type=MESSAGE)
    def post(self, request):
        data = request.data
        sender_user_id = request.user.user_id
        sender_company_id = request.user.company.get("company_id")
        receiver_data = data.get("receiver_id")
        receiver = CompanyAndUserRelation.get_relation(relation_id=receiver_data)
        receiver_company_id = receiver.company_id.company_id
        receiver_user_id = receiver.user_id.user_id
        if not sender_company_id == receiver_company_id:
            sender = Company.objects.get(pk=sender_company_id)
            receiver = Company.objects.get(pk=receiver_company_id)
            message = {
                "sender_company_id": sender_company_id,
                "sender_data": sender.brand,
                "sender_user_id": sender_user_id,
                "receiver_company_id": receiver_company_id,
                "receiver_data": receiver.brand,
                "receiver_user_id": receiver_user_id,
                "msg_text": data.get("msg_text"),
                "msg_topic": data.get("msg_topic"),
                "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
                "visible_for_sender": True,
                "visible_for_receiver": True,
            }
            try:
                message_validated = Message.parse_obj(message)
                message_validated = mm.create_message(message_validated)
                return Response(message_validated, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "You can`t send message to your company"}, status=status.HTTP_400_BAD_REQUEST)


class MessageDeleteView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, message_id):
        try:
            company_id = request.user.company.get("company_id")
            mm.delete_message(company_id, message_id)
            return Response({"message": "Message was deleted"}, status=status.HTTP_200_OK)
        except AttributeError:
            return Response({"error": "Authentication error"}, status=status.HTTP_403_FORBIDDEN)
        except MessageNotFound:
            return Response({"error": "Message not found"}, status=status.HTTP_400_BAD_REQUEST)


class OutboxView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            company_id = request.user.company.get("company_id")
            messages = mm.company_outbox_messages(company_id)
            return Response(messages, status=status.HTTP_200_OK)
        except AttributeError:
            raise NotAuthenticated(detail=Error.NO_USER_OR_COMPANY_ID.msg)


class InboxView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            company_id = request.user.company.get("company_id")
            messages = mm.company_inbox_messages(company_id)
            return Response(messages, status=status.HTTP_200_OK)
        except AttributeError:
            raise NotAuthenticated(detail=Error.NO_USER_OR_COMPANY_ID.msg)


class ListMessagesView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        try:
            company_id = request.user.company.get("company_id")
            messages = mm.get_messages_to_company(company_id)
            return Response(messages, status=status.HTTP_200_OK)
        except AttributeError:
            raise NotAuthenticated(detail=Error.NO_USER_OR_COMPANY_ID.msg)
