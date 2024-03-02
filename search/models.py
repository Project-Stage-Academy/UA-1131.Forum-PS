from django.db import models

from authentication.models import Company, CustomUser


class SavedCompany(models.Model):
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="saved_list"
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="saved_list_items"
    )
    added_at = models.DateTimeField(auto_now_add=True)
