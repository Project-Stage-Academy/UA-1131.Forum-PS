from django.urls import path
from rest_framework_simplejwt.views import TokenObtainSlidingView, TokenRefreshSlidingView

from authentication import views

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view(), name="auth_register"),
    path('email_varify/', views.VarifyEmail.as_view(), name="email_varify"),
    path('api/token/', TokenObtainSlidingView.as_view(), name='token_obtain'),
    path('api/token/refresh/', TokenRefreshSlidingView.as_view(), name='token_refresh'),
]
