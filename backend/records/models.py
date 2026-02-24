from django.db import models
from django.conf import settings
from semantic.models import semanticConcept
# Create your models here.

class Records(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name = 'records')
    raw_label = models.CharField(max_length=255)
    semantic_concept = models.ForeignKey(
        semanticConcept,
        on_delete=models.PROTECT,
        related_name="records"
    )
    amount = models.DecimalField(max_digits=10 , decimal_places=2)
    spent_at = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.raw_label} - {self.user} - {self.amount}"