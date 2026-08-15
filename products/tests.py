from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from .models import Product


class ProductApiTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user('admin1', password='p', role=User.Role.ADMIN)
        self.sales = User.objects.create_user('sales1', password='p', role=User.Role.SALES)
        self.gudang = User.objects.create_user('gudang1', password='p', role=User.Role.GUDANG)
        self.product = Product.objects.create(
            name='Vinyl Oak 3mm', category='vinyl', unit='m2', stock=100, price='150000'
        )

    def test_sales_can_read_but_not_create(self):
        self.client.force_authenticate(self.sales)
        list_res = self.client.get(reverse('product-list'))
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)

        create_res = self.client.post(reverse('product-list'), {
            'name': 'HPL White', 'category': 'hpl', 'unit': 'lembar',
            'stock': 50, 'price': '80000',
        })
        self.assertEqual(create_res.status_code, status.HTTP_403_FORBIDDEN)

    def test_gudang_can_create(self):
        self.client.force_authenticate(self.gudang)
        res = self.client.post(reverse('product-list'), {
            'name': 'Engsel Pintu', 'category': 'hardware', 'unit': 'pcs',
            'stock': 200, 'price': '15000',
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_admin_can_delete(self):
        self.client.force_authenticate(self.admin)
        res = self.client.delete(reverse('product-detail', args=[self.product.id]))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_unauthenticated_rejected(self):
        res = self.client.get(reverse('product-list'))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
