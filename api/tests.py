from django.test import TestCase
from rest_framework.test import APIClient


class PublicApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_health_endpoint(self):
        response = self.client.get("/api/health/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_product_list_is_public(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.json())

    def test_category_list_is_public(self):
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_unknown_product_returns_404(self):
        response = self.client.get("/api/products/does-not-exist/")
        self.assertEqual(response.status_code, 404)


class AuthenticationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient(enforce_csrf_checks=True)

    def _csrf(self):
        response = self.client.get("/api/auth/csrf/")
        self.assertEqual(response.status_code, 200)
        return response.json()["csrfToken"]

    def test_customer_can_register_and_get_current_user(self):
        csrf = self._csrf()

        response = self.client.post(
            "/api/auth/register/",
            {
                "email": "customer@example.com",
                "password": "A-strong-test-password-123!",
                "first_name": "Test",
                "last_name": "Customer",
            },
            format="json",
            HTTP_X_CSRFTOKEN=csrf,
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["user"]["email"], "customer@example.com")

        response = self.client.get("/api/auth/me/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["user"]["email"], "customer@example.com")
