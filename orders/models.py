from django.conf import settings
from django.db import models
from django.utils import timezone


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        DIPROSES = 'diproses', 'Diproses'
        SELESAI = 'selesai', 'Selesai'
        DIBATALKAN = 'dibatalkan', 'Dibatalkan'

    order_number = models.CharField(max_length=30, unique=True, blank=True)
    customer = models.ForeignKey('customers.Customer', on_delete=models.PROTECT, related_name='orders')
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            today = timezone.now().strftime('%Y%m%d')
            prefix = f'ORD-{today}-'
            last = (
                Order.objects.filter(order_number__startswith=prefix)
                .order_by('-order_number')
                .first()
            )
            next_seq = int(last.order_number[-4:]) + 1 if last else 1
            self.order_number = f'{prefix}{next_seq:04d}'
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('products.Product', on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price_at_order = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f'{self.product.name} x{self.quantity}'
