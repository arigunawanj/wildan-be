from django.db import models


class Customer(models.Model):
    class Type(models.TextChoices):
        RETAIL = 'retail', 'Retail'
        KONTRAKTOR = 'kontraktor', 'Kontraktor'

    name = models.CharField(max_length=200)
    type = models.CharField(max_length=10, choices=Type.choices)
    phone = models.CharField(max_length=30)
    address = models.TextField(blank=True)
    pic_name = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=100, blank=True)
    province = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
