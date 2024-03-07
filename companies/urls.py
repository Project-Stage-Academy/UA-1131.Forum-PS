from django.urls import path
from .views import CompaniesViewSet, SubscriptionCreateAPIView, UnsubscribeAPIView, SubscriptionListView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('companies', CompaniesViewSet, basename='companies')

urlpatterns = [
    path('subscribe/', SubscriptionCreateAPIView.as_view(), name='subscription-create'),
    path('unsubscribe/<int:subscription_id>/', UnsubscribeAPIView.as_view(), name='unsubscribe'),
    path('subscriptions/', SubscriptionListView.as_view(), name='subscriptionsList'),
]
