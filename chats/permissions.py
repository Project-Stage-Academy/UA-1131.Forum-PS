from rest_framework.permissions import BasePermission
from companies.models import CompaniesAndUsersRelations


class MessageParticipantPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        user_id = request.user.id
        sender_company_ids = CompaniesAndUsersRelations.objects.filter(user_id=user_id).values_list('company_id',
                                                                                                    flat=True)
        message_participants = [obj.sender.company_id, obj.recipient.company_id]
        return any(participant in sender_company_ids for participant in message_participants)


class ChatParticipantPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        user_id = request.user.id
        sender_company_ids = CompaniesAndUsersRelations.objects.filter(user_id=user_id).values_list('company_id',
                                                                                                    flat=True)

        return obj.participants.filter(company_id__in=sender_company_ids).exists()
