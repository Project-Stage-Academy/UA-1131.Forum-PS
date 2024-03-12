
import os
from bson import ObjectId
from pydantic import ValidationError
from datetime import datetime
from redis.utils import from_url
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.models import CustomUser
from authentication.permissions import IsAuthenticated

from .managers import LiveChatManager as lm


class StartConversation(APIView):
    """ Creating conversation, if it doesn`t exists, after this pk or conversation ll be used in web socket link"""
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = request.data
        user_email = data.get("email")
        current_user = request.user
        if request.user.email == user_email:
            return Response({'message': 'You cannot chat with yourself'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            participant = CustomUser.objects.get(email=user_email)
        except CustomUser.DoesNotExist:
            return Response({'message': 'You cannot chat with a non existent user'}, status=status.HTTP_400_BAD_REQUEST)
        existing_conversation = lm.get_conversation_by_participants(current_user, participant)
        if existing_conversation:
            return Response(existing_conversation, status=status.HTTP_200_OK)
        else:
            new_conversation = {
                "initiator_id": current_user.user_id,
                "receiver_id": participant.user_id,
                "start_time": datetime.now(),
                "messages": []
            }
            try:
                new_conversation = lm.create_conversation(new_conversation)
                return Response(new_conversation, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetConversations(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, convo_id):
        if ObjectId.is_valid(convo_id):
            existing_conversation = lm.get_conversation_by_id(convo_id)
            if not existing_conversation:
                return Response({'message': 'Conversation does not exist'}, status=status.HTTP_404_NOT_FOUND)
            if request.user.user_id in [existing_conversation.get("initiator_id"),
                                        existing_conversation.get("receiver_id")]:
                return Response(existing_conversation)
            else:
                return Response({"message": "You are not the participant of this live-chat"},
                                status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"message": "Provided invalid chat id"}, status=status.HTTP_400_BAD_REQUEST)


class ConversationsList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        current_user = request.user
        conversations_list = lm.get_users_conversations(current_user)
        return Response(conversations_list, status=status.HTTP_200_OK)


class EmergencyConversationRestart(APIView):
    """
    If its needed this view will restart chat by conversation id, if authenticated user is a participant in this chat.
    Messages are stored in redis, due to messages lifetime
    """
    permission_classes = (IsAuthenticated,)

    def post(self, request, convo_id):
        if ObjectId.is_valid(convo_id):
            existing_conversation = lm.get_conversation_by_id(convo_id)
            if request.user.user_id in [existing_conversation.get("initiator_id"),
                                        existing_conversation.get("receiver_id")]:
                redis = from_url(
                    os.environ.get("REDIS_URL"), encoding="utf-8", decode_responses=True
                )
                with redis.client() as conn:
                    users = conn.hgetall(f"{convo_id}_users")
                    if users:
                        conn.delete(f"{convo_id}_users")
                return Response({"message": "Chat was restarted"}, status=status.HTTP_200_OK)
            return Response({"message": "You are not the participant of this live-chat"},
                            status=status.HTTP_403_FORBIDDEN)

        else:
            return Response({"message": "Provided invalid chat id"}, status=status.HTTP_400_BAD_REQUEST)
