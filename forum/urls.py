from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from authentication.views import LoginView, LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('messages/', include('chats.urls')),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/login", LoginView.as_view(), name='login'),
    path("api/logout", LogoutView.as_view(), name='logout'), 
    path('companies/', include('companies.urls')),
    path('notifications/', include('notifications.urls'))
]
