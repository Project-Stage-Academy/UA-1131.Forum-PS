from bson import ObjectId
from pydantic import BaseModel, ValidationError
from forum.settings import DB


class MessageNotFound(Exception):
    pass


class MessageGroupNotFound(Exception):
    pass


class Message(BaseModel):
    """Pydentic BaseModel class for Messages validations"""
    msg_text: str
    msg_topic: str
    timestamp: str
    sender_id: int
    sender_data: str
    receiver_id: int
    receiver_data: str
    visible_for_sender: bool
    visible_for_receiver: bool


class MongoManager:

    @classmethod
    def id_to_string(cls, document):
        """Changes _id field of returned document from ObjectId to string."""

        document['_id'] = str(document['_id'])
        return document

    @classmethod
    def to_list(cls, cursor):
        """Returns the list of objects from the PyMongo cursor."""

        res = []
        for el in cursor:
            res.append(cls.id_to_string(el))
        return res


class MessagesManager(MongoManager):
    db = DB['long_term_messages']

    @classmethod
    def get_messages_to_company(cls, company_id):
        cursor = cls.db.find({"$or": [
            {"sender_id": company_id},
            {"receiver_id": company_id}]},
            {"visible_for_receiver": 0, "visible_for_sender": 0}
        )
        if not cursor:
            raise MessageGroupNotFound("No massage with this company")
        existing_messages = cls.to_list(cursor)
        return existing_messages

    @classmethod
    def get_message(cls, message_id):
        if ObjectId.is_valid(message_id):
            existing_message = cls.db.find_one({"_id": ObjectId(message_id)})
            if not existing_message:
                raise MessageNotFound("Message not found")
            existing_message = cls.id_to_string(existing_message)
            return existing_message
        raise ValidationError("Invalid message_id")

    @classmethod
    def delete_message(cls, company_id, message_id):
        query = {"_id": ObjectId(message_id)}
        message = cls.get_message(message_id)
        result = ""
        if message.get("sender_id") == company_id:
            result = cls.db.find_one_and_update(query, {"$set": {"visible_for_sender": False}})
        if message.get("receiver_id") == company_id:
            result = cls.db.find_one_and_update(query, {"$set": {"visible_for_receiver": False}})
        if not message.get("visible_for_sender") and not message.get("visible_for_receiver"):
            result = cls.db.find_one_and_delete(query)
        return result

    @classmethod
    def create_message(cls, message):
        cls.db.insert_one(message.model_dump())
        return message.dict()

    @classmethod
    def company_inbox_messages(cls, company_id):
        cursor = cls.db.find({"$and":
                                  [{"receiver_id": company_id},
                                   {"visible_for_receiver": True}]},
                             {"visible_for_receiver": 0, "visible_for_sender": 0})
        return cls.to_list(cursor)

    @classmethod
    def company_outbox_messages(cls, company_id):
        cursor = cls.db.find({"$and":
                                  [{"sender_id": company_id},
                                   {"visible_for_sender": True}]},
                             {"visible_for_receiver": 0, "visible_for_sender": 0})
        return cls.to_list(cursor)
