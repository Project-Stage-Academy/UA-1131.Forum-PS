import datetime
import json

import redis
from django.core.cache import cache
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from livechats.models import Conversation, Message
from livechats.serializers import MessageSerializer


class ChatConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_conversation(self, pk):
        conv = Conversation.objects.get(id=int(pk))
        initiator = conv.initiator
        receiver = conv.receiver
        return Conversation.objects.get(id=int(pk)), initiator, receiver

    async def create_message_data(self, message):
        conversation = await self.get_conversation(self.room_name)
        sender = self.scope["user"]
        message = {"timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                   "sender": sender,
                   "text": message["message"],
                   "conversation_id": conversation[0]}
        return message

    async def cache_data(self, message):
        _message = await self.create_message_data(message)
        chat_value = cache.get(_message["conversation_id"])
        if chat_value:
            chat_value = str(_message) + chat_value
        else:
            chat_value = str(_message)
        cache.set(_message["conversation_id"], chat_value, 36000)

    async def connect(self):
        print("here")
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"
        conversation, initiator, receiver = await self.get_conversation(self.room_name)
        participants_of_conv = [initiator, receiver]

        current_user = self.scope['user']

        if current_user.is_authenticated and current_user in participants_of_conv:
            await self.channel_layer.group_add(
                self.room_group_name, self.channel_name
            )

            await self.accept()
            await self.channel_layer.group_send(self.room_group_name,
                                                {"type": "chat.join",
                                                 "user_id": current_user.id,
                                                 "email": current_user.email, })
        else:
            # close connection to the other users
            await self.close()

    async def chat_join(self, event):
        user_id = event['user_id']
        email = event['email']
        _message = f"User {user_id} {email} joined the chat."
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": _message
            }
        )
        await self.cache_data({"message": _message})

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        chat_type = {"type": "chat_message"}
        return_dict = {**chat_type, **text_data_json}
        await self.channel_layer.group_send(self.room_group_name, return_dict)
        await self.cache_data(text_data_json)

    async def chat_message(self, event):
        text_data_json = event.copy()
        text_data_json.pop("type")
        _message = await self.create_message_data(text_data_json)
        serializer = MessageSerializer(instance=_message)
        await self.send(
            text_data=json.dumps(
                serializer.data
            )
        )
