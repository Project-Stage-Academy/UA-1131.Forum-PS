from django.db import models
from rest_framework.exceptions import ValidationError

from companies.models import Companies


# Create your models here.
class Chat(models.Model):
    participants = models.ManyToManyField(Companies, related_name='chats')
    subject = models.TextField(default=" ", null=True)

    def __str__(self):
        return f"{self.subject}  {self.participants}"


class Message(models.Model):
    message_id = models.BigAutoField(primary_key=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages", null=True)
    sender = models.ForeignKey(Companies, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(Companies, on_delete=models.CASCADE, related_name='received_messages')
    visible_for_sender = models.BooleanField(default=True)
    visible_for_recipient = models.BooleanField(default=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.sender == self.recipient:
            raise ValidationError("Sender and recipient cannot be the same.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
