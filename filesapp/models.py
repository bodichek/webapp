from django.db import models
from django.contrib.auth.models import User

class FinancialFile(models.Model):
    FILE_TYPES = (
        ('rozvaha', 'Rozvaha'),
        ('vysledovka', 'Výkaz zisku a ztráty'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.IntegerField()
    file_type = models.CharField(max_length=20, choices=FILE_TYPES)
    file = models.FileField(upload_to='pdf/')
    csv_file = models.FileField(upload_to="csv/", blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

class FinancialRow(models.Model):
    """
    Tabulka pro jednotlivé řádky finančních výkazů (po konverzi z PDF/CSV).
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.ForeignKey(FinancialFile, on_delete=models.CASCADE, related_name="rows")
    year = models.IntegerField()
    line = models.CharField(max_length=10)   # číslo řádku (např. "01", "05", "40")
    description = models.TextField(blank=True, null=True)
    value = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.year} | {self.line} | {self.value}"
    
class FinancialAnalysis(models.Model):
    FILE_TYPES = (
        ('rozvaha', 'Rozvaha'),
        ('vysledovka', 'Výkaz zisku a ztráty'),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="financial_analyses"   # 👈 sjednocený název
    )
    year = models.IntegerField()
    file_type = models.CharField(max_length=20, choices=FILE_TYPES)
    key = models.CharField(max_length=255)   # sjednoceno na delší rozsah
    value = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'year', 'file_type', 'key')
        verbose_name = "Financial Analysis"
        verbose_name_plural = "Financial Analyses"

    def __str__(self):
        return f"{self.user.username} | {self.year} | {self.file_type} | {self.key}: {self.value}"