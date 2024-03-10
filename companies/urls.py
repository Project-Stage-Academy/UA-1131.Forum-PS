from django.urls import path
from . import views 

urlpatterns = [
    path('create_company/', views.CompaniesListCreateView.as_view(), name='create_company'),
    path('get_company/<int:pk>/', views.CompanyRetrieveView.as_view(), name='get_company'),
    path('get_companies/', views.CompaniesRetrieveView.as_view(), name='get_companies'),
    path('subscribe/<int:pk>/', views.SubscriptionCreateAPIView.as_view(), name='subscription-create'),
    path('unsubscribe/<int:subscription_id>/', views.UnsubscribeAPIView.as_view(), name='unsubscribe'),
    path('get_subscriptions/', views.SubscriptionListView.as_view(), name='get_subscriptions'),
]
