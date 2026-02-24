from django.urls import path 
from .views import ChatView

urlpatterns = [
    path('intent-test/', ChatView.as_view(), name="intent-test")
]