from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view

from companies.urls import router as company_router

urlpatterns = [
    path('api_schema/', get_schema_view(title="API Schema", description='Forum API'), name='api_schema'),
    path('docs/', TemplateView.as_view(
        template_name='docs.html',
        extra_context={'schema_url':'api_schema'}
        ), name='swagger-ui'),
    path('admin/', admin.site.urls),
    path('auth/', include('authentication.urls')),
    path('companies/', include('companies.urls')),
    path('conversations/', include('livechats.urls')),
    path('messages/', include('chats.urls')),
    path('search/', include('search.urls')),
    path('notifications/', include('notifications.urls'))
]

urlpatterns += company_router.urls

