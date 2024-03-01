from django.urls import path
from authentication import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name="auth_register"),
    path('relate/', views.RelateUserToCompany.as_view(), name="relate"),
    path('email_verify/', views.VerifyEmail.as_view(), name="email_verify"),
    path('users/<int:pk>/', views.UserUpdateView.as_view(), name="user_details"),
    path('users/<int:pk>/password_update/', views.UserPasswordUpdateView.as_view(), name="user_pass_update"),
]
