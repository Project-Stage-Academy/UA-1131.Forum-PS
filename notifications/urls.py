from django.urls import path
from . import views

urlpatterns = [
    path('create_notification/', views.CreateNotification.as_view(), name="create_notification"),
    path('create_notifications/', views.CreateNotifications.as_view(), name="create_notifications"),
    path('get_notification/', views.GetNotifications.as_view(), name="get_notification"),
    path('delete_notifications/', views.DeleteNotifications.as_view(), name="delete_notification"),
    path('get_notification_by_type/', views.GetNotificationsByType.as_view(), name="get_notification_by_type"),
    path('notification_viewed/', views.NotificationViewed.as_view(), name="notification_viewed"),
]