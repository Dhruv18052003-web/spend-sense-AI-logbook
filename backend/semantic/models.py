from django.db import models

# Create your models here.
class semanticConcept(models.Model):
    semantic_id = models.CharField(max_length=100, unique= True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.semantic_id