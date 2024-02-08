from django.urls import path
from authentication import views


urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name="auth_register"),
    path('email_varify/', views.VarifyEmail.as_view(), name="email_varify"),
]
