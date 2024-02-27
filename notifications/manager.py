from datetime import datetime, timedelta
import pymongo
from bson import ObjectId
from typing import List, Dict
from datetime import date
from pydantic import BaseModel, Field, ValidationError
from forum.settings import DB

UPDATE = 'update'
MESSAGE = 'message'

class AlreadyExist(Exception):
    pass
class NoNotificationsFound(Exception):
    pass
class InvalidData(Exception):
    pass


class Viewed(BaseModel):
    user_id:int
    viewed_at:str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class Notification(BaseModel):
    created_at:str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    concerned_users:List = Field(default=[])
    viewed_by:List[Dict[str, Viewed]] = Field(default=[])
    event_id: int

class UpdateNotification(Notification):
    type:str = Field(default=UPDATE, frozen=True)

class MessageNotification(Notification):
    type:str = Field(default=MESSAGE, frozen=True)
    


class NotificationManager:
    """
    NotificationManager is responsible for database interactions, including data validating  
    and serializing, errors handling and retrieved data formatting. To register your model 
    in manager you have to include it in types collection, with type as a key and model
    as a value
    """
    UPDATE = 'update'
    MESSAGE = 'message'
    
    db = DB['Notification']
    types = {UPDATE: UpdateNotification,
             MESSAGE: MessageNotification}
    
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
    
    @classmethod
    def get_notification_by_query(cls, query):
        """Extracting the single document from database filtered by given query."""

        notification = cls.db.find_one(query)
        if not notification:
            raise NoNotificationsFound(f"Notification not found")
        return cls.id_to_string(notification)
    
    @classmethod
    def get_notifications_by_query(cls, query, err=None):
        """Extracting the multiple documents from database filtered by given query."""

        err = "There is no notifications that satisfy given conditions" if not err else err
        if not cls.db.count_documents(query):
            raise NoNotificationsFound(err)
        notifications = cls.db.find(query).sort('created_at', pymongo.ASCENDING)
        if not notifications:
            raise NoNotificationsFound(f"Notifications not found, perhaps due the connection error.")
        return cls.to_list(notifications)
    
    @classmethod
    def delete_notification_by_query(cls, query):
        """Delete notification that matches to given conditions."""

        notification = cls.db.find_one_and_delete(query)
        if not notification:
            raise NoNotificationsFound(f"Notification not found")
        return cls.id_to_string(notification)
    
    @classmethod
    def delete_old_notifications(cls):
        """Deleted notifications that are 30 days older than current date."""

        date = datetime.now() - timedelta(days=30)
        date = date.strftime("%Y-%m-%d %H:%M:%S")
        query = {"created_at": {"$lt": date}}
        res = cls.db.delete_many(query)
        return res.deleted_count
    
    @classmethod
    def create_notification(cls, data):
        """
        Creating and stores into the database notification with id of the event that triggered 
        the notification's creation (for instance update_id or chat_id) and other defined in the model
        information. Data should include type and event_id. 
        """
        type = data['type']
        model = cls.types[type]
        event_id = data['event_id']
        query = {'event_id': event_id}
        if cls.db.count_documents(query):
            raise AlreadyExist(f"Notification for {type} with EVENT_ID {event_id} already exists.")
        validated_model = model.model_validate(data)
        res = cls.db.insert_one(validated_model.model_dump())
        return str(res.inserted_id)
    
    @classmethod
    def create_notifications(cls, data:list):
        """Creting notifications from the array of data."""

        res = []
        for nf in data:
            try:
                id = cls.create_notification(nf)
                res.append(id)
            except AlreadyExist:
                continue
        return res
    
    @classmethod
    def extract_notifications_for_user(cls, u_id):
        """Extracting all the notifications that are regarded to user."""

        query = {'concerned_users': u_id}
        err_msg = f"There is no notifications for the user with ID {u_id}."
        return cls.get_notifications_by_query(query, err=err_msg)

    @classmethod
    def extract_notifications_by_type(cls, type):
        """Extracting all notifications of given type."""

        query = {'type': type}
        err_msg = f"There is no notifications of type <{type}>."
        return cls.get_notifications_by_query(query, err=err_msg)

    @classmethod
    def store_viewed_user(cls, nf_id, u_id):
        """
        This method stores user id in viewed_by field along with the time of viewing.
        """
        query = {'$and': [{'_id': ObjectId(nf_id)}, {'concerned_users': u_id}]}
        notification = cls.get_notification_by_query(query)
        if any(viewed['user_id'] == u_id for viewed in notification.get('viewed_by', [])):
            raise AlreadyExist(f"User with ID {u_id} already viewed this notification")
        try:
           viewed = Viewed.model_validate({'user_id': u_id})
        except ValidationError as e:
            raise InvalidData(str(e))
        update = {'$push': {'viewed_by': viewed.model_dump()}}
        notification = cls.db.find_one_and_update(query, update, return_document=pymongo.ReturnDocument.AFTER)
        if not notification:
            raise NoNotificationsFound(f"Notification not found, perhaps due the connection error.")
        return cls.id_to_string(notification)
    



    

        



    


