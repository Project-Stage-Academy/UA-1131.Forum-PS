from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from authentication.models import CompanyAndUserRelation
from .models import (Message, Chat)
from .permissions import (ChatParticipantPermission, MessageParticipantPermission)
from .serializers import (ChatSerializer, MessageSerializer, MailboxSerializer)





class MessageDetail(APIView):
    permission_classes = (IsAuthenticated, MessageParticipantPermission)

    def get(self, request, pk):
        message = get_object_or_404(Message, pk=pk)
        self.check_object_permissions(request, message)
        serializer = MessageSerializer(message)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SendMessage(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = MessageSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            participant_1 = serializer.validated_data.get('sender')
            participant_2 = serializer.validated_data.get('recipient')
            content = serializer.data.get('content')
            chat = Chat.objects.filter(participants=participant_1).filter(participants=participant_2)
            if not chat:
                chat = Chat.objects.create()
                chat.participants.add(participant_1, participant_2)
            message = Message.objects.create(chat=chat[0], sender=participant_1, recipient=participant_2,
                                   content=content)
            message.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

        user_companies = CompanyAndUserRelation.objects.filter(user_id=sender.id)

        queryset = Message.objects.filter(sender__in=user_companies, visible_for_sender=True).order_by("-timestamp")
        serializer = MailboxSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class InboxView(APIView):

    def get(self, request):
        recipient = request.user

        user_companies = CompanyAndUserRelation.objects.filter(user_id=recipient.id)

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

        user_company_ids = CompanyAndUserRelation.objects.filter(user_id=user_id)

        if message.sender in user_company_ids:
            message.visible_for_sender = False
            message.save()
            if not message.visible_for_recipient and not message.visible_for_sender:
                message.delete()
                return Response({"message": "Message was deleted"}, status=status.HTTP_200_OK)
            return Response({"message": "Message was deleted from your mailbox"}, status=status.HTTP_200_OK)
        if message.recipient in user_company_ids:
            message.visible_for_recipient = False
            message.save()
            if not message.visible_for_recipient and not message.visible_for_sender:
                message.delete()
                return Response({"message": "Message was deleted"}, status=status.HTTP_200_OK)
            return Response({"message": "Message was deleted from your mailbox"}, status=status.HTTP_200_OK)
