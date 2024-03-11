from datetime import datetime
from typing import Optional

from pydantic import BaseModel


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
