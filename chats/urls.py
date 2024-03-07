from django.urls import path
from chats import views

urlpatterns = [
    path('send_message/', views.SendMessageView.as_view(), name="send_message"),
    path('details/<str:message_id>/', views.MessageDetailView.as_view(), name="message_details"),
    path('delete/<str:message_id>/', views.MessageDeleteView.as_view(), name="message_delete"),
    path('inbox/', views.InboxView.as_view(), name="company_inbox"),
    path('outbox/', views.OutboxView.as_view(), name="company_outbox"),
    path('list/', views.ListMessagesView.as_view(), name="company_outbox"),

]
