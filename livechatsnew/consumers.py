import json

import pydantic
from bson import ObjectId
from datetime import datetime
from django.core.cache import cache
from collections import defaultdict
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from livechatsnew.utils import mongo_conversations
from livechatsnew.schemas import Message
from pydantic import parse_obj_as


class ChatConsumer(AsyncWebsocketConsumer):
    room_connection_counts = defaultdict(lambda: 0)

    @database_sync_to_async
    def get_conversation(self):
        conversations = mongo_conversations()
        conv = conversations.find_one({"_id": ObjectId(self.room_name)})
        initiator = conv.get("initiator_id")
        receiver = conv.get("receiver_id")
        return conv, initiator, receiver

    @database_sync_to_async
    def update_conversation(self, messages):
        """Function for updating live-chat messages data"""
        conversations = mongo_conversations()
        conversations.update_one({"_id": ObjectId(self.room_name)}, {"$push": {"messages": messages}})

    async def create_message_data(self, message):
        """Function for creating messages available for caching and sending"""
        conversation = await self.get_conversation()
        sender = self.scope["user"]
        message = {
            "msg_text": message["message"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sender_id": sender.id,
            "sender_data": str(sender),
            "conversation_id": str(conversation[0].get("_id")),

        }
        return message

    async def cache_data(self, message):
        """Function for adding messages and joining data to cache for 10 hours"""
        _message = await self.create_message_data(message)
        chat_value = cache.get(_message["conversation_id"])
        if chat_value:
            chat_value = str(_message) + "," + chat_value
        else:
            chat_value = str(_message)
        cache.set(_message["conversation_id"], chat_value, 36000)

    async def connect(self):
        """
        Connecting to the WS, also adding number to "room_connection_counts"
         for counting the number of active users in a channel
         """
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        conversation, initiator, receiver = await self.get_conversation()
        participants_of_conv = [initiator, receiver]

        current_user = self.scope['user']

        if current_user.is_authenticated and current_user.id in participants_of_conv:
            await self.channel_layer.group_add(
                self.room_group_name, self.channel_name
            )

            await self.accept()
            self.room_connection_counts[self.room_name] += 1

        else:
            await self.close()

    async def disconnect(self, close_code):
        """
        Disconnecting from the WS, after user leaves the channel in decrease "room_connection_counts",
        when num of active users is 0, the chat cache will be sent to MongoBD and Redis cache ll be cleaned.
        "parse_obj_as" validate the data in list of messages from cache.
         """
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        self.room_connection_counts[self.room_name] -= 1
        if not self.room_connection_counts[self.room_name]:
            chat_value = cache.get(self.room_name)
            if chat_value:
                messages = [Message.parse_obj(message).dict() for message in eval(chat_value)]
                await self.update_conversation(messages)
                cache.clear()



    async def receive(self, text_data=None, bytes_data=None):
        """
        When message is sent my user it ll be sent to the cache
        """
        text_data_json = json.loads(text_data)
        chat_type = {"type": "chat_message"}
        return_dict = {**chat_type, **text_data_json}
        await self.channel_layer.group_send(self.room_group_name, return_dict)
        await self.cache_data(text_data_json)

    async def chat_message(self, event):
        text_data_json = event.copy()
        text_data_json.pop("type")
        message = await self.create_message_data(text_data_json)
        message_serialized = Message.parse_obj(message).dict()
        await self.send(
            text_data=json.dumps(
                message_serialized
            )
        )
