from django.urls import path

from password_recovery.views import PasswordRecoveryAPIView, PasswordResetView

urlpatterns = [
    path('password_recovery/', PasswordRecoveryAPIView.as_view(), name='password_recovery'),
    path('password-reset/<str:jwt_token>/', PasswordResetView.as_view(), name='password_reset'),
]
