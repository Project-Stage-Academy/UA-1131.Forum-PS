import json
import os
from bson import ObjectId
from pydantic import ValidationError
from datetime import datetime
from redis.utils import from_url
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from authentication.authentications import UserAuthentication
from authentication.models import CustomUser
from authentication.permissions import IsAuthenticated
from .schemas import Conversation
<<<<<<< HEAD
from .utils import mongo_conversations

collections = mongo_conversations()
=======
from forum.settings import DB


collections = DB['conversations']
>>>>>>> d03a23617daf276dc005bcf525a39ebf482b1a0e


class StartConversation(APIView):
    """ Creating conversation, if it doesn`t exists, after this pk or conversation ll be used in web socket link"""
    authentication_classes = (UserAuthentication,)
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
        existing_conversation = collections.find_one({
            "$or": [
                {"initiator_id": current_user.user_id, "receiver_id": participant.user_id},
                {"initiator_id": participant.user_id, "receiver_id": current_user.user_id}
            ]
        })
        if existing_conversation:
            existing_conversation['_id'] = str(existing_conversation['_id'])
            return Response(existing_conversation, status=status.HTTP_200_OK)
        else:
            new_conversation = {
                "initiator_id": current_user.user_id,
                "receiver_id": participant.user_id,
                "start_time": datetime.now(),
                "messages": []
            }
            try:
                new_conversation_serialized = Conversation.parse_obj(new_conversation).dict()
                collections.insert_one(new_conversation_serialized)
                new_conversation_serialized['_id'] = str(new_conversation_serialized['_id'])
                return Response(new_conversation_serialized, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GetConversations(APIView):
    authentication_classes = (UserAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, convo_id):
        if ObjectId.is_valid(convo_id):
            existing_conversation = collections.find_one({"_id": ObjectId(convo_id)})
            if not existing_conversation:
                return Response({'message': 'Conversation does not exist'}, status=status.HTTP_404_NOT_FOUND)
            if request.user.user_id in [existing_conversation.get("initiator_id"),
                                        existing_conversation.get("receiver_id")]:
                existing_conversation['_id'] = str(existing_conversation['_id'])
                return Response(existing_conversation)
            else:
                return Response({"message": "You are not the participant of this live-chat"},
                                status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"message": "Provided invalid chat id"}, status=status.HTTP_400_BAD_REQUEST)


class ConversationsList(APIView):
    authentication_classes = (UserAuthentication,)
    permission_classes = (IsAuthenticated | IsAdminUser,)

    def get(self, request):
        user = request.user
        conversation_list = collections.find({
            "$or": [
                {"initiator_id": user.user_id},
                {"receiver_id": user.user_id},
            ]
        }
        ).sort([("_id", -1)]).limit(5)
        conversation_list_serialized = []
        for conversation in conversation_list:
            conversation['_id'] = str(conversation['_id'])
            conversation_list_serialized.append(
                {"_id": conversation["_id"],
                 "initiator_id": conversation["initiator_id"],
                 "receiver_id": conversation["receiver_id"],
                 "start_time": conversation["start_time"]})
        return Response(conversation_list_serialized, status=status.HTTP_200_OK)


class EmergencyConversationRestart(APIView):
    """
    If its needed this view will restart chat by conversation id, if authenticated user is a participant in this chat.
    Messages are stored in redis, due to messages lifetime
    """
    authentication_classes = (UserAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, convo_id):
        if ObjectId.is_valid(convo_id):
            existing_conversation = collections.find_one({"_id": ObjectId(convo_id)})
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
