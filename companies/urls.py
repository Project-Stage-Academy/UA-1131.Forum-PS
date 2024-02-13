from django.urls import path
from .views import CompaniesListCreateView, CompaniesRetrieveUpdateView

urlpatterns = [
    path('', CompaniesListCreateView.as_view(), name='companies-list-create'),
    path('<int:pk>/', CompaniesRetrieveUpdateView.as_view(), name='companies-retrieve-update'),
]
