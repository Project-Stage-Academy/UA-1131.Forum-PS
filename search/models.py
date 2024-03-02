from django.db import models

from authentication.models import CustomUser


class SavedCompany(models.Model):
    company_id = models.IntegerField()

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="saved_list_items"
    )
    added_at = models.DateTimeField(auto_now_add=True)
