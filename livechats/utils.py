
from forum.settings import DB


def mongo_conversations():
    """connecting to MangoDB and getting conversations data"""
    collections = DB['conversations']
    return collections
