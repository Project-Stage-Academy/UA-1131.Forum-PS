from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('companies', views.CompaniesViewSet, basename='companies')

urlpatterns = [
    path('get_company/<int:pk>/', views.CompanyRetrieveView.as_view(), name='get_company'),
    path('get_companies/', views.CompaniesRetrieveView.as_view(), name='get_companies'),
    path('subscribe/<int:pk>/', views.SubscriptionCreateAPIView.as_view(), name='subscription-create'),
    path('unsubscribe/<int:subscription_id>/', views.UnsubscribeAPIView.as_view(), name='unsubscribe'),
    path('subscriptions/', views.SubscriptionListView.as_view(), name='subscriptionsList'),
    path('create_article/', views.CreateArticle.as_view(), name='create_article'),
    path('get_article/<int:pk>/<int:page>/', views.RetrieveArticles.as_view(), name='get_article'),
    path('delete_article/<str:art_id>/', views.DeleteArticle.as_view(), name='delete_article'),
    path('update_article/<str:art_id>/', views.UpdateArticle.as_view(), name='update_article'),
]

