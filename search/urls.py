from django.urls import path

from .views import SearchCompanyView

APP_NAME = "search"

urlpatterns = [
    path(
        '', SearchCompanyView.as_view(), name="search-company"
    ),
]
