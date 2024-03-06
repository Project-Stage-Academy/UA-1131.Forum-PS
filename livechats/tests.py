import asyncio
import json
import unittest.mock
from unittest import TestCase, IsolatedAsyncioTestCase

from asgiref.sync import sync_to_async
from channels.generic.websocket import WebsocketConsumer
from channels.routing import URLRouter
from channels.testing import WebsocketCommunicator
from django.urls import path, re_path
from mongomock import ObjectId, patch
from pymongo import MongoClient
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from jwt import encode as jwt_encode
from authentication.models import CustomUser
from forum import settings
from forum.jwt_token_middleware import JWTAuthMiddlewareStack
from livechats.consumers import ChatConsumer

class StartConversationTestCase(APITestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = APIClient()
        cls.user_initiator = CustomUser.objects.create_user(email="user@example.com", password="password")
        cls.user_recipient = CustomUser.objects.create_user(email="participant@example.com", password="password")
        cls.user_recipient_two = CustomUser.objects.create_user(email="participant3@example.com", password="password")
        cls.user_initiator_token = RefreshToken.for_user(cls.user_initiator).access_token

    def setUp(self):
        self.mock_conversations = patch("forum.settings.CLIENT.livechats.conversations")
        self.mock_conversations.start()
        self.mock_redis = unittest.mock.patch("redis.Redis")
        self.mock_redis.start()
        self.base_chat = self.client.post("/conversations/start/", {"email": "participant@example.com"},
                                          format="json",
                                          **{"HTTP_AUTHORIZATION": f"Bearer {self.user_initiator_token}"})

    def test_start_conversation(self):
        token = RefreshToken.for_user(self.user_recipient_two).access_token
        post_response = self.client.post("/conversations/start/", {"email": "participant@example.com"},
                                         format="json", **{"HTTP_AUTHORIZATION": f"Bearer {token}"})
        self.chat_id = post_response.data.get('_id')
        valid = ObjectId.is_valid(self.chat_id)
        self.assertTrue(valid)
        self.assertEqual(post_response.status_code, 201)

        post_response = self.client.post("/conversations/start/", {"email": "participant@example.com"},
                                         format="json", **{"HTTP_AUTHORIZATION": f"Bearer {self.user_initiator_token}"})
        self.assertEqual(post_response.status_code, 200)

    def test_start_conversation_create_wrong_data(self):
        post_response = self.client.post("/conversations/start/", {"email": "user@example.com"},
                                         format="json", **{"HTTP_AUTHORIZATION": f"Bearer {self.user_initiator_token}"})

        self.assertEqual(post_response.status_code, 400)  # should be False

    def test_start_conversation_to_yourself(self):
        post_response = self.client.post("/conversations/start/", {"email": "wrong@example.com"},
                                         format="json", **{"HTTP_AUTHORIZATION": f"Bearer {self.user_initiator_token}"})

        self.assertEqual(post_response.status_code, 400)  # should be False
        self.assertEqual(post_response.data['message'], 'You cannot chat with a non existent user')

    def test_get_conversation(self):
        get_response = self.client.get(f'/conversations/{self.base_chat.data["_id"]}/',
                                       **{"HTTP_AUTHORIZATION": f"Bearer {self.user_initiator_token}"})
        self.assertEqual(get_response.data["initiator_id"], self.user_initiator.user_id)
        self.assertEqual(get_response.status_code, 200)  # should be False

    def test_get_conversation_not_participant(self):
        not_participant_token = RefreshToken.for_user(self.user_recipient_two).access_token
        get_response = self.client.get(f'/conversations/{self.base_chat.data["_id"]}/',
                                       **{"HTTP_AUTHORIZATION": f"Bearer {not_participant_token}"})
        self.assertEqual(get_response.status_code, 403)
        self.assertEqual(get_response.data["message"], "You are not the participant of this live-chat")

    def test_get_conversation_invalid_id(self):
        get_response = self.client.get(f'/conversations/22222/',
                                       **{"HTTP_AUTHORIZATION": f"Bearer {self.user_initiator_token}"})
        self.assertEqual(get_response.status_code, 400)
        self.assertEqual(get_response.data["message"], "Provided invalid chat id")

    def test_get_conversation_wrong_chat(self):
        get_response = self.client.get(f'/conversations/65e0b7565e55df16a396c444/',
                                       **{"HTTP_AUTHORIZATION": f"Bearer {self.user_initiator_token}"})
        self.assertEqual(get_response.status_code, 404)
        self.assertEqual(get_response.data["message"], 'Conversation does not exist')

    def test_user_conversation(self):
        get_response = self.client.get(f'/conversations/',
                                       **{"HTTP_AUTHORIZATION": f"Bearer {self.user_initiator_token}"})
        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(len(get_response.data), 1)

    def test_restart_conversation(self):
        post_response = self.client.post(f'/conversations/restart/{self.base_chat.data["_id"]}/',
                                         **{"HTTP_AUTHORIZATION": f"Bearer {self.user_initiator_token}"})

        self.assertEqual(post_response.status_code, 200)  # should be False
        self.assertEqual(post_response.data["message"], "Chat was restarted")

    def test_restart_conversation_invalid_id(self):
        post_response = self.client.post(f'/conversations/restart/2222222/',
                                         **{"HTTP_AUTHORIZATION": f"Bearer {self.user_initiator_token}"})
        self.assertEqual(post_response.status_code, 400)  # should be False
        self.assertEqual(post_response.data["message"], "Provided invalid chat id")

    def test_restart_conversation_not_participant(self):
        not_participant_token = RefreshToken.for_user(self.user_recipient_two).access_token
        post_response = self.client.post(f'/conversations/restart/{self.base_chat.data["_id"]}/',
                                         **{"HTTP_AUTHORIZATION": f"Bearer {not_participant_token}"})
        self.assertEqual(post_response.status_code, 403)
        self.assertEqual(post_response.data["message"], "You are not the participant of this live-chat")

    def tearDown(self):
        self.mock_conversations.stop()
        self.mock_redis.stop()

    @classmethod
    def tearDownClass(cls):
        client = MongoClient('localhost', 27017)
        client.drop_database('livechats')
