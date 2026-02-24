from django.db import models
from django.conf import settings


# Extend the Django.contrib User model.
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    currency = models.CharField(max_length=5)

    def __str__(self):
        return f"{self.user.username} - {self.currency}"

class Wallet(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet"
    )

    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user} - Balance: {self.balance}"