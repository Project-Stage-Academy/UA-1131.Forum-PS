from django.urls import path
from . import views

urlpatterns = [
    path('', views.CompaniesListCreateView.as_view(), name='companies-list-create'),
    path('<int:pk>/', views.CompaniesRetrieveView.as_view(), name='companies-retrieve-update'),
    path('subscribe/', views.SubscriptionCreateAPIView.as_view(), name='subscription-create'),
    path('unsubscribe/<int:subscription_id>/', views.UnsubscribeAPIView.as_view(), name='unsubscribe'),
    path('subscriptions/', views.SubscriptionListView.as_view(), name='subscriptionsList'),
    path('create_article/', views.CreateArticle.as_view(), name='create_article'),
    path('get_article/<int:pk>/<int:page>/', views.RetrieveArticles.as_view(), name='get_article'),
    path('delete_article/<str:art_id>/', views.DeleteArticle.as_view(), name='delete_article'),
    path('update_article/<str:art_id>/', views.UpdateArticle.as_view(), name='update_article'),
]

