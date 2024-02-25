import os

from pymongo import MongoClient


def mongo_conversations():
    """connecting to MangoDB and getting conversations data"""
    client = MongoClient(os.environ.get("MONGODB_HOST"))
    collections = client.livechats.conversations
    return collections
