from django.db import models
from django.contrib.auth.models import User

#* ===== USER ACCOUNTS MODELS ===== *#
class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)