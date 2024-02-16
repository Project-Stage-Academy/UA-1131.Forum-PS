from django.urls import path
from authentication import views
from authentication.views import PasswordRecoveryAPIView, PasswordResetView

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name="auth_register"),
    path('email_verify/', views.VerifyEmail.as_view(), name="email_verify"),
    path('users/<int:pk>/', views.UserUpdateView.as_view(), name="user_details"),
    path('users/<int:pk>/password_update/', views.UserPasswordUpdateView.as_view(), name="user_pass_update"),
    path('password_recovery/', PasswordRecoveryAPIView.as_view(), name='password_recovery'),
    path('password-reset/<str:jwt_token>/', PasswordResetView.as_view(), name='password_reset'),
]
