from django.db import models

from authentication.models import CustomUser


# Create your models here.

class Conversation(models.Model):
    initiator = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="convo_starter"
    )
    receiver = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="convo_participant"
    )
    start_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation _ {self.pk}"


class Message(models.Model):
    sender = models.ForeignKey(CustomUser, on_delete=models.SET_NULL,
                               null=True, related_name='message_sender')
    text = models.CharField(max_length=200, blank=True)
    conversation_id = models.ForeignKey(Conversation, on_delete=models.CASCADE, )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
