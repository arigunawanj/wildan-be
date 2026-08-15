from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from .models import Customer


class CustomerApiTests(APITestCase):
    def setUp(self):
        self.sales = User.objects.create_user('sales1', password='p', role=User.Role.SALES)
        self.gudang = User.objects.create_user('gudang1', password='p', role=User.Role.GUDANG)
        self.customer = Customer.objects.create(
            name='Toko Jaya Bangunan', type='retail', phone='08123', city='Jakarta',
        )

    def test_sales_can_create(self):
        self.client.force_authenticate(self.sales)
        res = self.client.post(reverse('customer-list'), {
            'name': 'CV Sukses Kontraktor', 'type': 'kontraktor', 'phone': '08129',
        })
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_gudang_can_read_but_not_create(self):
        self.client.force_authenticate(self.gudang)
        list_res = self.client.get(reverse('customer-list'))
        self.assertEqual(list_res.status_code, status.HTTP_200_OK)

        create_res = self.client.post(reverse('customer-list'), {
            'name': 'Toko X', 'type': 'retail', 'phone': '0800',
        })
        self.assertEqual(create_res.status_code, status.HTTP_403_FORBIDDEN)
