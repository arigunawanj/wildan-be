from django.db import models


class Product(models.Model):
    class Category(models.TextChoices):
        VINYL = 'vinyl', 'Vinyl'
        HPL = 'hpl', 'HPL'
        HARDWARE = 'hardware', 'Hardware'

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=10, choices=Category.choices)
    unit = models.CharField(max_length=50)
    stock = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    low_stock_threshold = models.PositiveIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
