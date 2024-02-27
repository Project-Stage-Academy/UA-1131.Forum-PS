from django.urls import path
from . import views

urlpatterns = [
    path('start/', views.StartConversation.as_view(), name='start_conversation'),
    path('<str:convo_id>/', views.GetConversations.as_view(), name='get_conversation'),
    path('', views.ConversationsList.as_view(), name='conversations'),
    path('restart/<str:convo_id>/', views.EmergencyConversationRestart.as_view(), name='restart_conversation'),
]