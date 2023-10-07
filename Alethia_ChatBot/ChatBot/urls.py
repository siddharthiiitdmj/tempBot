from django.urls import path
from .views import BotHandler

urlpatterns = [
    path('botquery', BotHandler.as_view())
]