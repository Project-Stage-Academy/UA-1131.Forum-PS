from django.contrib import admin
from django.urls import path, include
from authentication.views import LoginView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.views import  TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('recovery/', include('password_recovery.urls')),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/login", LoginView.as_view(), name='login'),

]
