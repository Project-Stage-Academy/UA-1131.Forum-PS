from django.urls import path
from chats import views

urlpatterns = [
    path('send_message/', views.SendMessage.as_view(), name="send_message"),
    path('<str:message_id>/', views.MessageDetail.as_view(), name="message_details"),
    path('delete/<str:message_id>/', views.MessageDeleteView.as_view(), name="message_delete"),
    path('inbox/', views.InboxView.as_view(), name="company_inbox"),
    path('outbox/', views.OutboxView.as_view(), name="company_outbox"),

]
