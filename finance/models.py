from django.db import models
from django.contrib.auth.models import User

class FinancialAnalysis(models.Model):
    FILE_TYPES = (
        ("rozvaha", "Rozvaha"),
        ("vysledovka", "Výsledovka"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.IntegerField()
    file_type = models.CharField(max_length=20, choices=FILE_TYPES)
    key = models.CharField(max_length=255)   # např. "Aktiva", "Pasiva"
    value = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} {self.year} {self.file_type} {self.key}: {self.value}"
