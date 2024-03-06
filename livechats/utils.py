import os
from pymongo import MongoClient


def mongo_conversations():
    """connecting to MangoDB and getting conversations data"""
    client = MongoClient(os.environ.get("MONGO_URL"))
    collections = client.livechats.conversations
    return collections
