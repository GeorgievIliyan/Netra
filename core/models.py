from datetime import date, datetime, timezone

from django.db import models
from django.contrib.auth.models import User

#* ===== USER ACCOUNTS MODELS ===== *#
class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
        ('saving', 'Saving')
    ]

    type = models.CharField(
        max_length=7,
        choices=TRANSACTION_TYPES,
        default='income'
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='value'
    )
    date = models.DateField(null=True, blank=True, auto_now_add=True)
    date_time = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    title = models.CharField(null=True, blank=True, max_length=50)
    description = models.TextField(null=True, blank=True, max_length=300)

    def save(self, *args, **kwargs):
        if not self.date_time:
            self.date_time = timezone.now()
        if not self.title:
            self.title = f"New {self.type.capitalize()} log at {self.date_time.strftime('%Y-%m-%d %H:%M:%S')}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.type.capitalize()}: {self.title or self.value}"