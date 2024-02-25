import os

from pymongo import MongoClient


def mongo_conversations():
    client = MongoClient(os.environ.get("MONGODB_HOST"))
    collections = client.livechats.conversations
    return collections
