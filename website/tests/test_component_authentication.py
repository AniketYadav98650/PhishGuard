
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class AuthenticationComponentTests(TestCase):

    def setUp(self):
        self.login_url = reverse("login")
        self.home_url = reverse("home")

        self.user = User.objects.create_user(
            username="auth_tester",
            password="TestPassword123!"
        )

    def test_valid_credentials_authenticate_user(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "auth_tester",
                "password": "TestPassword123!"
            }
        )

        self.assertRedirects(response, self.home_url)

        self.assertIn(
            "_auth_user_id",
            self.client.session
        )

        self.assertEqual(
            int(self.client.session["_auth_user_id"]),
            self.user.pk
        )

    def test_invalid_password_is_rejected(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "auth_tester",
                "password": "WrongPassword123!"
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertNotIn(
            "_auth_user_id",
            self.client.session
        )

        self.assertTrue(response.context["form"].errors)

    def test_missing_credentials_are_rejected(self):
        response = self.client.post(
            self.login_url,
            {
                "username": "",
                "password": ""
            }
        )

        self.assertEqual(response.status_code, 200)

        self.assertNotIn(
            "_auth_user_id",
            self.client.session
        )

        self.assertTrue(response.context["form"].errors)

        self.assertIn(
            "username",
            response.context["form"].errors
        )

        self.assertIn(
            "password",
            response.context["form"].errors
        )
