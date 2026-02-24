from django.contrib.auth.models import User
from rest_framework import serializers
from decimal import Decimal

from .models import UserProfile, Wallet


class UserRegistrationSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(write_only=True, max_length=150)
    last_name = serializers.CharField(write_only=True, max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    currency = serializers.CharField(write_only=True, max_length=5)
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.01"),
        write_only=True
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "password",
            "currency",
            "amount",
        ]

    def create(self, validated_data):
        first_name = validated_data.pop("first_name")
        last_name = validated_data.pop("last_name")
        currency = validated_data.pop("currency")
        amount = validated_data.pop("amount")

        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            first_name=first_name,
            last_name=last_name,
        )

        UserProfile.objects.create(user=user, currency=currency)
        Wallet.objects.create(user=user, balance=amount)
        return user

    def validate_currency(self, value):
        cleaned = value.strip().upper()
        if not cleaned.isalpha() or not (3 <= len(cleaned) <= 5):
            raise serializers.ValidationError(
                "Currency must be 3-5 alphabetic characters, for example USD."
            )
        return cleaned


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()
