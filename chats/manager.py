from bson import ObjectId
from pydantic import BaseModel, ValidationError
from forum.settings import DB
from forum.managers import MongoManager


class MessageNotFound(Exception):
    pass


class MessageGroupNotFound(Exception):
    pass


class Message(BaseModel):
    """Pydentic BaseModel class for Messages validations"""
    msg_text: str
    msg_topic: str
    timestamp: str
    sender_company_id: int
    sender_user_id: int
    sender_data: str
    receiver_company_id: int
    receiver_user_id: int
    receiver_data: str
    visible_for_sender: bool
    visible_for_receiver: bool


class MessagesManager(MongoManager):
    db = DB['long_term_messages']

    @classmethod
    def get_messages_to_company(cls, company_id):
        cursor = cls.db.find({"$or": [
            {"sender_company_id": company_id},
            {"receiver_company_id": company_id}]},
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
        if message.get("sender_company_id") == company_id:
            result = cls.db.find_one_and_update(query, {"$set": {"visible_for_sender": False}})
        if message.get("receiver_company_id") == company_id:
            result = cls.db.find_one_and_update(query, {"$set": {"visible_for_receiver": False}})
        check_message_to_delete = cls.get_message(message_id)
        if not check_message_to_delete.get("visible_for_sender") and not check_message_to_delete.get(
                "visible_for_receiver"):
            result = cls.db.find_one_and_delete(query)
        return result

    @classmethod
    def create_message(cls, message):
        new_message_id = cls.db.insert_one(message.model_dump()).inserted_id
        new_message = cls.get_message(new_message_id)
        return new_message

    @classmethod
    def company_inbox_messages(cls, company_id):
        cursor = cls.db.find({"$and":
                                  [{"receiver_company_id": company_id},
                                   {"visible_for_receiver": True}]},
                             {"visible_for_receiver": 0, "visible_for_sender": 0})
        return cls.to_list(cursor)

    @classmethod
    def company_outbox_messages(cls, company_id):
        cursor = cls.db.find({"$and":
                                  [{"sender_company_id": company_id},
                                   {"visible_for_sender": True}]},
                             {"visible_for_receiver": 0, "visible_for_sender": 0})
        return cls.to_list(cursor)
