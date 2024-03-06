import os
from pymongo import MongoClient
from forum.settings import DB


def mongo_conversations():
    """connecting to MangoDB and getting conversations data"""
<<<<<<< HEAD
    client = MongoClient(os.environ.get("MONGO_URL"))
    collections = client.livechats.conversations
=======
    collections = DB['conversations']
>>>>>>> d03a23617daf276dc005bcf525a39ebf482b1a0e
    return collections
