from .views import UserCreateAPIView, LogoutAPIView
from django.urls import path

urlpatterns = [
    path('register/', UserCreateAPIView.as_view(), name = 'Register user'),
    path('logout/', LogoutAPIView.as_view(), name = 'Logout user'),
]