from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        SALES = 'sales', 'Sales'
        GUDANG = 'gudang', 'Gudang'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.SALES)

    def __str__(self):
        return f'{self.username} ({self.role})'
