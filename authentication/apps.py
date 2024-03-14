from django.apps import AppConfig


class AuthenticationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "authentication"

    def ready(self):
        from .signals import (log_user_logged_in_failed,
                              log_user_logged_in_success)
