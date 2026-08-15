from django.test import TestCase
from accounts.models import User
from customers.models import Customer
from products.models import Product
from orders.models import Order
from orders.services import create_order, cancel_order, InsufficientStockError


class OrderServicesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('sales1', password='p', role=User.Role.SALES)
        self.customer = Customer.objects.create(name='Toko A', type='retail', phone='0800')
        self.product = Product.objects.create(
            name='Vinyl Oak', category='vinyl', unit='m2', stock=50, price='100000'
        )

    def test_create_order_decrements_stock(self):
        order = create_order(
            customer_id=self.customer.id,
            items=[{'product_id': self.product.id, 'quantity': 10}],
            created_by=self.user,
        )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 40)
        self.assertEqual(order.status, Order.Status.PENDING)
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().price_at_order, self.product.price)

    def test_create_order_rejects_insufficient_stock(self):
        with self.assertRaises(InsufficientStockError):
            create_order(
                customer_id=self.customer.id,
                items=[{'product_id': self.product.id, 'quantity': 999}],
                created_by=self.user,
            )
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 50, 'stock must be unchanged on rejection')

    def test_create_order_rolls_back_all_items_on_partial_failure(self):
        product2 = Product.objects.create(
            name='Engsel', category='hardware', unit='pcs', stock=5, price='10000'
        )
        with self.assertRaises(InsufficientStockError):
            create_order(
                customer_id=self.customer.id,
                items=[
                    {'product_id': self.product.id, 'quantity': 10},
                    {'product_id': product2.id, 'quantity': 999},
                ],
                created_by=self.user,
            )
        self.product.refresh_from_db()
        product2.refresh_from_db()
        self.assertEqual(self.product.stock, 50)
        self.assertEqual(product2.stock, 5)

    def test_cancel_order_restores_stock(self):
        order = create_order(
            customer_id=self.customer.id,
            items=[{'product_id': self.product.id, 'quantity': 10}],
            created_by=self.user,
        )
        cancel_order(order)
        self.product.refresh_from_db()
        order.refresh_from_db()
        self.assertEqual(self.product.stock, 50)
        self.assertEqual(order.status, Order.Status.DIBATALKAN)

    def test_cancel_already_cancelled_order_is_noop(self):
        order = create_order(
            customer_id=self.customer.id,
            items=[{'product_id': self.product.id, 'quantity': 10}],
            created_by=self.user,
        )
        cancel_order(order)
        cancel_order(order)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 50)
