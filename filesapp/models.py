from django.db import models
from django.contrib.auth.models import User

class UploadedFile(models.Model):
    FILE_TYPES = (
        ('rozvaha', 'Rozvaha'),
        ('vysledovka', 'Výsledovka'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to="pdf/")
    year = models.IntegerField(default=2025)
    file_type = models.CharField(max_length=20, choices=FILE_TYPES, default="rozvaha")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.file_type} ({self.year})"
