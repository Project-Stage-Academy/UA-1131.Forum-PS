from django.urls import path
from .views import CompaniesRetrieveUpdateView, SubscriptionCreateAPIView, UnsubscribeAPIView, SubscriptionListView

urlpatterns = [
    path('<int:pk>/', CompaniesRetrieveUpdateView.as_view(), name='companies-retrieve-update'),
    path('subscribe/', SubscriptionCreateAPIView.as_view(), name='subscription-create'),
    path('unsubscribe/<int:subscription_id>/', UnsubscribeAPIView.as_view(), name='unsubscribe'),
    path('subscriptions/', SubscriptionListView.as_view(), name='subscriptionsList'),
]
