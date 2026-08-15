from rest_framework.test import APIRequestFactory
from django.test import TestCase
from .models import User
from .permissions import IsAdmin, IsAdminOrGudang, IsAdminOrSales


class PermissionTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User(username='a', role=User.Role.ADMIN)
        self.sales = User(username='s', role=User.Role.SALES)
        self.gudang = User(username='g', role=User.Role.GUDANG)

    def _req(self, user):
        request = self.factory.get('/')
        request.user = user
        return request

    def test_is_admin(self):
        perm = IsAdmin()
        self.assertTrue(perm.has_permission(self._req(self.admin), None))
        self.assertFalse(perm.has_permission(self._req(self.sales), None))

    def test_is_admin_or_gudang(self):
        perm = IsAdminOrGudang()
        self.assertTrue(perm.has_permission(self._req(self.admin), None))
        self.assertTrue(perm.has_permission(self._req(self.gudang), None))
        self.assertFalse(perm.has_permission(self._req(self.sales), None))

    def test_is_admin_or_sales(self):
        perm = IsAdminOrSales()
        self.assertTrue(perm.has_permission(self._req(self.admin), None))
        self.assertTrue(perm.has_permission(self._req(self.sales), None))
        self.assertFalse(perm.has_permission(self._req(self.gudang), None))
