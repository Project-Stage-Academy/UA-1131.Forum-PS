from django.urls import path
from authentication import views
from authentication.views import PasswordRecoveryAPIView, PasswordResetView

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name="auth_register"),
    path('relate/', views.RelateUserToCompany.as_view(), name="relate"),
    path('email_verify/<str:jwt_token>', views.VerifyEmail.as_view(), name="email_verify"),
    path('users/<int:pk>/', views.UserUpdateView.as_view(), name="user_details"),
    path('password_recovery/', PasswordRecoveryAPIView.as_view(), name='password_recovery'),
    path('password-reset/<str:jwt_token>/', PasswordResetView.as_view(), name='password_reset'),
]
