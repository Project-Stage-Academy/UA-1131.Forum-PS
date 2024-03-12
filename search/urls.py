from django.urls import path

from search.views import SearchCompanyView

app_name = "search"

urlpatterns = [
    path(
        '', SearchCompanyView.as_view(), name="search-company"
    ),
]
