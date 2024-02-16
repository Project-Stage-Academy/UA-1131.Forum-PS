from django.db.models import Q
from rest_framework import serializers
from chats.models import Chat, Message
from companies.models import Companies, CompaniesAndUsersRelations


class ParticipantSerializer(serializers.ModelSerializer):
    brand = serializers.SerializerMethodField()

    def get_brand(self, participant):
        return participant.brand if participant else None

    class Meta:
        model = Companies
        fields = ['company_id', 'brand']


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'recipient', 'content', 'timestamp']
        ordering = ['timestamp']

    def validate(self, data):
        sender_id = self.context['request'].user.id
        sender_company_relations = CompaniesAndUsersRelations.objects.filter(user_id=sender_id)

        if not sender_company_relations.exists():
            raise serializers.ValidationError("You dont have companies in your list.")

        sender_company_ids = [relation.company_id for relation in sender_company_relations]
        sender_company_id = data.get('sender')
        if sender_company_id not in sender_company_ids:
            raise serializers.ValidationError("You are not allowed to send message")

        return data

    def create(self, validated_data):
        participant_1 = validated_data["sender"]
        participant_2 = validated_data["recipient"]
        content = validated_data["content"]

        chat = Chat.objects.filter(participants=participant_1).filter(participants=participant_2)
        if not chat:
            chat = Chat.objects.create()
            chat.participants.add(participant_1, participant_2)

        message = Message.objects.create(chat=chat[0], sender=participant_1, recipient=participant_2,
                                         content=content)
        return message


class ChatSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    participants = ParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ('id', 'participants', 'messages')


class InboxSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"
