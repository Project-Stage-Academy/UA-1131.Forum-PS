from datetime import datetime
from typing import Optional

import pydantic
from pydantic import BaseModel


# Create your models here.

class Message(BaseModel):
    msg_text: str
    timestamp: str
    sender_id: int
    sender_data: str
    conversation_id: str




class Conversation(BaseModel):
    initiator_id: int
    receiver_id: int
    start_time: datetime
    messages: Optional[list[Message]]

