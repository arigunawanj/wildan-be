from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from customers.models import Customer
from products.models import Product
from .models import Order


class OrderApiTests(APITestCase):
    def setUp(self):
        self.sales = User.objects.create_user('sales1', password='p', role=User.Role.SALES)
        self.gudang = User.objects.create_user('gudang1', password='p', role=User.Role.GUDANG)
        self.customer = Customer.objects.create(name='Toko A', type='retail', phone='0800')
        self.product = Product.objects.create(
            name='Vinyl Oak', category='vinyl', unit='m2', stock=50, price='100000'
        )

    def test_sales_can_create_order(self):
        self.client.force_authenticate(self.sales)
        res = self.client.post(reverse('order-list'), {
            'customer': self.customer.id,
            'items': [{'product_id': self.product.id, 'quantity': 5}],
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['status'], 'pending')
        self.assertEqual(len(res.data['items']), 1)

    def test_gudang_cannot_create_order(self):
        self.client.force_authenticate(self.gudang)
        res = self.client.post(reverse('order-list'), {
            'customer': self.customer.id,
            'items': [{'product_id': self.product.id, 'quantity': 5}],
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_gudang_can_read_orders(self):
        self.client.force_authenticate(self.sales)
        self.client.post(reverse('order-list'), {
            'customer': self.customer.id,
            'items': [{'product_id': self.product.id, 'quantity': 5}],
        }, format='json')

        self.client.force_authenticate(self.gudang)
        res = self.client.get(reverse('order-list'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 1)

    def test_insufficient_stock_returns_400(self):
        self.client.force_authenticate(self.sales)
        res = self.client.post(reverse('order-list'), {
            'customer': self.customer.id,
            'items': [{'product_id': self.product.id, 'quantity': 999}],
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cancel_order_via_status_endpoint(self):
        self.client.force_authenticate(self.sales)
        create_res = self.client.post(reverse('order-list'), {
            'customer': self.customer.id,
            'items': [{'product_id': self.product.id, 'quantity': 5}],
        }, format='json')
        order_id = create_res.data['id']

        status_res = self.client.patch(
            reverse('order-set-status', args=[order_id]), {'status': 'dibatalkan'}, format='json'
        )
        self.assertEqual(status_res.status_code, status.HTTP_200_OK)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 50)

    def test_stats_endpoint(self):
        self.client.force_authenticate(self.sales)
        self.client.post(reverse('order-list'), {
            'customer': self.customer.id,
            'items': [{'product_id': self.product.id, 'quantity': 5}],
        }, format='json')

        res = self.client.get(reverse('order-stats'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['orders_this_month'], 1)
        self.assertEqual(res.data['pending_orders'], 1)
