from django.urls import path
from . import views

urlpatterns = [
    path('chat/', views.chat, name='chat'),
    path('health/', views.health, name='health'),
    # Add a simple health check without database dependency
    path('health-simple/', views.health_check, name='health_simple'),
]