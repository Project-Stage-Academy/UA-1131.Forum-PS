import pymongo
from pydantic import BaseModel, Field, ValidationError
from forum.settings import DB, EMAIL_HOST_USER


class Message(BaseModel):
    """Pydentic BaseModel class for Messages validations"""
    msg_text: str
    msg_topic: str
    timestamp: str
    sender_id: int
    sender_data: str


class MessagesManager:
    db = DB['Messages']

