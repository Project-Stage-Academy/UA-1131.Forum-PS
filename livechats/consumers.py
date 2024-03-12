import json
import math
import os
from bson import ObjectId
from django.utils import timezone
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from redis.asyncio import from_url
from livechats.schemas import Message
from livechats.utils import mongo_conversations
from livechats.managers import LiveChatManager as lm


class ChatConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_conversation(self):
        conv = lm.get_conversation_by_id(self.room_name)
        initiator = conv.get("initiator_id")
        receiver = conv.get("receiver_id")
        return conv, initiator, receiver

    @database_sync_to_async
    def update_conversation(self, messages):
        """Function for updating live-chat messages data"""
        lm.upgrade_messages(self.room_name, messages)

    async def create_message_data(self, message):
        """Function for creating messages available for caching and sending"""
        conversation = await self.get_conversation()
        sender = self.scope["user"]
        message = {
            "msg_text": message["message"],
            "timestamp": timezone.now().strftime("%Y-%m-%d %H:%M:%S"),
            "sender_id": sender.user_id,
            "sender_data": f"{sender.first_name} {sender.surname}, {sender.email}",
            "conversation_id": str(conversation[0].get("_id")),
        }
        return message

    async def cache_data(self, message):
        """Function for adding messages and joining data to cache for 10 hours"""
        _message = await self.create_message_data(message)
        _message_json = json.dumps(_message)
        redis = await from_url(
            os.environ.get("REDIS_URL"), encoding="utf-8", decode_responses=True
        )
        async with redis.client() as conn:
            await conn.lpush(_message["conversation_id"], _message_json)
            await conn.expire(_message["conversation_id"], 36000)

    async def connect(self):
        """
        Connecting to the WS, also adding number Redis activity tracker
         for counting the number of active users in a channel
         """

        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        conversation, initiator, receiver = await self.get_conversation()
        participants_of_conv = [initiator, receiver]
        current_user = self.scope['user']
        if current_user.user_id in participants_of_conv:
            await self.channel_layer.group_add(
                self.room_group_name, self.channel_name
            )
            await self.accept()
            redis = await from_url(
                os.environ.get("REDIS_URL"), encoding="utf-8", decode_responses=True
            )
            async with redis.client() as conn:
                user_active = conn.hget(f"{self.room_name}_users", current_user.email)
                if not user_active:
                    await conn.hincrby(f"{self.room_name}_users", current_user.email, 1)
                    await conn.expire(f"{self.room_name}_users", 36000)
                else:
                    await conn.hincrby(f"{self.room_name}_users", current_user.email, +1)
                    await conn.expire(f"{self.room_name}_users", 36000)
        else:
            await self.close()

    async def disconnect(self, close_code):
        """
        Disconnecting from the WS, after user leaves the channel it decreases activity tracker in redis,
        when num of active users is 0, the chat cache will be sent to MongoBD and Redis cache ll be cleaned.
         """
        current_user = self.scope['user']
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        redis = await from_url(
            os.environ.get("REDIS_URL"), encoding="utf-8", decode_responses=True
        )
        messages = None
        async with redis.client() as conn:
            await conn.hincrby(f"{self.room_name}_users", current_user.email, -1)
            user_activity = await conn.hget(f"{self.room_name}_users", current_user.email, )
            if user_activity == "0":
                await conn.hdel(f"{self.room_name}_users", current_user.email, )
                if not await conn.hgetall(f"{self.room_name}_users"):
                    conn.delete(f"{self.room_name}_users")
                    messages = await conn.lrange(self.room_name, 0, -1)
                    await conn.delete(self.room_name)
        if messages:
            messages_list = [Message.parse_raw(msg).dict() for msg in messages]
            await self.update_conversation(messages_list)

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
