from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from authentication import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name="auth_register"),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('relate/<int:pk>/', views.RelateUserToCompany.as_view(), name="relate"),
    path('email_verify/', views.VerifyEmail.as_view(), name="email_verify"),
    path('users/<int:pk>/', views.UserUpdateView.as_view(), name="user_details"),
    path('users/<int:pk>/password_update/', views.UserPasswordUpdateView.as_view(), name="user_pass_update"),
    path('password-reset/<str:jwt_token>/', views.PasswordResetView.as_view(), name='password_reset'),
    path('password_recovery/', views.PasswordRecoveryAPIView.as_view(), name='password_recovery'),
]