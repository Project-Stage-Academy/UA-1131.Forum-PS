from rest_framework import serializers

from chats.models import (Chat, Message)

from authentication.models import CompanyAndUserRelation


class ParticipantSerializer(serializers.ModelSerializer):
    brand = serializers.SerializerMethodField()

    def get_brand(self, participant):
        return participant.company_id.brand if participant else None

    class Meta:

        model = CompanyAndUserRelation

        fields = ["relation_id", "brand", "company_id"]


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'recipient', 'content', 'timestamp']
        ordering = ['timestamp']

    def validate_sender(self, data):
        sender_id = self.context['request'].user.id

        sender_company_relations = CompanyAndUserRelation.objects.filter(user_id=sender_id)

        if not sender_company_relations.exists():
            raise serializers.ValidationError("You dont have companies in your list.")

        sender_company_ids = [relation.company_id for relation in sender_company_relations]
        sender_company_id = data.company_id
        if sender_company_id not in sender_company_ids:
            raise serializers.ValidationError("You are not allowed to send message")

        return data


class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ('id', 'participants', 'messages')


class MailboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'recipient', 'content', 'timestamp']
