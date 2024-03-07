from django.urls import path
from chats import views

urlpatterns = [
    path('send_message/', views.SendMessage.as_view(), name="send_message"),
    path('details/<str:message_id>/', views.MessageDetail.as_view(), name="message_details"),
    path('delete/<str:message_id>/', views.MessageDeleteView.as_view(), name="message_delete"),

]
