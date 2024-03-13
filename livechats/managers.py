import math
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel
from typing import Optional

from forum.settings import DB
from forum.managers import MongoManager


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


class LiveChatManager(MongoManager):
    db = DB['conversations']

    @classmethod
    def create_conversation(cls, new_conversation):
        new_conversation_serialized = Conversation.parse_obj(new_conversation).dict()
        cls.db.insert_one(new_conversation_serialized)
        return cls.id_to_string(new_conversation_serialized)

    @classmethod
    def get_conversation_by_participants(cls, initiator, participant):
        query = {
            "$or": [
                {"initiator_id": initiator.user_id, "receiver_id": participant.user_id},
                {"initiator_id": participant.user_id, "receiver_id": initiator.user_id}
            ]
        }
        conversation = cls.db.find_one(query, {"messages": 0})
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
        conversations = cls.db.find(query, {"messages": 0})
        conversation_list = cls.to_list(conversations)
        conversation_list = conversation_list[::-1]
        return conversation_list

    @classmethod
    def get_conversation_by_id(cls, conversation_id):
        query = {"_id": ObjectId(conversation_id)}
        existing_conversation = cls.db.find_one(query, {"messages": 0})
        if existing_conversation:
            return cls.id_to_string(existing_conversation)
        return None

    @classmethod
    def upgrade_messages(cls, conversation_id, messages):
        if len(messages) > 50:
            for i in range(math.ceil(len(messages) / 50)):
                if len(messages) > 50:
                    cls.db.update_one({"_id": ObjectId(conversation_id)},
                                      {"$push": {"messages": {"$each": messages[0:50]}}})
                    messages = messages[50:]
                else:
                    cls.db.update_one({"_id": ObjectId(conversation_id)}, {"$push": {"messages": messages}})
                    break
        else:
            cls.db.update_one({"_id": ObjectId(conversation_id)}, {"$push": {"messages": messages}})
