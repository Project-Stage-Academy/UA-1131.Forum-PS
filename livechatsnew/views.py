import os
from redis.utils import from_url

from datetime import datetime
from bson import ObjectId
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from pymongo import MongoClient
from pydantic import ValidationError

from authentication.models import CustomUser
from .schemas import Conversation

client = MongoClient(os.environ.get("MONGODB_HOST"))
collections = client.livechats.conversations


# Create your views here.

class StartConversation(APIView):
    """ Creating conversation, if it doesn`t exists, after this pk or conversation ll be used in web socket link"""

    def post(self, request):
        data = request.data
        user_email = data.get("email")
        current_user = request.user
        if request.user.email == user_email:
            return Response({'message': 'You cannot chat with yourself'})

        try:
            participant = CustomUser.objects.get(email=user_email)

        except CustomUser.DoesNotExist:
            return Response({'message': 'You cannot chat with a non existent user'})

        existing_conversation = collections.find_one({
            "$or": [
                {"initiator_id": current_user.id, "receiver_id": participant.id},
                {"initiator_id": participant.id, "receiver_id": current_user.id}
            ]
        })

        if existing_conversation:
            existing_conversation['_id'] = str(existing_conversation['_id'])
            return Response({'conversation': existing_conversation})
        else:
            new_conversation = {
                "initiator_id": current_user.id,
                "receiver_id": participant.id,
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
    def get(self, request, convo_id):
        if ObjectId.is_valid(convo_id):
            conversation = collections.find_one({"_id": ObjectId(convo_id)})
            if not conversation:
                return Response({'message': 'Conversation does not exist'}, status=status.HTTP_404_NOT_FOUND)
            else:
                conversation['_id'] = str(conversation['_id'])
                return Response(conversation)
        else:
            return Response({"message": "Provided invalid chat id"})


class ConversationsList(APIView):
    def get(self, request):
        user = request.user
        conversation_list = collections.find({
            "$or": [
                {"initiator_id": user.id},
                {"receiver_id": user.id},
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
        return Response(conversation_list_serialized)


class EmergencyConversationRestart(APIView):
    def post(self, request, convo_id):
        if ObjectId.is_valid(convo_id):
            existing_conversation = collections.find_one({"_id": ObjectId(convo_id)})
            if request.user.id in [existing_conversation.get("initiator_id"), existing_conversation.get("receiver_id")]:
                redis = from_url(
                    os.environ.get("REDIS_HOST"), encoding="utf-8", decode_responses=True
                )
                with redis.client() as conn:
                    users = conn.hgetall(f"{convo_id}_users")
                    if users:
                        conn.delete(f"{convo_id}_users")
                return Response({"message": "Chat was restarted"})
            return Response({"message": "You are not the participant in this chat"})

        else:
            return Response({"message": "Provided invalid chat id"})
