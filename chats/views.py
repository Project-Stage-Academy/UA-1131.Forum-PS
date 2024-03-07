import json

from pydantic import ValidationError

from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.permissions import IsAuthenticated
from .manager import MessagesManager as manager
from .manager import Message
from authentication.models import Company


class MessageDetail(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, message_id):
        message = manager.get_message(message_id)
        message_json = json.loads(message)
        company_id = request.data.get("company_id")
        if message.get("sender_id") == company_id:
            if bool(message.get("visible_for_sender")):
                return Response(message_json, status=status.HTTP_200_OK)
            return Response({"message": "no such message"}, status=status.HTTP_200_OK)
        if message.get("receiver_id") == company_id:
            if bool(message.get("visible_for_receiver")):
                return Response(message_json, status=status.HTTP_200_OK)
            return Response({"message": "no such message"}, status=status.HTTP_200_OK)
        return Response(message_json, status=status.HTTP_200_OK)


class SendMessage(APIView):
    permission_classes = [IsAuthenticated]

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
        company_id = request.user.company.get("company_id")
        manager.delete_message(company_id, message_id)
        return Response({"message": "Message was deleted"}, status=status.HTTP_200_OK)

# class ChatList(APIView):
#     permission_classes = (IsAuthenticated, ChatParticipantPermission)
#
#     def get(self, request, pk):
#         chat = get_object_or_404(Chat, pk=pk)
#         self.check_object_permissions(request, chat)
#         serializer = ChatSerializer(chat)
#         return Response(serializer.data, status=status.HTTP_200_OK)


# class OutboxView(APIView):
#
#     def get(self, request):
#         sender = request.user
#
#         user_companies = CompanyAndUserRelation.objects.filter(user_id=sender.id)
#
#         queryset = Message.objects.filter(sender__in=user_companies, visible_for_sender=True).order_by("-timestamp")
#         serializer = MailboxSerializer(queryset, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#
# class InboxView(APIView):
#
#     def get(self, request):
#         recipient = request.user
#
#         user_companies = CompanyAndUserRelation.objects.filter(user_id=recipient.id)
#
#         queryset = Message.objects.filter(recipient__in=user_companies, visible_for_recipient=True).order_by(
#             "-timestamp")
#         serializer = MailboxSerializer(queryset, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
