from rest_framework.permissions import BasePermission

from authentication.models import CompanyAndUserRelation



class MessageParticipantPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        user_id = request.user.id

        sender_company_ids = CompanyAndUserRelation.objects.filter(user_id=user_id)

        message_participants = [obj.sender, obj.recipient]
        return any(participant in sender_company_ids for participant in message_participants)


class ChatParticipantPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        user_id = request.user.id

        sender_company_ids = CompanyAndUserRelation.objects.filter(user_id=user_id)


        return obj.participants.filter(company_id__in=sender_company_ids).exists()
