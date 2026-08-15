from django.db import transaction
from products.models import Product
from .models import Order, OrderItem


class InsufficientStockError(Exception):
    def __init__(self, product_name, requested, available):
        self.product_name = product_name
        self.requested = requested
        self.available = available
        super().__init__(
            f'Stok "{product_name}" tidak cukup: diminta {requested}, tersedia {available}'
        )


@transaction.atomic
def create_order(customer_id: int, items: list[dict], created_by) -> Order:
    order = Order.objects.create(customer_id=customer_id, created_by=created_by)

    for item in items:
        product = Product.objects.select_for_update().get(id=item['product_id'])
        quantity = item['quantity']
        if product.stock < quantity:
            raise InsufficientStockError(product.name, quantity, product.stock)

        OrderItem.objects.create(
            order=order, product=product, quantity=quantity, price_at_order=product.price,
        )
        product.stock -= quantity
        product.save(update_fields=['stock'])

    return order


@transaction.atomic
def cancel_order(order: Order) -> Order:
    if order.status == Order.Status.DIBATALKAN:
        return order

    for item in order.items.select_related('product').select_for_update():
        product = item.product
        product.stock += item.quantity
        product.save(update_fields=['stock'])

    order.status = Order.Status.DIBATALKAN
    order.save(update_fields=['status'])
    return order
