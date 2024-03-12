from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel
from typing import Optional

from rest_framework import status

from forum.settings import DB


class Message(BaseModel):
    """Pydentic BaseModel class for Messages validations"""
    msg_text: str
    timestamp: str
    sender_id: int
    sender_data: str
    conversation_id: str


class Conversation(BaseModel):
    """Pydentic BaseModel class for conversation validations"""
    initiator_id: int
    receiver_id: int
    start_time: datetime
    messages: Optional[list[Message]]


class MongoManager:

    @classmethod
    def id_to_string(cls, document):
        """Changes _id field of returned document from ObjectId to string."""

        document['_id'] = str(document['_id'])
        return document

    @classmethod
    def to_list(cls, cursor):
        """Returns the list of objects from the PyMongo cursor."""

        res = []
        for el in cursor:
            res.append(cls.id_to_string(el))
        return res


class LiveChatManager(MongoManager):
    collections = DB['conversations']

    @classmethod
    def create_conversation(cls, new_conversation):
        new_conversation_serialized = Conversation.parse_obj(new_conversation).dict()
        cls.collections.insert_one(new_conversation_serialized)
        return cls.id_to_string(new_conversation_serialized)

    @classmethod
    def get_conversation_by_participants(cls, initiator, participant):
        query = {
            "$or": [
                {"initiator_id": initiator.user_id, "receiver_id": participant.user_id},
                {"initiator_id": participant.user_id, "receiver_id": initiator.user_id}
            ]
        }
        conversation = cls.collections.find_one(query)
        if conversation:
            return cls.id_to_string(conversation)
        return None

    @classmethod
    def get_users_conversations(cls, participant):
        query = {
            "$or": [
                {"initiator_id": participant.user_id},
                {"receiver_id": participant.user_id},
            ]}
        conversations = cls.collections.find(query, {"messages": 0})
        conversation_list = cls.to_list(conversations)
        conversation_list = conversation_list.reverse()
        return conversation_list

    @classmethod
    def get_conversation_by_id(cls, conversation_id):
        query = {"_id": ObjectId(conversation_id)}
        existing_conversation = cls.collections.find_one(query)
        if existing_conversation:
            return cls.id_to_string(existing_conversation)
        return None
