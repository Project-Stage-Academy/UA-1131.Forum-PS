import os
from datetime import datetime

from bson import ObjectId
from django.shortcuts import redirect, reverse
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from pymongo import MongoClient
from pydantic import ValidationError

from authentication.models import CustomUser
from .schemas import Conversation

client = MongoClient(os.environ.get("MONGODB_HOST"))
collections = client.livechats.conversations


# Create your views here.
@api_view(['POST'])
def start_conversation(request, ):
    """ Creating conversation, if it doesn`t exists, after this pk or conversation ll be used in web socket link"""
    data = request.data
    user_email = data.pop("email")
    current_user = request.user
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
        return redirect(reverse('get_conversation', args=(existing_conversation["_id"],)))
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
            return Response(new_conversation_serialized, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_conversation(request, convo_id):
    conversation = collections.find_one({"_id": ObjectId(convo_id)})
    if not conversation:
        return Response({'message': 'Conversation does not exist'}, status=status.HTTP_404_NOT_FOUND)
    else:
        conversation['_id'] = str(conversation['_id'])
        return Response(conversation)


@api_view(['GET'])
def conversations(request):
    user = request.user
    conversation_list = collections.find({
        "$or": [
            {"initiator_id": user.id},
            {"receiver_id": user.id},
        ]
    }
    )
    conversation_list_serialized = []
    for conversation in conversation_list:
        conversation['_id'] = str(conversation['_id'])
        conversation_list_serialized.append(conversation)
    return Response(conversation_list_serialized)
