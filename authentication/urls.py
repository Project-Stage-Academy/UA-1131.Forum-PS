from django.urls import path
from authentication import views


urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name="auth_register"),
    path('email_verify/', views.VerifyEmail.as_view(), name="email_verify"),
]
