from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import User


class AuthTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='sales1', password='pass12345', role=User.Role.SALES
        )

    def test_login_returns_tokens_and_user(self):
        res = self.client.post(reverse('auth-login'), {
            'username': 'sales1', 'password': 'pass12345',
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)
        self.assertEqual(res.data['user']['role'], 'sales')

    def test_login_wrong_password_rejected(self):
        res = self.client.post(reverse('auth-login'), {
            'username': 'sales1', 'password': 'wrong',
        })
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_requires_auth(self):
        res = self.client.get(reverse('auth-me'))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_current_user(self):
        login = self.client.post(reverse('auth-login'), {
            'username': 'sales1', 'password': 'pass12345',
        })
        access = login.data['access']
        res = self.client.get(
            reverse('auth-me'), HTTP_AUTHORIZATION=f'Bearer {access}'
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['username'], 'sales1')

    def test_logout_blacklists_refresh_token(self):
        login = self.client.post(reverse('auth-login'), {
            'username': 'sales1', 'password': 'pass12345',
        })
        refresh = login.data['refresh']
        logout_res = self.client.post(reverse('auth-logout'), {'refresh': refresh})
        self.assertEqual(logout_res.status_code, status.HTTP_205_RESET_CONTENT)

        refresh_res = self.client.post(reverse('auth-refresh'), {'refresh': refresh})
        self.assertEqual(refresh_res.status_code, status.HTTP_401_UNAUTHORIZED)
