from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from chats.models import Message, Chat
from chats.permissions import ChatParticipantPermission, MessageParticipantPermission
from chats.serializers import ChatSerializer, MessageSerializer, MailboxSerializer
from companies.models import CompaniesAndUsersRelations


# Create your views here.

class MessageDetail(APIView):
    permission_classes = (IsAuthenticated, MessageParticipantPermission)

    def get(self, request, pk):
        message = get_object_or_404(Message, pk=pk)
        self.check_object_permissions(request, message)
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SendMessage(generics.CreateAPIView):
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]


class ChatList(APIView):
    permission_classes = (IsAuthenticated, ChatParticipantPermission)

    def get(self, request, pk):
        chat = get_object_or_404(Chat, pk=pk)
        self.check_object_permissions(request, chat)
        serializer = ChatSerializer(chat)
        return Response(serializer.data, status=status.HTTP_200_OK)


class OutboxView(APIView):

    def get(self, request):
        sender = request.user
        user_companies = CompaniesAndUsersRelations.objects.filter(user_id=sender.id).values_list('company_id',
                                                                                                  flat=True)
        queryset = Message.objects.filter(sender__in=user_companies, visible_for_sender=True).order_by("-timestamp")
        serializer = MailboxSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InboxView(APIView):

    def get(self, request):
        recipient = request.user
        user_companies = CompaniesAndUsersRelations.objects.filter(user_id=recipient.id).values_list('company_id',
                                                                                                     flat=True)
        queryset = Message.objects.filter(recipient__in=user_companies, visible_for_recipient=True).order_by(
            "-timestamp")
        serializer = MailboxSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageDeleteView(APIView):
    permission_classes = (IsAuthenticated, MessageParticipantPermission)

    def post(self, request, pk):
        user_id = request.user.id
        message = get_object_or_404(Message, pk=pk)
        self.check_object_permissions(request, message)
        user_company_ids = CompaniesAndUsersRelations.objects.filter(user_id=user_id).values_list('company_id',
                                                                                                  flat=True)
        if message.sender.company_id in user_company_ids:
            message.visible_for_sender = False
            message.save()
            if not message.visible_for_recipient and not message.visible_for_sender:
                message.delete()
                return Response({"message": "Message was deleted"}, status=status.HTTP_200_OK)
            return Response({"message": "Message was deleted from your mailbox"}, status=status.HTTP_200_OK)
        if message.recipient.company_id in user_company_ids:
            message.visible_for_recipient = False
            message.save()
            if not message.visible_for_recipient and not message.visible_for_sender:
                message.delete()
                return Response({"message": "Message was deleted"}, status=status.HTTP_200_OK)
            return Response({"message": "Message was deleted from your mailbox"}, status=status.HTTP_200_OK)
