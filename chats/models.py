from django.db import models
from authentication.models import CustomUser
from companies.models import Companies


# Create your models here.
class Chat(models.Model):
    participants = models.ManyToManyField(Companies, related_name='chats')
    subject = models.TextField(default=" ", null=True)


class Message(models.Model):
    message_id = models.BigAutoField(primary_key=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages",null=True)
    sender = models.ForeignKey(Companies, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(Companies, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
