from django.shortcuts import render, get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.permissions import CustomUserUpdatePermission
from chats.models import Message, Chat
from chats.permissions import ChatParticipantPermission, MessageParticipantPermission
from chats.serializers import ChatSerializer, MessageSerializer, InboxSerializer
from companies.models import CompaniesAndUsersRelations, Companies


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


class InboxView(APIView):

    def get(self, request):
        recipient = self.request.user
        user_companies = CompaniesAndUsersRelations.objects.filter(user_id=recipient.id).values_list('company_id',
                                                                                                     flat=True)
        queryset = Message.objects.filter(sender__in=user_companies).order_by("-timestamp")
        serializer = InboxSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
