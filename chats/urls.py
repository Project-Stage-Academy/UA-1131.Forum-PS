from django.urls import path
from chats import views

urlpatterns = [
    path('send_message/', views.SendMessage.as_view(), name="send_message"),
    path('chat/<int:pk>/', views.ChatList.as_view(), name="list_chat"),
    path('inbox/', views.InboxView.as_view(), name="inbox"),

]