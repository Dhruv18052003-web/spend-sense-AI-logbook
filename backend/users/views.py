from django.shortcuts import render
from .serializers import UserRegistrationSerializer
from rest_framework.generics import CreateAPIView
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from .serializers import LogoutSerializer
# Create your views here.

class UserCreateAPIView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import LogoutSerializer


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)

        if serializer.is_valid():
            try:
                refresh_token = serializer.validated_data['refresh']
                token = RefreshToken(refresh_token)
                token.blacklist()

                return Response(
                    {"message": "Logged out successfully"},
                    status=status.HTTP_205_RESET_CONTENT
                )
            except Exception:
                return Response(
                    {"error": "Invalid refresh token"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
